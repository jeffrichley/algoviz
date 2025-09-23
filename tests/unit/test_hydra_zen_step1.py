"""Unit tests for STEP 1: Hydra-zen Configuration Builders.

Tests the hydra-zen configuration builders created in src/agloviz/config/hydra_zen.py
"""

import pytest
from hydra_zen import instantiate

from agloviz.config.hydra_zen import (
    DarkThemeConfig,
    # Theme configs
    DefaultThemeConfig,
    # Renderer configs
    DraftRenderer,
    # Timing configs
    DraftTimingConfig,
    FastTimingConfig,
    HDRenderer,
    HighContrastThemeConfig,
    MazeLargeConfig,
    # Scenario configs
    MazeSmallConfig,
    MediumRenderer,
    NormalTimingConfig,
    WeightedGraphConfig,
)
from agloviz.config.models import ScenarioConfig, ThemeConfig, TimingConfig
from agloviz.rendering.renderer import SimpleRenderer


class TestRendererConfigs:
    """Test renderer configuration builders."""

    def test_draft_renderer_instantiation(self):
        """Test that DraftRenderer can be instantiated."""
        renderer = instantiate(DraftRenderer)
        assert isinstance(renderer, SimpleRenderer)
        assert renderer.config.resolution == (854, 480)
        assert renderer.config.frame_rate == 15

    def test_medium_renderer_instantiation(self):
        """Test that MediumRenderer can be instantiated."""
        renderer = instantiate(MediumRenderer)
        assert isinstance(renderer, SimpleRenderer)
        assert renderer.config.resolution == (1280, 720)
        assert renderer.config.frame_rate == 30

    def test_hd_renderer_instantiation(self):
        """Test that HDRenderer can be instantiated."""
        renderer = instantiate(HDRenderer)
        assert isinstance(renderer, SimpleRenderer)
        assert renderer.config.resolution == (1920, 1080)
        assert renderer.config.frame_rate == 60

    def test_all_renderer_configs_have_different_resolutions(self):
        """Test that renderer configs have progressively higher resolutions."""
        draft = instantiate(DraftRenderer)
        medium = instantiate(MediumRenderer)
        hd = instantiate(HDRenderer)

        draft_pixels = draft.config.resolution[0] * draft.config.resolution[1]
        medium_pixels = medium.config.resolution[0] * medium.config.resolution[1]
        hd_pixels = hd.config.resolution[0] * hd.config.resolution[1]

        assert draft_pixels < medium_pixels < hd_pixels


class TestScenarioConfigs:
    """Test scenario configuration builders."""

    def test_maze_small_config_instantiation(self):
        """Test that MazeSmallConfig can be instantiated."""
        scenario = instantiate(MazeSmallConfig)
        assert isinstance(scenario, ScenarioConfig)
        assert scenario.name == "maze_small"
        assert scenario.grid_size == (10, 10)
        assert len(scenario.obstacles) == 3

    def test_maze_large_config_instantiation(self):
        """Test that MazeLargeConfig can be instantiated."""
        scenario = instantiate(MazeLargeConfig)
        assert isinstance(scenario, ScenarioConfig)
        assert scenario.name == "maze_large"
        assert scenario.grid_size == (20, 20)
        assert len(scenario.obstacles) == 4

    def test_weighted_graph_config_instantiation(self):
        """Test that WeightedGraphConfig can be instantiated."""
        scenario = instantiate(WeightedGraphConfig)
        assert isinstance(scenario, ScenarioConfig)
        assert scenario.name == "weighted_graph"
        assert len(scenario.obstacles) == 0  # No obstacles in weighted graph


class TestThemeConfigs:
    """Test theme configuration builders."""

    def test_default_theme_config_instantiation(self):
        """Test that DefaultThemeConfig can be instantiated."""
        theme = instantiate(DefaultThemeConfig)
        assert isinstance(theme, ThemeConfig)
        assert theme.name == "default"
        assert "visited" in theme.colors
        assert "frontier" in theme.colors

    def test_dark_theme_config_instantiation(self):
        """Test that DarkThemeConfig can be instantiated."""
        theme = instantiate(DarkThemeConfig)
        assert isinstance(theme, ThemeConfig)
        assert theme.name == "dark"
        assert theme.colors["visited"] == "#BB86FC"
        assert theme.colors["frontier"] == "#03DAC6"

    def test_high_contrast_theme_config_instantiation(self):
        """Test that HighContrastThemeConfig can be instantiated."""
        theme = instantiate(HighContrastThemeConfig)
        assert isinstance(theme, ThemeConfig)
        assert theme.name == "high_contrast"
        assert theme.colors["visited"] == "#00FF00"
        assert theme.colors["frontier"] == "#0000FF"


class TestTimingConfigs:
    """Test timing configuration builders."""

    def test_draft_timing_config_instantiation(self):
        """Test that DraftTimingConfig can be instantiated."""
        timing = instantiate(DraftTimingConfig)
        assert isinstance(timing, TimingConfig)
        assert timing.mode.value == "draft"

    def test_normal_timing_config_instantiation(self):
        """Test that NormalTimingConfig can be instantiated."""
        timing = instantiate(NormalTimingConfig)
        assert isinstance(timing, TimingConfig)
        assert timing.mode.value == "normal"

    def test_fast_timing_config_instantiation(self):
        """Test that FastTimingConfig can be instantiated."""
        timing = instantiate(FastTimingConfig)
        assert isinstance(timing, TimingConfig)
        assert timing.mode.value == "fast"


class TestHydraZenBenefits:
    """Test the key benefits of hydra-zen configuration builders."""

    def test_type_safety_through_builds(self):
        """Test that builds() provides type safety through signature inspection."""
        # If any of these configs had type mismatches, builds() would fail at definition time
        configs = [
            DraftRenderer, MediumRenderer, HDRenderer,
            MazeSmallConfig, MazeLargeConfig, WeightedGraphConfig,
            DefaultThemeConfig, DarkThemeConfig, HighContrastThemeConfig,
            DraftTimingConfig, NormalTimingConfig, FastTimingConfig
        ]

        # All configs should instantiate without type errors
        for config in configs:
            instance = instantiate(config)
            assert instance is not None

    def test_configuration_separation_from_cli(self):
        """Test that configuration builders have no CLI dependencies."""
        import inspect

        from agloviz.config import hydra_zen

        # Check that hydra_zen module has no CLI imports
        source = inspect.getsource(hydra_zen)

        # Should not import any CLI-related modules
        assert "typer" not in source.lower()
        assert "click" not in source.lower()
        assert "argparse" not in source.lower()
        assert "sys.argv" not in source.lower()

        # Should only import configuration-related modules
        assert "hydra_zen" in source
        assert "builds" in source

    def test_all_configs_are_builds_objects(self):
        """Test that all configuration objects are hydra-zen builds."""

        configs = [
            DraftRenderer, MediumRenderer, HDRenderer,
            MazeSmallConfig, MazeLargeConfig, WeightedGraphConfig,
            DefaultThemeConfig, DarkThemeConfig, HighContrastThemeConfig,
            DraftTimingConfig, NormalTimingConfig, FastTimingConfig
        ]

        for config in configs:
            # All should be hydra-zen builds objects
            assert hasattr(config, '_target_'), f"Config {config} missing _target_"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
