"""Unit tests for CLI error display system."""

from unittest.mock import Mock

import pytest
import typer
from rich.console import Console

from agloviz.cli.error_display import (
    CLIErrorDisplay,
    CLIErrorHandler,
    ExitCodes,
    create_cli_error_handler,
    display_error_summary,
    handle_cli_exception,
)
from agloviz.core.errors import (
    AGLOVizError,
    ConfigError,
    ErrorSeverity,
    FileContext,
    StoryboardError,
)


@pytest.mark.unit
class TestCLIErrorDisplay:
    """Test CLI error display functionality."""

    def test_display_initialization(self):
        """Test CLI error display initialization."""
        display = CLIErrorDisplay()

        assert display.console is not None
        assert display.logger is not None

    def test_display_error_basic(self):
        """Test basic error display."""
        # Use null console to suppress output during testing
        console = Console(file=open('/dev/null', 'w'))
        display = CLIErrorDisplay(console=console)

        error = AGLOVizError(
            issue="Test error",
            remedy="Test remedy",
            suggestions=["suggestion1", "suggestion2"],
        )

        # Should not raise an exception
        display.display_error(error, show_context=False, show_debug=False)
        console.file.close()

    def test_display_error_with_file_context(self, tmp_path):
        """Test error display with file context."""
        # Create a test file
        test_file = tmp_path / "test.yaml"
        test_content = """line 1
line 2
line 3 with error
line 4
line 5"""
        test_file.write_text(test_content)

        console = Console(file=open('/dev/null', 'w'))
        display = CLIErrorDisplay(console=console)

        context = FileContext(str(test_file), line_number=3)
        error = ConfigError(
            issue="Syntax error",
            context=context,
        )

        # Should display file excerpt
        display.display_error(error, show_context=True)
        console.file.close()

    def test_display_file_excerpt(self, tmp_path):
        """Test file excerpt display functionality."""
        # Create test file with multiple lines
        test_file = tmp_path / "config.yaml"
        lines = [f"line {i}\n" for i in range(1, 21)]  # 20 lines
        test_file.write_text(''.join(lines))

        console = Console(file=open('/dev/null', 'w'))
        display = CLIErrorDisplay(console=console)

        # Test with specific line number
        display.display_file_excerpt(str(test_file), line_number=10, context_lines=2)

        # Test without line number
        display.display_file_excerpt(str(test_file))

        console.file.close()

    def test_display_file_excerpt_nonexistent_file(self):
        """Test file excerpt display with nonexistent file."""
        console = Console(file=open('/dev/null', 'w'))
        display = CLIErrorDisplay(console=console)

        # Should handle nonexistent file gracefully
        display.display_file_excerpt("nonexistent.yaml", line_number=5)
        console.file.close()

    def test_display_suggestions(self):
        """Test suggestion display."""
        console = Console(file=open('/dev/null', 'w'))
        display = CLIErrorDisplay(console=console)

        suggestions = ["option1", "option2", "option3"]

        # Should not raise an exception
        display.display_suggestions(suggestions, "Test Suggestions", "original_input")
        console.file.close()

    def test_get_exit_code(self):
        """Test exit code determination."""
        display = CLIErrorDisplay()

        # Test different error categories
        config_error = ConfigError(issue="Config error")
        assert display.get_exit_code(config_error) == ExitCodes.CONFIG_ERROR

        # Test different severities
        warning_error = AGLOVizError(issue="Warning", severity=ErrorSeverity.WARNING)
        assert display.get_exit_code(warning_error) == ExitCodes.SUCCESS  # Warnings don't exit

        critical_error = AGLOVizError(issue="Critical", severity=ErrorSeverity.CRITICAL)
        assert display.get_exit_code(critical_error) > 0  # Critical errors exit

    def test_language_detection(self):
        """Test file language detection for syntax highlighting."""
        display = CLIErrorDisplay()

        assert display._get_language_for_extension("py") == "python"
        assert display._get_language_for_extension("yaml") == "yaml"
        assert display._get_language_for_extension("yml") == "yaml"
        assert display._get_language_for_extension("json") == "json"
        assert display._get_language_for_extension("unknown") == "text"


@pytest.mark.unit
class TestCLIErrorHandler:
    """Test CLI error handler functionality."""

    def test_handler_initialization(self):
        """Test CLI error handler initialization."""
        handler = CLIErrorHandler(debug_mode=True)

        assert handler.debug_mode is True
        assert handler.display is not None
        assert handler.logger is not None

    def test_handle_config_error_with_agloviz_error(self):
        """Test handling ALGOViz config errors."""
        handler = CLIErrorHandler(debug_mode=False)

        # Mock the display to avoid actual exit
        handler.display.handle_error_and_exit = Mock()

        error = ConfigError(issue="Test config error")
        handler.handle_config_error(error, "config.yaml")

        # Should call the display handler
        handler.display.handle_error_and_exit.assert_called_once_with(
            error, show_debug=False
        )

    def test_handle_config_error_with_generic_exception(self):
        """Test handling generic exceptions as config errors."""
        handler = CLIErrorHandler(debug_mode=False)

        # Mock the display to avoid actual exit
        handler.display.handle_error_and_exit = Mock()

        generic_error = ValueError("Generic error")
        handler.handle_config_error(generic_error, "config.yaml")

        # Should convert to ConfigError and call display
        handler.display.handle_error_and_exit.assert_called_once()
        call_args = handler.display.handle_error_and_exit.call_args[0]
        converted_error = call_args[0]

        assert isinstance(converted_error, ConfigError)
        assert "Configuration error: Generic error" in converted_error.issue

    def test_handle_file_not_found(self):
        """Test file not found error handling."""
        handler = CLIErrorHandler()

        # Mock the display to avoid actual exit
        handler.display.handle_error_and_exit = Mock()

        handler.handle_file_not_found("missing.yaml", "configuration file")

        # Should create appropriate ConfigError
        handler.display.handle_error_and_exit.assert_called_once()
        call_args = handler.display.handle_error_and_exit.call_args[0]
        error = call_args[0]

        assert isinstance(error, ConfigError)
        assert "Configuration file not found: missing.yaml" in error.issue

    def test_handle_file_not_found_with_suggestions(self, tmp_path):
        """Test file not found with similar file suggestions."""
        # Create some similar files
        (tmp_path / "config.yaml").touch()
        (tmp_path / "configuration.yml").touch()
        (tmp_path / "other.txt").touch()

        handler = CLIErrorHandler()
        handler.display.handle_error_and_exit = Mock()

        missing_file = tmp_path / "config.yml"  # Similar to existing files
        handler.handle_file_not_found(str(missing_file), "config file")

        # Should include suggestions
        call_args = handler.display.handle_error_and_exit.call_args[0]
        error = call_args[0]

        # Should have suggestions for similar files
        assert len(error.suggestions) > 0

    def test_handle_validation_error_pydantic(self):
        """Test handling Pydantic validation errors."""
        from pydantic import BaseModel, ValidationError

        class TestModel(BaseModel):
            name: str
            count: int

        handler = CLIErrorHandler()
        handler.display.handle_error_and_exit = Mock()

        # Create a validation error
        try:
            TestModel(name="", count="not_an_int")
        except ValidationError as e:
            handler.handle_validation_error(e, "test.yaml")

        # Should convert to ConfigError
        handler.display.handle_error_and_exit.assert_called_once()
        call_args = handler.display.handle_error_and_exit.call_args[0]
        error = call_args[0]

        assert isinstance(error, ConfigError)
        assert "Configuration validation failed" in error.issue

    def test_handle_unexpected_error(self):
        """Test handling unexpected errors."""
        handler = CLIErrorHandler()
        handler.display.handle_error_and_exit = Mock()

        unexpected_error = RuntimeError("Unexpected runtime error")
        handler.handle_unexpected_error(unexpected_error, "test operation", "test context")

        # Should create critical AGLOVizError
        handler.display.handle_error_and_exit.assert_called_once()
        call_args = handler.display.handle_error_and_exit.call_args[0]
        error = call_args[0]

        assert isinstance(error, AGLOVizError)
        assert error.severity == ErrorSeverity.CRITICAL
        assert "Unexpected error during test operation" in error.issue
        assert "RuntimeError" in error.metadata["error_type"]


@pytest.mark.unit
class TestExitCodes:
    """Test exit code constants and consistency."""

    def test_exit_code_constants(self):
        """Test that all exit codes are defined."""
        assert ExitCodes.SUCCESS == 0
        assert ExitCodes.CONFIG_ERROR == 1
        assert ExitCodes.STORYBOARD_ERROR == 2
        assert ExitCodes.ADAPTER_ERROR == 3
        assert ExitCodes.SCENARIO_ERROR == 4
        assert ExitCodes.REGISTRY_ERROR == 5
        assert ExitCodes.RENDER_ERROR == 6
        assert ExitCodes.VOICEOVER_ERROR == 7
        assert ExitCodes.PLUGIN_ERROR == 8
        assert ExitCodes.UNEXPECTED_ERROR == 9
        assert ExitCodes.CRITICAL_ERROR == 10

    def test_exit_code_uniqueness(self):
        """Test that all exit codes are unique."""
        codes = [
            ExitCodes.SUCCESS,
            ExitCodes.CONFIG_ERROR,
            ExitCodes.STORYBOARD_ERROR,
            ExitCodes.ADAPTER_ERROR,
            ExitCodes.SCENARIO_ERROR,
            ExitCodes.REGISTRY_ERROR,
            ExitCodes.RENDER_ERROR,
            ExitCodes.VOICEOVER_ERROR,
            ExitCodes.PLUGIN_ERROR,
            ExitCodes.UNEXPECTED_ERROR,
            ExitCodes.CRITICAL_ERROR,
        ]

        assert len(codes) == len(set(codes))  # All unique


@pytest.mark.unit
class TestErrorSummaryDisplay:
    """Test error summary display functionality."""

    def test_display_error_summary_empty(self):
        """Test error summary with no errors."""
        console = Console(file=open('/dev/null', 'w'))

        # Should handle empty list gracefully
        display_error_summary([], console)
        console.file.close()

    def test_display_error_summary_single(self):
        """Test error summary with single error."""
        console = Console(file=open('/dev/null', 'w'))
        error = ConfigError(issue="Single error", config_key="test")

        display_error_summary([error], console)
        console.file.close()

    def test_display_error_summary_multiple(self):
        """Test error summary with multiple errors."""
        console = Console(file=open('/dev/null', 'w'))
        errors = [
            ConfigError(issue="Config error 1", config_key="key1"),
            ConfigError(issue="Config error 2", config_key="key2"),
            AGLOVizError(issue="Generic error", severity=ErrorSeverity.WARNING),
            StoryboardError(
                issue="Storyboard error",
                act="intro",
                shot="setup",
                beat="title",
                suggestions=["show_title"],
            ),
        ]

        display_error_summary(errors, console)
        console.file.close()

    def test_display_error_summary_with_common_suggestions(self):
        """Test error summary with repeated suggestions."""
        console = Console(file=open('/dev/null', 'w'))
        errors = [
            ConfigError(
                issue="Error 1",
                config_key="key1",
                suggestions=["timing", "render"]
            ),
            ConfigError(
                issue="Error 2",
                config_key="key2",
                suggestions=["timing", "scenario"]
            ),
            ConfigError(
                issue="Error 3",
                config_key="key3",
                suggestions=["timing", "theme"]
            ),
        ]

        # Should show "timing" as most common suggestion
        display_error_summary(errors, console)
        console.file.close()


@pytest.mark.unit
class TestGlobalErrorHandling:
    """Test global error handling functions."""

    def test_create_cli_error_handler(self):
        """Test CLI error handler factory."""
        handler = create_cli_error_handler(debug_mode=True)

        assert isinstance(handler, CLIErrorHandler)
        assert handler.debug_mode is True

    def test_handle_cli_exception_with_agloviz_error(self):
        """Test global exception handler with ALGOViz error."""
        # Mock to avoid actual exit
        original_handler = CLIErrorHandler.handle_config_error
        CLIErrorHandler.handle_config_error = Mock()

        try:
            error = ConfigError(issue="Test error")
            # This would normally exit, but we're mocking
            with pytest.raises((SystemExit, typer.Exit)):  # Mock will raise Exit
                handle_cli_exception(error, "test operation")
        finally:
            CLIErrorHandler.handle_config_error = original_handler

    def test_handle_cli_exception_with_file_not_found(self):
        """Test global exception handler with FileNotFoundError."""
        # Mock to avoid actual exit
        original_handler = CLIErrorHandler.handle_file_not_found
        CLIErrorHandler.handle_file_not_found = Mock()

        try:
            error = FileNotFoundError("File 'missing.yaml' not found")
            handle_cli_exception(error, "file operation")

            # Should call file not found handler
            CLIErrorHandler.handle_file_not_found.assert_called()
        finally:
            CLIErrorHandler.handle_file_not_found = original_handler

    def test_handle_cli_exception_with_validation_error(self):
        """Test global exception handler with validation error."""
        from pydantic import BaseModel, ValidationError

        class TestModel(BaseModel):
            name: str

        # Mock to avoid actual exit
        original_handler = CLIErrorHandler.handle_validation_error
        CLIErrorHandler.handle_validation_error = Mock()

        try:
            # Create validation error
            try:
                TestModel(name=123)  # Invalid type
            except ValidationError as e:
                handle_cli_exception(e, "validation", "test.yaml")

            # Should call validation error handler
            CLIErrorHandler.handle_validation_error.assert_called()
        finally:
            CLIErrorHandler.handle_validation_error = original_handler

    def test_handle_cli_exception_with_unexpected_error(self):
        """Test global exception handler with unexpected error."""
        # Mock to avoid actual exit
        original_handler = CLIErrorHandler.handle_unexpected_error
        CLIErrorHandler.handle_unexpected_error = Mock()

        try:
            error = RuntimeError("Unexpected runtime error")
            handle_cli_exception(error, "unexpected operation")

            # Should call unexpected error handler
            CLIErrorHandler.handle_unexpected_error.assert_called()
        finally:
            CLIErrorHandler.handle_unexpected_error = original_handler


@pytest.mark.unit
class TestErrorDisplayIntegration:
    """Test integration between error display and error taxonomy."""

    def test_config_error_display_integration(self):
        """Test config error display with full features."""
        console = Console(file=open('/dev/null', 'w'))
        display = CLIErrorDisplay(console=console)

        context = FileContext("config.yaml", line_number=15)
        error = ConfigError(
            issue="Invalid timing mode 'fase'",
            context=context,
            config_key="timing.mode",
            valid_options=["draft", "normal", "fast"],
            suggestions=["fast"],  # Should suggest "fast" for "fase"
        )

        # Should display all components
        display.display_error(error, show_context=True, show_suggestions=True)
        console.file.close()

    def test_storyboard_error_display_integration(self):
        """Test storyboard error display with context."""
        console = Console(file=open('/dev/null', 'w'))
        display = CLIErrorDisplay(console=console)

        error = StoryboardError(
            issue="Unknown action 'show_titel'",
            act="intro",
            shot="setup",
            beat="title",
            action="show_titel",
            suggestions=["show_title"],
        )

        # Should display storyboard context
        display.display_error(error)
        console.file.close()

    def test_error_with_rich_metadata_display(self):
        """Test error display with rich metadata."""
        console = Console(file=open('/dev/null', 'w'))
        display = CLIErrorDisplay(console=console)

        error = AGLOVizError(
            issue="Complex error with metadata",
            remedy="Try this specific remedy",
            suggestions=["suggestion1", "suggestion2", "suggestion3"],
            severity=ErrorSeverity.CRITICAL,
            metadata={
                "user_input": "invalid_value",
                "valid_options": ["option1", "option2"],
                "timestamp": "2024-01-01T00:00:00",
            }
        )

        # Should display all components including debug info
        display.display_error(error, show_debug=True)
        console.file.close()


@pytest.mark.unit
class TestRealWorldCLIScenarios:
    """Test realistic CLI error scenarios."""

    def test_config_validation_cli_scenario(self, tmp_path):
        """Test realistic config validation CLI scenario."""
        # Create invalid config file
        config_file = tmp_path / "invalid.yaml"
        config_content = """scenario:
  name: test
  start: [0, 0]
  goal: [0, 0]  # Same as start - invalid
timing:
  mode: fase  # Typo - should be "fast"
render:
  quality: ultra  # Invalid - should be draft/medium/high
"""
        config_file.write_text(config_content)

        console = Console(file=open('/dev/null', 'w'))
        handler = CLIErrorHandler(debug_mode=True)
        handler.display = CLIErrorDisplay(console=console)

        # Mock exit to capture the error
        handler.display.handle_error_and_exit = Mock()

        # Simulate validation error

        # This would be the actual validation error from our system
        error = ConfigError(
            issue="Multiple validation errors found",
            context=FileContext(str(config_file)),
            suggestions=["Check enum values", "Verify position constraints"],
        )

        handler.handle_config_error(error, str(config_file))

        # Should handle the error appropriately
        handler.display.handle_error_and_exit.assert_called_once()
        console.file.close()

    def test_typo_suggestion_cli_scenario(self):
        """Test CLI scenario with typo suggestions."""
        console = Console(file=open('/dev/null', 'w'))
        display = CLIErrorDisplay(console=console)

        # User types "agloviz redner" instead of "agloviz render"
        error = ConfigError(
            issue="Unknown command 'redner'",
            suggestions=["render", "preview"],
            remedy="Check command spelling",
        )

        display.display_error(error)
        console.file.close()

    def test_multiple_error_aggregation_scenario(self):
        """Test CLI scenario with multiple aggregated errors."""
        console = Console(file=open('/dev/null', 'w'))

        errors = [
            ConfigError(
                issue="Missing field 'start'",
                context=FileContext("scenario.yaml", line_number=5),
                config_key="start",
            ),
            ConfigError(
                issue="Invalid enum 'ultra'",
                context=FileContext("render.yaml", line_number=3),
                config_key="quality",
                valid_options=["draft", "medium", "high"],
            ),
            ConfigError(
                issue="Type mismatch for 'frame_rate'",
                context=FileContext("render.yaml", line_number=7),
                config_key="frame_rate",
                expected_type="int",
                actual_type="str",
            ),
        ]

        # Should display aggregated summary
        display_error_summary(errors, console)
        console.file.close()
