"""Simplified property-based tests for SuggestionEngine using Hypothesis.

This module uses Hypothesis to generate test cases for the suggestion algorithms,
optimized for speed while maintaining coverage of key properties.
"""

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from agloviz.core.errors import SuggestionEngine

# Global settings for faster tests
fast_settings = settings(
    max_examples=5,  # Very few examples for speed
    deadline=500,  # 0.5 second deadline per test
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)


@pytest.mark.unit
class TestSuggestionEngineProperties:
    """Essential property-based tests for SuggestionEngine using Hypothesis."""

    @given(
        input_str=st.text(
            alphabet=st.characters(whitelist_categories=["L"]), min_size=1, max_size=6
        ),
        valid_options=st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=["L"]),
                min_size=1,
                max_size=6,
            ),
            min_size=1,
            max_size=3,
        ),
    )
    @fast_settings
    def test_suggest_corrections_basic_properties(
        self, input_str: str, valid_options: list[str]
    ) -> None:
        """Test basic suggestion engine properties with generated inputs."""
        # Ensure unique options
        assume(len(set(valid_options)) == len(valid_options))

        engine = SuggestionEngine(max_suggestions=3)
        suggestions = engine.suggest_corrections(input_str, valid_options)

        # Property 1: Number of suggestions should not exceed max_suggestions
        assert len(suggestions) <= 3

        # Property 2: All suggestions should be from valid_options
        assert all(suggestion in valid_options for suggestion in suggestions)

        # Property 3: No duplicate suggestions
        assert len(suggestions) == len(set(suggestions))

    @given(
        s1=st.text(alphabet=st.characters(whitelist_categories=["L"]), max_size=4),
        s2=st.text(alphabet=st.characters(whitelist_categories=["L"]), max_size=4),
    )
    @fast_settings
    def test_levenshtein_distance_properties(self, s1: str, s2: str) -> None:
        """Test Levenshtein distance algorithm properties."""
        engine = SuggestionEngine()
        distance = engine._levenshtein_distance(s1, s2)

        # Property 1: Distance is non-negative
        assert distance >= 0

        # Property 2: Distance is symmetric
        assert distance == engine._levenshtein_distance(s2, s1)

        # Property 3: Distance is 0 if and only if strings are equal
        if s1 == s2:
            assert distance == 0

        # Property 4: Distance is at most the length of the longer string
        assert distance <= max(len(s1), len(s2))

    @given(
        input_str=st.sampled_from(["timing", "render", "config", "test"]),
        valid_options=st.sampled_from(
            [
                ["timing", "render", "scenario"],
                ["config", "setting", "option"],
                ["test", "spec", "check"],
            ]
        ),
    )
    @fast_settings
    def test_exact_match_always_suggested(
        self, input_str: str, valid_options: list[str]
    ) -> None:
        """Test that exact matches (case-insensitive) are always suggested."""
        engine = SuggestionEngine()
        suggestions = engine.suggest_corrections(input_str, valid_options)

        # If there's an exact case-insensitive match, it should be in suggestions
        exact_matches = [
            opt for opt in valid_options if opt.lower() == input_str.lower()
        ]
        for exact_match in exact_matches:
            assert exact_match in suggestions

    @given(
        input_str=st.text(
            alphabet=st.characters(whitelist_categories=["L"]), min_size=1, max_size=5
        ),
    )
    @fast_settings
    def test_empty_options_returns_empty_suggestions(self, input_str: str) -> None:
        """Test that empty valid_options returns empty suggestions."""
        engine = SuggestionEngine()

        # Empty options should return empty suggestions
        empty_suggestions = engine.suggest_corrections(input_str, [])
        assert empty_suggestions == []


@pytest.mark.unit
class TestConfigErrorProperties:
    """Essential property-based tests for ConfigError with various inputs."""

    @given(
        config_keys=st.lists(
            st.sampled_from(["timing", "render", "scenario", "theme", "config"]),
            min_size=1,
            max_size=3,
            unique=True,
        ),
        typo_key=st.sampled_from(["tming", "rendr", "scenaro", "thme", "confg"]),
    )
    @fast_settings
    def test_config_error_suggestion_generation(
        self, config_keys: list[str], typo_key: str
    ) -> None:
        """Test ConfigError suggestion generation with various key combinations."""
        assume(typo_key not in config_keys)  # Ensure it's actually a typo

        from agloviz.core.errors import ConfigError

        error = ConfigError(
            issue=f"Unknown key '{typo_key}'",
            config_key=typo_key,
            valid_options=config_keys,
        )

        # Should have generated suggestions if there are similar keys
        engine = SuggestionEngine()
        manual_suggestions = engine.suggest_corrections(typo_key, config_keys)

        if manual_suggestions:
            # If manual suggestion engine finds matches, ConfigError should too
            assert len(error.suggestions) > 0

    @given(
        field_types=st.sampled_from(["str", "int", "float", "bool"]),
        actual_types=st.sampled_from(["str", "int", "float", "bool"]),
        field_names=st.sampled_from(["name", "count", "enabled", "value"]),
    )
    @fast_settings
    def test_type_mismatch_error_properties(
        self, field_types: str, actual_types: str, field_names: str
    ) -> None:
        """Test type mismatch error generation properties."""
        assume(field_types != actual_types)  # Must be different types

        from agloviz.core.errors import create_type_mismatch_error

        error = create_type_mismatch_error(
            key=field_names,
            expected_type=field_types,
            actual_type=actual_types,
        )

        # Properties that should always hold
        assert field_names in error.issue
        assert field_types in error.issue
        assert actual_types in error.issue
        assert error.metadata["expected_type"] == field_types
        assert error.metadata["actual_type"] == actual_types
        assert error.metadata["config_key"] == field_names


@pytest.mark.unit
class TestErrorMessageProperties:
    """Essential property-based tests for error message formatting."""

    @given(
        categories=st.sampled_from(["ConfigError", "StoryboardError", "AdapterError"]),
        issues=st.text(
            alphabet=st.characters(whitelist_categories=["L", "P"]),
            min_size=5,
            max_size=20,
        ),
    )
    @fast_settings
    def test_error_message_format_consistency(
        self, categories: str, issues: str
    ) -> None:
        """Test that error messages have consistent format regardless of content."""
        from agloviz.core.errors import AGLOVizError

        error = AGLOVizError(issue=issues)
        message = error.format_message()

        # Properties that should always hold
        assert error.category in message  # Category should appear in message
        assert issues in message  # Issue should appear in message

        # Message should have consistent separator structure
        parts = message.split(" - ")
        assert len(parts) >= 2  # At least category and issue
        assert parts[0] == error.category

    @given(
        file_paths=st.text(
            alphabet=st.characters(whitelist_categories=["L"]), min_size=1, max_size=10
        ),
        line_numbers=st.one_of(st.none(), st.integers(min_value=1, max_value=100)),
    )
    @fast_settings
    def test_file_context_format_properties(
        self, file_paths: str, line_numbers: int | None
    ) -> None:
        """Test file context formatting properties."""
        from agloviz.core.errors import FileContext

        context = FileContext(file_paths, line_numbers)
        location = context.format_location()

        # Properties that should always hold
        assert file_paths in location

        if line_numbers is not None:
            assert str(line_numbers) in location
            assert ":" in location  # Should have separator

        # Metadata should be complete
        metadata = context.get_metadata()
        assert metadata["file_path"] == file_paths
        assert metadata["line_number"] == line_numbers
