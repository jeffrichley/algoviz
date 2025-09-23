"""Unit tests for ALGOViz configuration models - Updated for new architecture."""

import pytest
from pydantic import ValidationError

from agloviz.config.models import (
    ScenarioConfig,
    SceneConfig,
    ThemeConfig,
    TimingConfig,
    TimingMode,
    WidgetConfigSpec,
)


@pytest.mark.unit
class TestScenarioConfig:
    """Test ScenarioConfig validation and behavior."""

    def test_valid_scenario_config(self):
        """Test creating a valid scenario configuration."""
        config = ScenarioConfig(
            name="test_scenario",
            obstacles=[(1, 1), (2, 2)],
            start=(0, 0),
            goal=(9, 9),
            grid_size=(10, 10),
        )

        assert config.name == "test_scenario"
        assert config.obstacles == [(1, 1), (2, 2)]
        assert config.start == (0, 0)
        assert config.goal == (9, 9)
        assert config.grid_size == (10, 10)

    def test_scenario_config_defaults(self):
        """Test scenario configuration with default values."""
        config = ScenarioConfig(name="default_test")

        assert config.name == "default_test"
        assert config.obstacles == []
        assert config.start == (0, 0)
        assert config.goal == (9, 9)
        assert config.grid_size == (10, 10)

    def test_scenario_config_validation(self):
        """Test scenario configuration validation."""
        # Should require name
        with pytest.raises(ValidationError):
            ScenarioConfig()

        # Should accept valid data
        config = ScenarioConfig(name="valid")
        assert config.name == "valid"


@pytest.mark.unit
class TestThemeConfig:
    """Test ThemeConfig validation and behavior."""

    def test_valid_theme_config(self):
        """Test creating a valid theme configuration."""
        custom_colors = {
            "visited": "#FF0000",
            "frontier": "#00FF00",
            "goal": "#0000FF",
            "path": "#FFFF00",
            "obstacle": "#000000",
            "grid": "#FFFFFF",
        }

        config = ThemeConfig(name="custom_theme", colors=custom_colors)

        assert config.name == "custom_theme"
        assert config.colors["visited"] == "#FF0000"
        assert config.colors["frontier"] == "#00FF00"

    def test_theme_config_defaults(self):
        """Test theme configuration with default values."""
        config = ThemeConfig()

        assert config.name == "default"
        assert "visited" in config.colors
        assert "frontier" in config.colors
        assert "goal" in config.colors
        assert "path" in config.colors
        assert "obstacle" in config.colors
        assert "grid" in config.colors


@pytest.mark.unit
class TestTimingConfig:
    """Test TimingConfig validation and behavior."""

    def test_valid_timing_config(self):
        """Test creating a valid timing configuration."""
        config = TimingConfig(
            mode=TimingMode.DRAFT, ui=0.5, events=0.4, effects=0.3, waits=0.25
        )

        assert config.mode == TimingMode.DRAFT
        assert config.ui == 0.5
        assert config.events == 0.4
        assert config.effects == 0.3
        assert config.waits == 0.25

    def test_timing_config_defaults(self):
        """Test timing configuration with default values."""
        config = TimingConfig()

        assert config.mode == TimingMode.NORMAL
        assert config.ui == 1.0
        assert config.events == 0.8
        assert config.effects == 0.5
        assert config.waits == 0.5

    def test_timing_config_validation(self):
        """Test timing configuration validation."""
        # Should accept valid timing modes
        for mode in TimingMode:
            config = TimingConfig(mode=mode)
            assert config.mode == mode

        # Should validate duration ranges
        with pytest.raises(ValidationError):
            TimingConfig(step_duration=0.05)  # Too low

        with pytest.raises(ValidationError):
            TimingConfig(step_duration=15.0)  # Too high


@pytest.mark.unit
class TestSceneConfig:
    """Test SceneConfig validation and behavior."""

    def test_valid_scene_config(self):
        """Test creating a valid scene configuration."""
        config = SceneConfig(
            name="test_scene",
            algorithm="bfs",
            widgets={
                "grid": {"_target_": "agloviz.widgets.grid.GridWidget", "width": 10},
                "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"},
            },
            event_bindings={
                "enqueue": [{"widget": "queue", "action": "add_element", "order": 1}]
            },
        )

        assert config.name == "test_scene"
        assert config.algorithm == "bfs"
        assert len(config.widgets) == 2
        assert "grid" in config.widgets
        assert "queue" in config.widgets
        assert "enqueue" in config.event_bindings

    def test_scene_config_defaults(self):
        """Test scene configuration with default values."""
        config = SceneConfig(name="default_scene", algorithm="dfs")

        assert config.name == "default_scene"
        assert config.algorithm == "dfs"
        assert config.widgets == {}
        assert config.event_bindings == {}

    def test_scene_config_validation(self):
        """Test scene configuration validation."""
        # Should require name and algorithm
        with pytest.raises(ValidationError):
            SceneConfig()

        with pytest.raises(ValidationError):
            SceneConfig(name="test")

        with pytest.raises(ValidationError):
            SceneConfig(algorithm="bfs")

        # Should accept valid data
        config = SceneConfig(name="valid", algorithm="bfs")
        assert config.name == "valid"
        assert config.algorithm == "bfs"


@pytest.mark.unit
class TestWidgetConfigSpec:
    """Test WidgetConfigSpec validation and behavior."""

    def test_valid_widget_config_spec(self):
        """Test creating a valid widget config spec."""
        spec = WidgetConfigSpec(_target_="agloviz.widgets.grid.GridWidget")

        assert spec._target_ == "agloviz.widgets.grid.GridWidget"

    def test_widget_config_spec_validation(self):
        """Test widget config spec validation."""
        # Should require _target_
        with pytest.raises(TypeError):
            WidgetConfigSpec()

        # Should accept valid _target_
        spec = WidgetConfigSpec(_target_="agloviz.widgets.queue.QueueWidget")
        assert spec._target_ == "agloviz.widgets.queue.QueueWidget"
