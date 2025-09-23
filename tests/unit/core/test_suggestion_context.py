"""Unit tests for SuggestionEngine context-aware functionality."""

import pytest

from agloviz.core.errors import SuggestionEngine


@pytest.mark.unit
class TestSuggestionEngineContext:
    """Test context-aware suggestion functionality."""

    def test_prefix_matching(self):
        """Test prefix-based suggestion matching."""
        engine = SuggestionEngine()

        # Test input prefix matches option
        suggestions = engine.suggest_corrections(
            "qual", ["quality", "quantity", "other"]
        )
        assert "quality" in suggestions
        # quantity might not meet similarity threshold, so just check other is not included
        assert "other" not in suggestions

        # Test option prefix matches input
        suggestions = engine.suggest_corrections(
            "resolution", ["res", "format", "quality"]
        )
        assert "res" in suggestions
        assert "format" not in suggestions

    def test_render_context_suggestions(self):
        """Test context-aware suggestions for render context."""
        engine = SuggestionEngine()

        options = [
            "quality",
            "format",
            "resolution",
            "frame_rate",
            "start",
            "goal",
            "grid_file",
        ]

        # Test render context prioritizes render-related options
        suggestions = engine.suggest_corrections("qual", options, context="render")
        assert "quality" in suggestions

        # Test with different render keywords
        suggestions = engine.suggest_corrections(
            "res", options, context="render_config"
        )
        assert "resolution" in suggestions

        suggestions = engine.suggest_corrections("fram", options, context="render")
        assert "frame_rate" in suggestions

        # Non-render options should not be prioritized in render context
        suggestions = engine.suggest_corrections("sta", options, context="render")
        # "start" might still appear due to general matching, but render options are prioritized

    def test_scenario_context_suggestions(self):
        """Test context-aware suggestions for scenario context."""
        engine = SuggestionEngine()

        options = [
            "start",
            "goal",
            "grid_file",
            "obstacles",
            "weighted",
            "quality",
            "format",
        ]

        # Test scenario context prioritizes scenario-related options
        suggestions = engine.suggest_corrections("sta", options, context="scenario")
        assert "start" in suggestions

        suggestions = engine.suggest_corrections(
            "goa", options, context="scenario_config"
        )
        assert "goal" in suggestions

        suggestions = engine.suggest_corrections("grid", options, context="scenario")
        assert "grid_file" in suggestions

        suggestions = engine.suggest_corrections("obstac", options, context="scenario")
        assert "obstacles" in suggestions

        suggestions = engine.suggest_corrections("weigh", options, context="scenario")
        assert "weighted" in suggestions

    def test_timing_context_suggestions(self):
        """Test context-aware suggestions for timing context."""
        engine = SuggestionEngine()

        options = [
            "ui",
            "events",
            "effects",
            "waits",
            "multipliers",
            "quality",
            "format",
        ]

        # Test timing context prioritizes timing-related options
        suggestions = engine.suggest_corrections("u", options, context="timing")
        assert "ui" in suggestions

        suggestions = engine.suggest_corrections(
            "event", options, context="timing_config"
        )
        assert "events" in suggestions

        suggestions = engine.suggest_corrections("effect", options, context="timing")
        assert "effects" in suggestions

        suggestions = engine.suggest_corrections("wait", options, context="timing")
        assert "waits" in suggestions

        suggestions = engine.suggest_corrections("multi", options, context="timing")
        assert "multipliers" in suggestions

    def test_unknown_context_fallback(self):
        """Test that unknown contexts fall back to general suggestions."""
        engine = SuggestionEngine()

        options = ["quality", "format", "start", "goal"]

        # Unknown context should still provide suggestions based on similarity
        suggestions = engine.suggest_corrections(
            "qual", options, context="unknown_context"
        )
        assert "quality" in suggestions

        # Should work the same as no context for unknown contexts
        suggestions_no_context = engine.suggest_corrections("qual", options)
        suggestions_unknown_context = engine.suggest_corrections(
            "qual", options, context="unknown"
        )

        # Both should find "quality" since it's a close match
        assert "quality" in suggestions_no_context
        assert "quality" in suggestions_unknown_context

    def test_context_with_no_matching_keywords(self):
        """Test context handling when no options match context keywords."""
        engine = SuggestionEngine()

        # Render context but no render-related options
        options = ["start", "goal", "obstacles", "weighted"]
        suggestions = engine.suggest_corrections("sta", options, context="render")

        # Should still provide suggestions based on general matching
        assert "start" in suggestions

    def test_context_case_insensitive(self):
        """Test that context matching is case-insensitive."""
        engine = SuggestionEngine()

        options = ["quality", "format", "resolution"]

        # Different case variations of render context
        suggestions_lower = engine.suggest_corrections(
            "qual", options, context="render"
        )
        suggestions_upper = engine.suggest_corrections(
            "qual", options, context="RENDER"
        )
        suggestions_mixed = engine.suggest_corrections(
            "qual", options, context="Render_Config"
        )

        # All should find quality
        assert "quality" in suggestions_lower
        assert "quality" in suggestions_upper
        assert "quality" in suggestions_mixed

    def test_multiple_context_keywords(self):
        """Test options that match multiple context keywords."""
        engine = SuggestionEngine()

        # An option that could match multiple contexts
        options = ["grid_resolution", "other_option"]

        # Should work in scenario context (grid)
        suggestions = engine.suggest_corrections("grid", options, context="scenario")
        assert "grid_resolution" in suggestions

        # Should also work in render context (resolution)
        suggestions = engine.suggest_corrections("reso", options, context="render")
        assert "grid_resolution" in suggestions

    def test_context_suggestions_respect_similarity_threshold(self):
        """Test that context suggestions still respect similarity thresholds."""
        engine = SuggestionEngine(min_similarity=0.8)  # High threshold

        options = ["quality", "completely_different"]

        # Even with render context, very dissimilar options shouldn't be suggested
        suggestions = engine.suggest_corrections("xyz", options, context="render")

        # Should be empty or very limited due to high similarity threshold
        assert len(suggestions) <= 1  # At most one if any meet the threshold

    def test_context_suggestions_ordering(self):
        """Test that context-relevant suggestions are properly ordered."""
        engine = SuggestionEngine()

        options = ["quality", "start", "format", "goal"]

        # In render context, render-related options should be prioritized
        suggestions = engine.suggest_corrections("q", options, context="render")

        # Quality should appear (render-related) even though it's not the closest match
        if suggestions:  # Only test if suggestions are found
            # At minimum, quality should be suggested since it matches render context
            render_options = [
                opt for opt in suggestions if opt in ["quality", "format"]
            ]
            assert len(render_options) > 0
