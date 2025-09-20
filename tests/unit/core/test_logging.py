"""Unit tests for ALGOViz structured logging system."""

import json
from unittest.mock import Mock

import pytest

from agloviz.core.errors import AGLOVizError, ConfigError, ErrorSeverity, FileContext
from agloviz.core.logging import (
    AGLOVizLogger,
    ErrorCollector,
    configure_logging,
    get_logger,
    log_error,
    log_info,
    log_success,
    log_warning,
)


@pytest.mark.unit
class TestAGLOVizLogger:
    """Test the structured logger implementation."""

    def test_logger_initialization(self):
        """Test logger initialization with default settings."""
        logger = AGLOVizLogger()

        assert logger.name == "agloviz"
        assert logger.console is not None
        assert logger.debug_mode is False
        assert logger.logger.level == 20  # INFO level

    def test_logger_with_custom_settings(self):
        """Test logger initialization with custom settings."""
        logger = AGLOVizLogger(
            name="test_logger",
            level="DEBUG",
            enable_rich=False,
        )

        assert logger.name == "test_logger"
        assert logger.console is None  # Rich disabled
        assert logger.logger.level == 10  # DEBUG level

    def test_debug_mode_toggle(self):
        """Test enabling and disabling debug mode."""
        logger = AGLOVizLogger()

        # Initially disabled
        assert logger.debug_mode is False

        # Enable debug mode
        logger.enable_debug_mode(True)
        assert logger.debug_mode is True
        assert logger.logger.level == 10  # DEBUG level

        # Disable debug mode
        logger.enable_debug_mode(False)
        assert logger.debug_mode is False
        assert logger.logger.level == 20  # INFO level

    def test_log_error_basic(self):
        """Test basic error logging."""
        logger = AGLOVizLogger(enable_rich=False)  # Disable rich for testing
        error = AGLOVizError(issue="Test error")

        # Should not raise an exception
        logger.log_error(error, show_rich=False)

    def test_log_error_with_context(self):
        """Test error logging with additional context."""
        logger = AGLOVizLogger(enable_rich=False)
        context = FileContext("test.yaml", line_number=5)
        error = ConfigError(
            issue="Invalid value",
            context=context,
            config_key="test_key",
        )

        additional_context = {"user_action": "validation", "timestamp": "2024-01-01"}

        # Should not raise an exception
        logger.log_error(error, additional_context=additional_context, show_rich=False)

    def test_log_warning(self):
        """Test warning logging."""
        logger = AGLOVizLogger(enable_rich=False)

        # Should not raise an exception
        logger.log_warning(
            message="Test warning",
            category="Test",
            context="test context",
            suggestions=["suggestion1", "suggestion2"],
        )

    def test_log_info_and_success(self):
        """Test info and success logging."""
        logger = AGLOVizLogger(enable_rich=False)

        # Should not raise exceptions
        logger.log_info("Test info message", extra_data="test")
        logger.log_success("Test success message", result="success")

    def test_log_debug(self):
        """Test debug logging."""
        logger = AGLOVizLogger(enable_rich=False)

        # Debug message when debug mode disabled
        logger.log_debug("Debug message 1")

        # Enable debug mode and try again
        logger.enable_debug_mode(True)
        logger.log_debug("Debug message 2")

    def test_aggregate_errors_single(self):
        """Test aggregating a single error."""
        logger = AGLOVizLogger(enable_rich=False)
        error = AGLOVizError(issue="Single error")

        # Should handle single error gracefully
        logger.aggregate_errors([error])

    def test_aggregate_errors_multiple(self):
        """Test aggregating multiple errors."""
        logger = AGLOVizLogger(enable_rich=False)
        errors = [
            ConfigError(issue="Config error 1", config_key="key1"),
            ConfigError(issue="Config error 2", config_key="key2"),
            AGLOVizError(issue="Generic error", severity=ErrorSeverity.WARNING),
        ]

        # Should handle multiple errors gracefully
        logger.aggregate_errors(errors)

    def test_export_error_log(self, tmp_path):
        """Test exporting errors to JSON file."""
        logger = AGLOVizLogger(enable_rich=False)
        errors = [
            ConfigError(issue="Test error 1", config_key="key1"),
            AGLOVizError(issue="Test error 2", severity=ErrorSeverity.WARNING),
        ]

        output_file = tmp_path / "error_log.json"
        logger.export_error_log(str(output_file), errors)

        # Verify file was created
        assert output_file.exists()

        # Verify JSON content
        with open(output_file) as f:
            data = json.load(f)

        assert data["total_errors"] == 2
        assert len(data["errors"]) == 2
        assert "timestamp" in data
        assert "summary" in data

        # Check summary statistics
        summary = data["summary"]
        assert summary["total_errors"] == 2
        assert "ConfigError" in summary["by_category"]
        assert summary["by_category"]["ConfigError"] == 1


@pytest.mark.unit
class TestErrorCollector:
    """Test the error collection system."""

    def test_error_collector_initialization(self):
        """Test error collector initialization."""
        collector = ErrorCollector(max_errors=5)

        assert collector.max_errors == 5
        assert len(collector.errors) == 0
        assert not collector.has_errors()
        assert collector.get_error_count() == 0

    def test_add_error(self):
        """Test adding errors to the collector."""
        collector = ErrorCollector()
        error = AGLOVizError(issue="Test error")

        collector.add_error(error)

        assert collector.has_errors()
        assert collector.get_error_count() == 1
        assert collector.errors[0] == error

    def test_add_config_error_convenience(self):
        """Test the convenience method for adding config errors."""
        collector = ErrorCollector()

        collector.add_config_error(
            issue="Invalid value",
            config_key="test_key",
            file_path="test.yaml",
            line_number=10,
        )

        assert collector.has_errors()
        error = collector.errors[0]
        assert isinstance(error, ConfigError)
        assert error.issue == "Invalid value"
        assert error.metadata["config_key"] == "test_key"

    def test_has_critical_errors(self):
        """Test checking for critical errors."""
        collector = ErrorCollector()

        # Add regular error
        collector.add_error(AGLOVizError(issue="Regular error"))
        assert not collector.has_critical_errors()

        # Add critical error
        collector.add_error(AGLOVizError(
            issue="Critical error",
            severity=ErrorSeverity.CRITICAL
        ))
        assert collector.has_critical_errors()

    def test_get_errors_by_category(self):
        """Test filtering errors by category."""
        collector = ErrorCollector()

        collector.add_error(ConfigError(issue="Config error 1", config_key="key1"))
        collector.add_error(AGLOVizError(issue="Generic error"))
        collector.add_error(ConfigError(issue="Config error 2", config_key="key2"))

        config_errors = collector.get_errors_by_category("ConfigError")
        assert len(config_errors) == 2
        assert all(isinstance(e, ConfigError) for e in config_errors)

        generic_errors = collector.get_errors_by_category("AGLOVizError")
        assert len(generic_errors) == 1

    def test_flush_errors(self):
        """Test flushing collected errors."""
        collector = ErrorCollector()

        # Add some errors
        collector.add_error(AGLOVizError(issue="Error 1"))
        collector.add_error(AGLOVizError(issue="Error 2"))

        assert collector.get_error_count() == 2

        # Flush errors
        flushed_errors = collector.flush()

        assert len(flushed_errors) == 2
        assert collector.get_error_count() == 0  # Should be cleared
        assert not collector.has_errors()

    def test_clear_errors(self):
        """Test clearing errors without logging."""
        collector = ErrorCollector()

        collector.add_error(AGLOVizError(issue="Error 1"))
        collector.add_error(AGLOVizError(issue="Error 2"))

        assert collector.has_errors()

        collector.clear()

        assert not collector.has_errors()
        assert collector.get_error_count() == 0

    def test_max_errors_auto_flush(self):
        """Test automatic flushing when max errors reached."""
        collector = ErrorCollector(max_errors=2)

        # Add first error
        collector.add_error(AGLOVizError(issue="Error 1"))
        assert collector.get_error_count() == 1

        # Add second error - should trigger flush and reset
        collector.add_error(AGLOVizError(issue="Error 2"))
        assert collector.get_error_count() == 0  # Should be flushed

        # Add third error - should start fresh collection
        collector.add_error(AGLOVizError(issue="Error 3"))
        assert collector.get_error_count() == 1

    def test_export_to_file(self, tmp_path):
        """Test exporting collected errors to file."""
        collector = ErrorCollector()

        collector.add_error(ConfigError(issue="Config error", config_key="test"))
        collector.add_error(AGLOVizError(issue="Generic error"))

        output_file = tmp_path / "collector_export.json"
        collector.export_to_file(str(output_file))

        # File should be created
        assert output_file.exists()


@pytest.mark.unit
class TestGlobalLoggingFunctions:
    """Test global logging convenience functions."""

    def test_get_logger_singleton(self):
        """Test that get_logger returns the same instance."""
        logger1 = get_logger()
        logger2 = get_logger()

        assert logger1 is logger2  # Should be the same instance

    def test_configure_logging(self):
        """Test logging configuration."""
        logger = configure_logging(
            level="DEBUG",
            debug_mode=True,
            enable_file_logging=False,
        )

        assert isinstance(logger, AGLOVizLogger)
        assert logger.debug_mode is True
        assert logger.logger.level == 10  # DEBUG level

    def test_convenience_logging_functions(self):
        """Test convenience logging functions."""
        # These should not raise exceptions
        log_info("Test info message")
        log_success("Test success message")
        log_warning("Test warning message")

        # Test with error
        error = AGLOVizError(issue="Test error")
        log_error(error)

    def test_debug_mode_functions(self):
        """Test debug mode convenience functions."""
        from agloviz.core.logging import disable_debug, enable_debug

        # Should not raise exceptions
        enable_debug()
        disable_debug()


@pytest.mark.unit
class TestLoggingIntegration:
    """Test integration between logging and error systems."""

    def test_structured_error_logging(self):
        """Test that errors are logged with proper structure."""
        logger = AGLOVizLogger(enable_rich=False)

        context = FileContext("test.yaml", line_number=5)
        error = ConfigError(
            issue="Test configuration error",
            context=context,
            config_key="test_key",
            suggestions=["suggestion1", "suggestion2"],
        )

        # Mock the logger to capture the logged data
        mock_logger = Mock()
        logger.logger = mock_logger

        logger.log_error(error, additional_context={"test": "data"}, show_rich=False)

        # Verify the logger was called with structured data
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args

        assert "ALGOViz Error:" in call_args[0][0]
        assert "structured_data" in call_args[1]["extra"]

    def test_error_summary_generation(self):
        """Test error summary statistics generation."""
        logger = AGLOVizLogger(enable_rich=False)

        errors = [
            ConfigError(issue="Config error 1", config_key="key1"),
            ConfigError(issue="Config error 2", config_key="key2"),
            AGLOVizError(issue="Generic error", severity=ErrorSeverity.WARNING),
            AGLOVizError(issue="Critical error", severity=ErrorSeverity.CRITICAL),
        ]

        summary = logger._generate_error_summary(errors)

        assert summary["total_errors"] == 4
        assert summary["by_category"]["ConfigError"] == 2
        assert summary["by_category"]["AGLOVizError"] == 2
        assert summary["by_severity"]["error"] == 2  # 2 ConfigErrors (no AGLOVizError with ERROR severity)
        assert summary["by_severity"]["warning"] == 1
        assert summary["by_severity"]["critical"] == 1
        assert summary["has_critical"] is True

    def test_file_logging_integration(self, tmp_path):
        """Test file logging functionality."""
        log_file = tmp_path / "test.log"

        logger = AGLOVizLogger(
            enable_rich=False,
            enable_file_logging=True,
            log_file_path=str(log_file),
        )

        # Log some messages
        logger.log_info("Test info message")
        error = AGLOVizError(issue="Test error")
        logger.log_error(error, show_rich=False)

        # Force flush handlers
        for handler in logger.logger.handlers:
            handler.flush()

        # Verify log file was created and has content
        assert log_file.exists()

        with open(log_file) as f:
            content = f.read()

        assert "Test info message" in content
        assert "Test error" in content


@pytest.mark.unit
class TestErrorCollectorAdvanced:
    """Test advanced error collector functionality."""

    def test_collector_with_mixed_error_types(self):
        """Test collector with different error types."""
        collector = ErrorCollector()

        # Add different types of errors
        collector.add_error(ConfigError(issue="Config issue", config_key="key1"))
        collector.add_error(AGLOVizError(issue="Generic issue"))

        # Test category filtering
        config_errors = collector.get_errors_by_category("ConfigError")
        generic_errors = collector.get_errors_by_category("AGLOVizError")

        assert len(config_errors) == 1
        assert len(generic_errors) == 1
        assert isinstance(config_errors[0], ConfigError)
        assert isinstance(generic_errors[0], AGLOVizError)

    def test_collector_export_integration(self, tmp_path):
        """Test collector export with real file I/O."""
        collector = ErrorCollector()

        # Add errors with rich metadata
        collector.add_config_error(
            issue="Missing required field",
            config_key="scenario.start",
            file_path="scenario.yaml",
            line_number=10,
            valid_options=["start", "goal"],
        )

        collector.add_error(AGLOVizError(
            issue="Generic error",
            severity=ErrorSeverity.WARNING,
            suggestions=["try this", "or this"],
            metadata={"custom": "data"},
        ))

        # Export to file
        output_file = tmp_path / "collector_test.json"
        collector.export_to_file(str(output_file))

        # Verify export
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert data["total_errors"] == 2
        assert len(data["errors"]) == 2

        # Verify error structure
        config_error = next(e for e in data["errors"] if e["category"] == "ConfigError")
        assert config_error["metadata"]["config_key"] == "scenario.start"
        assert config_error["context"]["metadata"]["file_path"] == "scenario.yaml"
        assert config_error["context"]["metadata"]["line_number"] == 10


@pytest.mark.unit
class TestLoggingConfiguration:
    """Test logging system configuration and global state."""

    def test_global_logger_configuration(self):
        """Test global logger configuration."""
        # Configure with specific settings
        logger = configure_logging(
            level="WARNING",
            debug_mode=False,
            enable_file_logging=False,
        )

        assert isinstance(logger, AGLOVizLogger)
        assert logger.logger.level == 30  # WARNING level
        assert logger.debug_mode is False

        # Verify global logger is updated
        global_logger = get_logger()
        assert global_logger is logger

    def test_convenience_function_integration(self):
        """Test that convenience functions use the global logger."""
        # Configure logger
        configure_logging(level="DEBUG", debug_mode=True)

        # Use convenience functions - should not raise exceptions
        log_info("Integration test info")
        log_success("Integration test success")
        log_warning("Integration test warning", category="Test")

        # Test error logging
        error = ConfigError(issue="Integration test error", config_key="test")
        log_error(error)

    def test_logger_state_persistence(self):
        """Test that logger state persists across calls."""
        # Configure debug mode
        logger = configure_logging(debug_mode=True)
        assert logger.debug_mode is True

        # Get logger again - should maintain state
        same_logger = get_logger()
        assert same_logger is logger
        assert same_logger.debug_mode is True


@pytest.mark.unit
class TestRealWorldErrorScenarios:
    """Test realistic error scenarios that would occur in ALGOViz."""

    def test_config_file_typo_scenario(self):
        """Test realistic config file typo scenario."""
        # User types "tming" instead of "timing"
        context = FileContext("my_config.yaml", line_number=5)
        error = ConfigError(
            issue="Unknown config key 'tming'",
            context=context,
            config_key="tming",
            valid_options=["timing", "render", "scenario", "theme"],
        )

        # Should provide helpful suggestions
        assert "timing" in error.suggestions
        assert "my_config.yaml:5" in error.format_message()
        assert error.metadata["config_key"] == "tming"

    def test_multiple_config_errors_scenario(self):
        """Test scenario with multiple configuration errors."""
        collector = ErrorCollector()

        # Simulate multiple config validation errors
        collector.add_config_error(
            issue="Missing required field 'start'",
            config_key="scenario.start",
            file_path="scenario.yaml",
            line_number=8,
        )

        collector.add_config_error(
            issue="Invalid enum value 'ultra' for quality",
            config_key="render.quality",
            file_path="render.yaml",
            line_number=3,
            valid_options=["draft", "medium", "high"],
        )

        collector.add_config_error(
            issue="Type mismatch: expected int, got str",
            config_key="render.frame_rate",
            file_path="render.yaml",
            line_number=5,
            expected_type="int",
            actual_type="str",
        )

        # Verify all errors collected
        assert collector.get_error_count() == 3

        # Verify different error types
        config_errors = collector.get_errors_by_category("ConfigError")
        assert len(config_errors) == 3

        # Verify errors have appropriate metadata
        for error in config_errors:
            assert error.metadata.get("config_key")
            assert error.issue

    def test_suggestion_quality_scenario(self):
        """Test suggestion quality for realistic typos."""
        from agloviz.core.errors import SuggestionEngine

        engine = SuggestionEngine()

        # Test common typos in ALGOViz context
        test_cases = [
            ("tming", ["timing"], "timing"),  # Missing letter
            ("scenaro", ["scenario"], "scenario"),  # Typo
            ("qualiy", ["quality"], "quality"),  # Missing letter
            ("fase", ["fast"], "fast"),  # Similar word
            ("redner", ["render"], "render"),  # Letter swap
        ]

        for typo, valid_options, expected in test_cases:
            suggestions = engine.suggest_corrections(typo, valid_options)
            assert expected in suggestions, f"Expected '{expected}' in suggestions for '{typo}'"
