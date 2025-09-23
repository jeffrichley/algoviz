"""Tests for timing parameter resolution."""

from omegaconf import OmegaConf

from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.resolvers import ResolverContext, _resolve_timing_path


class TestTimingParameterResolution:
    """Test timing parameter resolution."""

    def test_resolve_simple_timing_path(self):
        """Test resolving simple timing configuration paths."""
        timing_config = {
            "ui": 1.0,
            "events": 0.8,
            "effects": 0.5,
            "waits": 0.5
        }

        # Test simple path resolution
        assert _resolve_timing_path("ui", timing_config) == 1.0
        assert _resolve_timing_path("events", timing_config) == 0.8
        assert _resolve_timing_path("effects", timing_config) == 0.5
        assert _resolve_timing_path("waits", timing_config) == 0.5

    def test_resolve_timing_path_with_pydantic_model(self):
        """Test resolving timing paths with Pydantic TimingConfig model."""
        timing_config = TimingConfig(
            mode=TimingMode.NORMAL,
            ui=1.0,
            events=0.8,
            effects=0.5,
            waits=0.5
        )

        # Test Pydantic model attribute resolution
        assert _resolve_timing_path("mode", timing_config) == TimingMode.NORMAL
        assert _resolve_timing_path("ui", timing_config) == 1.0
        assert _resolve_timing_path("events", timing_config) == 0.8
        assert _resolve_timing_path("effects", timing_config) == 0.5
        assert _resolve_timing_path("waits", timing_config) == 0.5

    def test_resolve_timing_path_with_context(self):
        """Test resolving timing paths using ResolverContext."""
        timing_config = {
            "ui": 1.5,
            "events": 1.2,
            "effects": 0.8
        }

        context = ResolverContext(timing=timing_config)

        with context:
            assert _resolve_timing_path("ui") == 1.5
            assert _resolve_timing_path("events") == 1.2
            assert _resolve_timing_path("effects") == 0.8

    def test_resolve_timing_path_without_context(self):
        """Test resolving timing paths without context."""
        # Should return template pattern when no context and no timing_config provided
        assert _resolve_timing_path("ui") == "${timing_value:ui}"
        assert _resolve_timing_path("events") == "${timing_value:events}"
        assert _resolve_timing_path("missing") == "${timing_value:missing}"

    def test_resolve_timing_path_missing_keys(self):
        """Test resolving missing timing configuration keys."""
        timing_config = {
            "ui": 1.0,
            "events": 0.8
        }

        # Test missing key resolution (should return default 1.0)
        assert _resolve_timing_path("missing", timing_config) == 1.0
        assert _resolve_timing_path("effects", timing_config) == 1.0
        assert _resolve_timing_path("waits", timing_config) == 1.0

    def test_resolve_timing_path_with_omega_conf_templates(self):
        """Test resolving timing paths with OmegaConf template syntax."""
        timing_config = {
            "ui": 1.0,
            "events": 0.8,
            "effects": 0.5
        }

        # Test with OmegaConf template resolution
        template = "${timing_value:ui}"
        params_config = OmegaConf.create({"duration": template})

        # This would be resolved by OmegaConf with the resolver
        # For now, test the direct resolver function
        assert _resolve_timing_path("ui", timing_config) == 1.0
        assert _resolve_timing_path("events", timing_config) == 0.8
        assert _resolve_timing_path("effects", timing_config) == 0.5

    def test_resolve_timing_path_error_handling(self):
        """Test error handling for invalid timing configuration data."""
        # Test with None timing config - should return template pattern
        assert _resolve_timing_path("ui", None) == "${timing_value:ui}"

        # Test with empty timing config - should return template pattern
        assert _resolve_timing_path("ui", {}) == "${timing_value:ui}"

        # Test with invalid path
        timing_config = {"ui": 1.0}
        assert _resolve_timing_path("", timing_config) == 1.0

    def test_resolve_timing_path_with_different_modes(self):
        """Test resolving timing paths with different timing modes."""
        # Test with different timing modes
        draft_timing = TimingConfig(mode=TimingMode.DRAFT, ui=0.5, events=0.4, effects=0.25, waits=0.25)
        normal_timing = TimingConfig(mode=TimingMode.NORMAL, ui=1.0, events=0.8, effects=0.5, waits=0.5)
        fast_timing = TimingConfig(mode=TimingMode.FAST, ui=0.25, events=0.2, effects=0.125, waits=0.125)

        # Test mode resolution
        assert _resolve_timing_path("mode", draft_timing) == TimingMode.DRAFT
        assert _resolve_timing_path("mode", normal_timing) == TimingMode.NORMAL
        assert _resolve_timing_path("mode", fast_timing) == TimingMode.FAST

        # Test bucket resolution
        assert _resolve_timing_path("ui", draft_timing) == 0.5
        assert _resolve_timing_path("ui", normal_timing) == 1.0
        assert _resolve_timing_path("ui", fast_timing) == 0.25

        assert _resolve_timing_path("effects", draft_timing) == 0.25
        assert _resolve_timing_path("effects", normal_timing) == 0.5
        assert _resolve_timing_path("effects", fast_timing) == 0.125

    def test_resolve_complex_timing_structure(self):
        """Test resolving complex timing configuration structures."""
        timing_config = {
            "mode": "normal",
            "base_timings": {
                "ui": 1.0,
                "events": 0.8,
                "effects": 0.5,
                "waits": 0.5
            },
            "multipliers": {
                "draft": 0.5,
                "normal": 1.0,
                "fast": 0.25
            },
            "custom_timings": {
                "animation": 1.2,
                "transition": 0.3,
                "highlight": 0.8
            }
        }

        # Test various complex paths
        assert _resolve_timing_path("mode", timing_config) == "normal"
        assert _resolve_timing_path("base_timings", timing_config) == {
            "ui": 1.0,
            "events": 0.8,
            "effects": 0.5,
            "waits": 0.5
        }
        assert _resolve_timing_path("multipliers", timing_config) == {
            "draft": 0.5,
            "normal": 1.0,
            "fast": 0.25
        }
        assert _resolve_timing_path("custom_timings", timing_config) == {
            "animation": 1.2,
            "transition": 0.3,
            "highlight": 0.8
        }

    def test_resolve_timing_path_with_numeric_values(self):
        """Test resolving timing paths with various numeric values."""
        timing_config = {
            "integer_timing": 2,
            "float_timing": 1.5,
            "zero_timing": 0.0,
            "negative_timing": -0.5,
            "large_timing": 10.0
        }

        # Test various numeric value types
        assert _resolve_timing_path("integer_timing", timing_config) == 2
        assert _resolve_timing_path("float_timing", timing_config) == 1.5
        assert _resolve_timing_path("zero_timing", timing_config) == 0.0
        assert _resolve_timing_path("negative_timing", timing_config) == -0.5
        assert _resolve_timing_path("large_timing", timing_config) == 10.0
