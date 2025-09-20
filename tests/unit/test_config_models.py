"""Unit tests for ALGOViz configuration models."""

import pytest
from pydantic import ValidationError

from agloviz.config.models import (
    RenderConfig,
    RenderFormat,
    RenderQuality,
    ScenarioConfig,
    SubtitleFormat,
    SubtitleMode,
    SubtitlesConfig,
    ThemeConfig,
    TimingConfig,
    TimingMode,
    VideoConfig,
    VoiceoverBackend,
    VoiceoverConfig,
)


@pytest.mark.unit
class TestScenarioConfig:
    """Test ScenarioConfig validation and behavior."""

    def test_valid_scenario_config(self):
        """Test creating a valid scenario configuration."""
        config = ScenarioConfig(
            name="test_maze",
            grid_file="grids/test.yaml",
            start=(0, 0),
            goal=(9, 9),
            obstacles=[(3, 3), (4, 4)],
            weighted=True,
        )

        assert config.name == "test_maze"
        assert config.grid_file == "grids/test.yaml"
        assert config.start == (0, 0)
        assert config.goal == (9, 9)
        assert config.obstacles == [(3, 3), (4, 4)]
        assert config.weighted is True

    def test_scenario_config_defaults(self):
        """Test scenario configuration with default values."""
        config = ScenarioConfig(
            name="simple",
            grid_file="grid.yaml",
            start=(0, 0),
            goal=(5, 5),
        )

        assert config.obstacles == []
        assert config.weighted is False

    def test_scenario_config_invalid_data(self):
        """Test scenario configuration validation errors."""
        with pytest.raises(ValidationError):
            ScenarioConfig(
                name="",  # Empty name should fail
                grid_file="grid.yaml",
                start=(0, 0),
                goal=(5, 5),
            )


@pytest.mark.unit
class TestThemeConfig:
    """Test ThemeConfig validation and behavior."""

    def test_valid_theme_config(self):
        """Test creating a valid theme configuration."""
        colors = {
            "visited": "#FF0000",
            "frontier": "#00FF00",
            "goal": "#0000FF",
        }

        config = ThemeConfig(name="custom", colors=colors)

        assert config.name == "custom"
        assert config.colors == colors

    def test_theme_config_defaults(self):
        """Test theme configuration with default values."""
        config = ThemeConfig()

        assert config.name == "default"
        assert "visited" in config.colors
        assert "frontier" in config.colors
        assert "goal" in config.colors
        assert config.colors["visited"] == "#4CAF50"


@pytest.mark.unit
class TestVoiceoverConfig:
    """Test VoiceoverConfig validation and behavior."""

    def test_valid_voiceover_config(self):
        """Test creating a valid voiceover configuration."""
        config = VoiceoverConfig(
            enabled=True,
            backend=VoiceoverBackend.COQUI,
            lang="en",
            voice="en_US_female",
            speed=1.2,
        )

        assert config.enabled is True
        assert config.backend == VoiceoverBackend.COQUI
        assert config.lang == "en"
        assert config.voice == "en_US_female"
        assert config.speed == 1.2

    def test_voiceover_config_defaults(self):
        """Test voiceover configuration with default values."""
        config = VoiceoverConfig()

        assert config.enabled is False
        assert config.backend == VoiceoverBackend.COQUI
        assert config.lang == "en"
        assert config.voice == "en_US"
        assert config.speed == 1.0

    def test_voiceover_speed_validation(self):
        """Test voiceover speed validation bounds."""
        # Valid speeds
        VoiceoverConfig(speed=0.5)
        VoiceoverConfig(speed=2.0)

        # Invalid speeds
        with pytest.raises(ValidationError):
            VoiceoverConfig(speed=0.05)  # Too slow

        with pytest.raises(ValidationError):
            VoiceoverConfig(speed=5.0)  # Too fast


@pytest.mark.unit
class TestSubtitlesConfig:
    """Test SubtitlesConfig validation and behavior."""

    def test_valid_subtitles_config(self):
        """Test creating a valid subtitles configuration."""
        config = SubtitlesConfig(
            enabled=True,
            mode=SubtitleMode.WHISPER_ALIGN,
            format=SubtitleFormat.VTT,
            burn_in=True,
        )

        assert config.enabled is True
        assert config.mode == SubtitleMode.WHISPER_ALIGN
        assert config.format == SubtitleFormat.VTT
        assert config.burn_in is True

    def test_subtitles_config_defaults(self):
        """Test subtitles configuration with default values."""
        config = SubtitlesConfig()

        assert config.enabled is False
        assert config.mode == SubtitleMode.BASELINE
        assert config.format == SubtitleFormat.SRT
        assert config.burn_in is False


@pytest.mark.unit
class TestRenderConfig:
    """Test RenderConfig validation and behavior."""

    def test_valid_render_config(self):
        """Test creating a valid render configuration."""
        config = RenderConfig(
            resolution=(2560, 1440),
            frame_rate=60,
            quality=RenderQuality.HIGH,
            format=RenderFormat.GIF,
        )

        assert config.resolution == (2560, 1440)
        assert config.frame_rate == 60
        assert config.quality == RenderQuality.HIGH
        assert config.format == RenderFormat.GIF

    def test_render_config_defaults(self):
        """Test render configuration with default values."""
        config = RenderConfig()

        assert config.resolution == (1920, 1080)
        assert config.frame_rate == 30
        assert config.quality == RenderQuality.MEDIUM
        assert config.format == RenderFormat.MP4

    def test_frame_rate_validation(self):
        """Test frame rate validation bounds."""
        # Valid frame rates
        RenderConfig(frame_rate=1)
        RenderConfig(frame_rate=60)
        RenderConfig(frame_rate=120)

        # Invalid frame rates
        with pytest.raises(ValidationError):
            RenderConfig(frame_rate=0)  # Too low

        with pytest.raises(ValidationError):
            RenderConfig(frame_rate=200)  # Too high


@pytest.mark.unit
class TestTimingConfig:
    """Test TimingConfig validation and behavior."""

    def test_valid_timing_config(self):
        """Test creating a valid timing configuration."""
        config = TimingConfig(
            mode=TimingMode.DRAFT,
            ui=0.8,
            events=0.6,
            effects=0.4,
            waits=0.3,
        )

        assert config.mode == TimingMode.DRAFT
        assert config.ui == 0.8
        assert config.events == 0.6
        assert config.effects == 0.4
        assert config.waits == 0.3

    def test_timing_config_defaults(self):
        """Test timing configuration with default values."""
        config = TimingConfig()

        assert config.mode == TimingMode.NORMAL
        assert config.ui == 1.0
        assert config.events == 0.8
        assert config.effects == 0.5
        assert config.waits == 0.5
        assert "draft" in config.multipliers
        assert config.multipliers["normal"] == 1.0

    def test_base_for_method(self):
        """Test the base_for timing calculation method."""
        config = TimingConfig(
            ui=2.0,
            events=1.5,
            effects=1.0,
            waits=0.5,
        )

        # Test UI action in normal mode
        assert config.base_for("show_grid", "normal") == 2.0

        # Test event action in draft mode (0.5x multiplier)
        assert config.base_for("enqueue_node", "draft") == 0.75  # 1.5 * 0.5

        # Test effect action in fast mode (0.25x multiplier)
        assert config.base_for("highlight_path", "fast") == 0.25  # 1.0 * 0.25

        # Test wait action
        assert config.base_for("pause", "normal") == 0.5

    def test_bucket_for_action_mapping(self):
        """Test action to timing bucket mapping."""
        config = TimingConfig()

        # UI actions
        assert config._bucket_for_action("show_grid") == "ui"
        assert config._bucket_for_action("hide_widget") == "ui"
        assert config._bucket_for_action("transition_scene") == "ui"

        # Event actions
        assert config._bucket_for_action("enqueue_node") == "events"
        assert config._bucket_for_action("dequeue_item") == "events"
        assert config._bucket_for_action("visit_neighbor") == "events"

        # Effect actions
        assert config._bucket_for_action("highlight_path") == "effects"
        assert config._bucket_for_action("animate_queue") == "effects"
        assert config._bucket_for_action("trace_algorithm") == "effects"

        # Wait actions
        assert config._bucket_for_action("wait_for_input") == "waits"
        assert config._bucket_for_action("pause_execution") == "waits"

        # Unknown actions default to ui
        assert config._bucket_for_action("unknown_action") == "ui"

    def test_timing_bounds_validation(self):
        """Test timing value bounds validation."""
        # Valid timing values
        TimingConfig(ui=0.1, events=10.0)

        # Invalid timing values
        with pytest.raises(ValidationError):
            TimingConfig(ui=0.05)  # Too small

        with pytest.raises(ValidationError):
            TimingConfig(events=15.0)  # Too large


@pytest.mark.unit
class TestVideoConfig:
    """Test VideoConfig validation and behavior."""

    def test_valid_video_config(self):
        """Test creating a valid video configuration."""
        scenario = ScenarioConfig(
            name="test",
            grid_file="test.yaml",
            start=(0, 0),
            goal=(5, 5),
        )

        config = VideoConfig(scenario=scenario)

        assert config.scenario == scenario
        assert isinstance(config.theme, ThemeConfig)
        assert isinstance(config.voiceover, VoiceoverConfig)
        assert isinstance(config.subtitles, SubtitlesConfig)
        assert isinstance(config.render, RenderConfig)
        assert isinstance(config.timing, TimingConfig)

    def test_video_config_with_custom_components(self):
        """Test video configuration with custom component configs."""
        scenario = ScenarioConfig(
            name="custom_test",
            grid_file="custom.yaml",
            start=(1, 1),
            goal=(8, 8),
        )

        theme = ThemeConfig(
            name="dark",
            colors={"visited": "#FFFFFF", "goal": "#FF0000"}
        )

        voiceover = VoiceoverConfig(enabled=True, speed=1.5)

        config = VideoConfig(
            scenario=scenario,
            theme=theme,
            voiceover=voiceover,
        )

        assert config.scenario.name == "custom_test"
        assert config.theme.name == "dark"
        assert config.voiceover.enabled is True
        assert config.voiceover.speed == 1.5
        # Defaults should still be applied for unspecified components
        assert config.subtitles.enabled is False
        assert config.render.quality == RenderQuality.MEDIUM

    def test_video_config_serialization(self):
        """Test video configuration serialization to dict."""
        scenario = ScenarioConfig(
            name="serialize_test",
            grid_file="serialize.yaml",
            start=(0, 0),
            goal=(3, 3),
        )

        config = VideoConfig(scenario=scenario)
        config_dict = config.model_dump()

        assert isinstance(config_dict, dict)
        assert config_dict["scenario"]["name"] == "serialize_test"
        assert config_dict["theme"]["name"] == "default"
        assert config_dict["timing"]["mode"] == "normal"
        assert config_dict["render"]["quality"] == "medium"
