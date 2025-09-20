"""Unit tests for ALGOViz error taxonomy system."""

import pytest
from rich.console import Console

from agloviz.core.errors import (
    AdapterError,
    AGLOVizError,
    AlgorithmContext,
    ConfigError,
    ErrorCategory,
    ErrorSeverity,
    FileContext,
    PluginError,
    RegistryError,
    RenderError,
    ScenarioError,
    StoryboardContext,
    StoryboardError,
    SuggestionEngine,
    VoiceoverError,
    create_invalid_enum_error,
    create_missing_field_error,
    create_type_mismatch_error,
    create_unknown_key_error,
)


@pytest.mark.unit
class TestErrorContext:
    """Test error context providers."""

    def test_file_context_basic(self):
        """Test basic file context formatting."""
        context = FileContext("config.yaml")

        assert context.format_location() == "config.yaml"
        assert context.get_metadata()["file_path"] == "config.yaml"
        assert context.get_metadata()["line_number"] is None

    def test_file_context_with_line(self):
        """Test file context with line number."""
        context = FileContext("config.yaml", line_number=15)

        assert context.format_location() == "config.yaml:15"
        assert context.get_metadata()["line_number"] == 15

    def test_file_context_with_line_and_column(self):
        """Test file context with line and column."""
        context = FileContext("config.yaml", line_number=15, column=8)

        assert context.format_location() == "config.yaml:15:8"
        assert context.get_metadata()["column"] == 8

    def test_storyboard_context(self):
        """Test storyboard context formatting."""
        context = StoryboardContext(act="intro", shot="setup", beat="show_title")

        assert context.format_location() == "Act intro/Shot setup/Beat show_title"
        metadata = context.get_metadata()
        assert metadata["act"] == "intro"
        assert metadata["shot"] == "setup"
        assert metadata["beat"] == "show_title"

    def test_algorithm_context(self):
        """Test algorithm context formatting."""
        state = {"current_node": "(2,3)", "queue_size": 5}
        context = AlgorithmContext("bfs", step_index=42, current_state=state)

        assert context.format_location() == "bfs[step 42]"
        metadata = context.get_metadata()
        assert metadata["algorithm"] == "bfs"
        assert metadata["step_index"] == 42
        assert metadata["current_state"] == state


@pytest.mark.unit
class TestSuggestionEngine:
    """Test the suggestion algorithm system."""

    def test_exact_case_insensitive_match(self):
        """Test exact case-insensitive matching."""
        engine = SuggestionEngine()
        suggestions = engine.suggest_corrections(
            "TIMING", ["timing", "render", "scenario"]
        )

        assert "timing" in suggestions

    def test_levenshtein_suggestions(self):
        """Test Levenshtein distance-based suggestions."""
        engine = SuggestionEngine()

        # Test typo correction
        suggestions = engine.suggest_corrections(
            "tming", ["timing", "render", "scenario", "theme"]
        )

        assert "timing" in suggestions  # Should suggest timing for "tming"

    def test_fuzzy_matching(self):
        """Test fuzzy substring and prefix matching."""
        engine = SuggestionEngine()

        # Test substring matching - "tim" should match "timing"
        suggestions = engine.suggest_corrections(
            "tim", ["timing", "render", "scenario"]
        )

        assert "timing" in suggestions

    def test_context_aware_suggestions(self):
        """Test context-aware suggestion enhancement."""
        engine = SuggestionEngine()

        # Test timing context
        suggestions = engine.suggest_corrections(
            "ui", ["ui", "events", "effects", "waits", "resolution", "quality"],
            context="timing"
        )

        # Should prioritize timing-related options
        timing_options = ["ui", "events", "effects", "waits"]
        assert any(opt in suggestions for opt in timing_options)

    def test_levenshtein_distance_calculation(self):
        """Test Levenshtein distance algorithm."""
        engine = SuggestionEngine()

        # Test known distances
        assert engine._levenshtein_distance("", "") == 0
        assert engine._levenshtein_distance("abc", "") == 3
        assert engine._levenshtein_distance("", "abc") == 3
        assert engine._levenshtein_distance("abc", "abc") == 0
        assert engine._levenshtein_distance("abc", "ab") == 1
        assert engine._levenshtein_distance("abc", "abcd") == 1
        assert engine._levenshtein_distance("timing", "tming") == 1  # Missing 'i'

    def test_max_suggestions_limit(self):
        """Test that suggestions are limited to max_suggestions."""
        engine = SuggestionEngine(max_suggestions=2)

        suggestions = engine.suggest_corrections(
            "test", ["test1", "test2", "test3", "test4", "test5"]
        )

        assert len(suggestions) <= 2

    def test_similarity_threshold(self):
        """Test minimum similarity threshold filtering."""
        engine = SuggestionEngine(min_similarity=0.8)

        suggestions = engine.suggest_corrections(
            "abc", ["xyz", "def", "abcd"]  # Only "abcd" should be similar enough
        )

        # Should only include very similar options
        assert len(suggestions) <= 1


@pytest.mark.unit
class TestAGLOVizError:
    """Test the base AGLOVizError class."""

    def test_basic_error_creation(self):
        """Test creating a basic ALGOViz error."""
        error = AGLOVizError(
            issue="Something went wrong",
            remedy="Try again",
        )

        assert error.issue == "Something went wrong"
        assert error.remedy == "Try again"
        assert error.category == "AGLOVizError"
        assert error.severity == ErrorSeverity.ERROR
        assert error.suggestions == []

    def test_error_with_context(self):
        """Test error with file context."""
        context = FileContext("test.yaml", line_number=10)
        error = AGLOVizError(
            issue="Invalid syntax",
            context=context,
        )

        assert "test.yaml:10" in error.format_message()
        assert error.context == context

    def test_error_with_suggestions(self):
        """Test error with suggestions."""
        suggestions = ["option1", "option2", "option3"]
        error = AGLOVizError(
            issue="Unknown option",
            suggestions=suggestions,
        )

        assert error.suggestions == suggestions

    def test_error_message_formatting(self):
        """Test error message formatting structure."""
        context = FileContext("config.yaml", line_number=5)
        error = AGLOVizError(
            issue="Invalid value",
            context=context,
            remedy="Use valid value",
        )

        message = error.format_message()
        assert "AGLOVizError" in message
        assert "config.yaml:5" in message
        assert "Invalid value" in message
        assert "Use valid value" in message

    def test_error_to_dict(self):
        """Test error serialization to dictionary."""
        context = FileContext("test.yaml", line_number=3)
        error = AGLOVizError(
            issue="Test error",
            context=context,
            remedy="Test remedy",
            suggestions=["suggestion1", "suggestion2"],
            severity=ErrorSeverity.WARNING,
            metadata={"custom": "data"},
        )

        error_dict = error.to_dict()

        assert error_dict["category"] == "AGLOVizError"
        assert error_dict["issue"] == "Test error"
        assert error_dict["remedy"] == "Test remedy"
        assert error_dict["suggestions"] == ["suggestion1", "suggestion2"]
        assert error_dict["severity"] == "warning"
        assert error_dict["metadata"]["custom"] == "data"
        assert error_dict["context"]["location"] == "test.yaml:3"

    def test_error_to_json(self):
        """Test error serialization to JSON."""
        error = AGLOVizError(issue="Test error")
        json_str = error.to_json()

        assert '"category": "AGLOVizError"' in json_str
        assert '"issue": "Test error"' in json_str

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        assert parsed["category"] == "AGLOVizError"


@pytest.mark.unit
class TestConfigError:
    """Test ConfigError with enhanced functionality."""

    def test_config_error_basic(self):
        """Test basic config error creation."""
        error = ConfigError(
            issue="Invalid configuration",
            config_key="timing.mode",
        )

        assert error.issue == "Invalid configuration"
        assert error.metadata["config_key"] == "timing.mode"

    def test_config_error_with_suggestions(self):
        """Test config error with auto-generated suggestions."""
        error = ConfigError(
            issue="Unknown key",
            config_key="tming",  # Typo
            valid_options=["timing", "render", "scenario"],
        )

        # Should auto-generate suggestions for the typo
        assert len(error.suggestions) > 0
        assert "timing" in error.suggestions

    def test_config_error_remedy_generation(self):
        """Test automatic remedy generation."""
        error = ConfigError(
            issue="Type mismatch",
            config_key="frame_rate",
            expected_type="int",
            actual_type="str",
        )

        assert "Change frame_rate from str to int" in error.remedy

    def test_config_error_with_valid_options(self):
        """Test remedy generation with valid options."""
        error = ConfigError(
            issue="Invalid enum",
            config_key="quality",
            valid_options=["draft", "medium", "high"],
        )

        assert "Use one of: draft, medium, high" in error.remedy


@pytest.mark.unit
class TestSpecificErrorTypes:
    """Test specific error type implementations."""

    def test_storyboard_error(self):
        """Test storyboard error creation."""
        error = StoryboardError(
            issue="Unknown action 'show_titel'",
            act="intro",
            shot="setup",
            beat="title",
            action="show_titel",
            suggestions=["show_title"],
        )

        assert "Act intro/Shot setup/Beat title" in error.format_message()
        assert error.metadata["action"] == "show_titel"
        assert "show_title" in error.suggestions

    def test_adapter_error(self):
        """Test algorithm adapter error creation."""
        state = {"current": "(2,3)", "queue": ["(1,1)", "(3,3)"]}
        error = AdapterError(
            issue="KeyError accessing neighbors",
            algorithm="bfs",
            step_index=15,
            current_state=state,
        )

        assert "bfs[step 15]" in error.format_message()
        assert error.metadata["algorithm"] == "bfs"
        assert error.metadata["step_index"] == 15
        assert "Try with minimal scenario" in error.remedy

    def test_scenario_error(self):
        """Test scenario contract violation error."""
        error = ScenarioError(
            issue="Start position out of bounds",
            contract_violation="bounds_check",
            location="scenario.yaml",
            entity="start",
            position=(10, 5),
        )

        assert error.metadata["contract_violation"] == "bounds_check"
        assert error.metadata["entity"] == "start"
        assert error.metadata["position"] == (10, 5)

    def test_registry_error(self):
        """Test component registry error."""
        error = RegistryError(
            issue="Widget not found",
            component_type="widget",
            component_name="priority_que",  # Typo
            available_options=["queue", "stack", "priority_queue", "hud"],
        )

        assert error.metadata["component_type"] == "widget"
        assert error.metadata["component_name"] == "priority_que"
        # Should auto-generate suggestions
        assert len(error.suggestions) > 0
        assert "priority_queue" in error.suggestions

    def test_render_error(self):
        """Test rendering pipeline error."""
        error = RenderError(
            issue="Missing dependency",
            stage="encoding",
            required_tool="ffmpeg",
            install_command="brew install ffmpeg",
        )

        assert error.metadata["render_stage"] == "encoding"
        assert error.metadata["required_tool"] == "ffmpeg"
        assert "Install ffmpeg with: brew install ffmpeg" in error.remedy

    def test_voiceover_error(self):
        """Test voiceover system error."""
        error = VoiceoverError(
            issue="TTS backend not available",
            component="coqui",
            fallback_action="silent mode",
            voice="en_US",
            language="en",
        )

        assert error.severity == ErrorSeverity.WARNING  # Should be warning, not error
        assert error.metadata["voiceover_component"] == "coqui"
        assert error.metadata["voice"] == "en_US"
        assert "Fallback: silent mode" in error.remedy

    def test_plugin_error(self):
        """Test plugin system error."""
        error = PluginError(
            issue="Version incompatibility",
            plugin_name="advanced_widgets",
            action_taken="skipping plugin",
            plugin_version="2.0.0",
            required_version=">=1.5",
            current_version="1.2.0",
        )

        assert error.severity == ErrorSeverity.WARNING
        assert error.metadata["plugin_name"] == "advanced_widgets"
        assert error.metadata["plugin_version"] == "2.0.0"
        assert "Action taken: skipping plugin" in error.remedy


@pytest.mark.unit
class TestErrorFactories:
    """Test error factory functions."""

    def test_create_unknown_key_error(self):
        """Test unknown key error factory."""
        context = FileContext("config.yaml", line_number=10)
        error = create_unknown_key_error(
            unknown_key="tming",
            valid_keys=["timing", "render", "scenario"],
            file_context=context,
        )

        assert isinstance(error, ConfigError)
        assert "Unknown config key 'tming'" in error.issue
        assert error.context == context
        assert "timing" in error.suggestions  # Should suggest correction

    def test_create_type_mismatch_error(self):
        """Test type mismatch error factory."""
        context = FileContext("config.yaml", line_number=5)
        error = create_type_mismatch_error(
            key="frame_rate",
            expected_type="int",
            actual_type="str",
            file_context=context,
        )

        assert isinstance(error, ConfigError)
        assert "Expected int for 'frame_rate', got str" in error.issue
        assert error.metadata["expected_type"] == "int"
        assert error.metadata["actual_type"] == "str"

    def test_create_missing_field_error(self):
        """Test missing field error factory."""
        context = FileContext("scenario.yaml", line_number=8)
        error = create_missing_field_error(
            field="start",
            file_context=context,
        )

        assert isinstance(error, ConfigError)
        assert "Missing required field 'start'" in error.issue
        assert "Add the required field" in error.remedy

    def test_create_invalid_enum_error(self):
        """Test invalid enum error factory."""
        context = FileContext("config.yaml", line_number=12)
        error = create_invalid_enum_error(
            key="quality",
            invalid_value="hgh",  # Typo for "high"
            valid_options=["draft", "medium", "high"],
            file_context=context,
        )

        assert isinstance(error, ConfigError)
        assert "Invalid value 'hgh' for 'quality'" in error.issue
        assert error.metadata["valid_options"] == ["draft", "medium", "high"]
        # Should generate suggestions for the invalid enum value
        assert len(error.suggestions) > 0
        assert "high" in error.suggestions  # Should suggest "high" for "hgh"


@pytest.mark.unit
class TestErrorMessageFormatting:
    """Test error message formatting and display."""

    def test_basic_message_formatting(self):
        """Test basic error message structure."""
        error = AGLOVizError(
            issue="Test issue",
            remedy="Test remedy",
        )

        message = error.format_message()
        assert message == "AGLOVizError - Test issue - Test remedy"

    def test_message_with_context(self):
        """Test error message with context."""
        context = FileContext("test.yaml", line_number=5)
        error = AGLOVizError(
            issue="Test issue",
            context=context,
        )

        message = error.format_message()
        assert message == "AGLOVizError - test.yaml:5 - Test issue"

    def test_message_without_remedy(self):
        """Test error message without remedy."""
        error = AGLOVizError(issue="Test issue")

        message = error.format_message()
        assert message == "AGLOVizError - Test issue"
        assert " - " not in message.split("Test issue")[1]  # No trailing separator

    def test_rich_message_formatting(self):
        """Test rich console message formatting."""
        # This test verifies the method runs without error
        # Full rich output testing would require more complex mocking
        console = Console(file=open('/dev/null', 'w'))  # Suppress output

        error = AGLOVizError(
            issue="Test error",
            remedy="Test remedy",
            suggestions=["suggestion1", "suggestion2"],
            severity=ErrorSeverity.WARNING,
        )

        # Should not raise an exception
        error.format_rich_message(console)
        console.file.close()


@pytest.mark.unit
class TestErrorSeverityHandling:
    """Test error severity classification and handling."""

    def test_critical_error(self):
        """Test critical error creation."""
        error = AGLOVizError(
            issue="System cannot continue",
            severity=ErrorSeverity.CRITICAL,
        )

        assert error.severity == ErrorSeverity.CRITICAL

    def test_warning_error(self):
        """Test warning-level error."""
        error = VoiceoverError(
            issue="TTS not available",
            component="coqui",
            fallback_action="silent mode",
        )

        # VoiceoverError defaults to WARNING severity
        assert error.severity == ErrorSeverity.WARNING

    def test_error_metadata_preservation(self):
        """Test that custom metadata is preserved."""
        custom_metadata = {
            "user_input": "invalid_value",
            "timestamp": "2024-01-01T00:00:00",
            "session_id": "abc123",
        }

        error = AGLOVizError(
            issue="Test error",
            metadata=custom_metadata,
        )

        assert error.metadata == custom_metadata

        # Should be included in serialization
        error_dict = error.to_dict()
        assert error_dict["metadata"] == custom_metadata


@pytest.mark.unit
class TestErrorIntegrationPatterns:
    """Test common error usage patterns and integration."""

    def test_config_validation_error_pattern(self):
        """Test typical config validation error pattern."""
        # Simulate a config validation scenario
        context = FileContext("scenario.yaml", line_number=15)
        error = ConfigError(
            issue="Invalid timing mode 'fase'",
            context=context,
            config_key="timing.mode",
            valid_options=["draft", "normal", "fast"],
        )

        # Should have auto-generated suggestions
        assert "fast" in error.suggestions  # Should suggest "fast" for "fase"
        assert error.context == context
        assert "timing.mode" in error.metadata["config_key"]

    def test_storyboard_action_error_pattern(self):
        """Test typical storyboard action error pattern."""
        error = StoryboardError(
            issue="Unknown action 'show_titel'",
            act="intro",
            shot="setup",
            beat="title_display",
            action="show_titel",
            suggestions=["show_title"],
        )

        assert "Act intro/Shot setup/Beat title_display" in error.format_message()
        assert error.metadata["action"] == "show_titel"
        assert "show_title" in error.suggestions

    def test_algorithm_crash_error_pattern(self):
        """Test typical algorithm crash error pattern."""
        crash_state = {
            "current_node": "(5,5)",
            "queue": ["(4,5)", "(6,5)"],
            "visited": ["(0,0)", "(1,0)", "(2,0)"],
        }

        error = AdapterError(
            issue="KeyError: 'neighbors' not found",
            algorithm="bfs",
            step_index=25,
            current_state=crash_state,
        )

        assert "bfs[step 25]" in error.format_message()
        assert error.metadata["state_snapshot"] == crash_state
        assert "minimal scenario" in error.remedy

    def test_multiple_error_aggregation(self):
        """Test pattern for collecting multiple errors."""
        errors = [
            ConfigError(issue="Missing field 'start'", config_key="start"),
            ConfigError(issue="Invalid type for 'goal'", config_key="goal"),
            ConfigError(issue="Unknown key 'tming'", config_key="tming", valid_options=["timing"]),
        ]

        # Verify all errors are properly structured
        for error in errors:
            assert isinstance(error, ConfigError)
            assert error.issue
            assert error.metadata.get("config_key")

        # Verify they can be serialized for logging
        error_dicts = [error.to_dict() for error in errors]
        assert len(error_dicts) == 3
        assert all("config_key" in ed["metadata"] for ed in error_dicts)


@pytest.mark.unit
class TestErrorCategories:
    """Test error category enumeration."""

    def test_all_error_categories_exist(self):
        """Test that all expected error categories are defined."""
        expected_categories = [
            "ConfigError",
            "StoryboardError",
            "AdapterError",
            "ScenarioError",
            "RegistryError",
            "RenderError",
            "VoiceoverError",
            "PluginError",
        ]

        for category in expected_categories:
            assert hasattr(ErrorCategory, category.upper().replace("ERROR", ""))

    def test_error_severity_levels(self):
        """Test error severity enumeration."""
        assert ErrorSeverity.CRITICAL == "critical"
        assert ErrorSeverity.ERROR == "error"
        assert ErrorSeverity.WARNING == "warning"
        assert ErrorSeverity.INFO == "info"

    def test_error_category_consistency(self):
        """Test that error classes match their category names."""
        config_error = ConfigError(issue="test")
        assert config_error.category == "ConfigError"

        storyboard_error = StoryboardError(issue="test", act="1", shot="1", beat="1")
        assert storyboard_error.category == "StoryboardError"

        adapter_error = AdapterError(issue="test", algorithm="bfs", step_index=1)
        assert adapter_error.category == "AdapterError"
