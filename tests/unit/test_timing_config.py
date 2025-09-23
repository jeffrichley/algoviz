"""Tests for TimingConfig bucket resolution and base_for method."""

from agloviz.config.models import TimingConfig, TimingMode


class TestTimingConfig:
    """Test TimingConfig bucket resolution and timing calculations."""

    def test_timing_config_defaults(self):
        """Test TimingConfig default values."""
        config = TimingConfig()

        assert config.mode == TimingMode.NORMAL
        assert config.ui == 1.0
        assert config.events == 0.8
        assert config.effects == 0.5
        assert config.waits == 0.5
        assert config.multipliers == {"draft": 0.5, "normal": 1.0, "fast": 0.25}

    def test_bucket_for_action_ui_actions(self):
        """Test bucket resolution for UI actions."""
        config = TimingConfig()

        ui_actions = ["show_title", "show_grid", "hide_grid", "show_widgets", "hide_widgets"]
        for action in ui_actions:
            assert config._bucket_for_action(action) == "ui"

    def test_bucket_for_action_event_actions(self):
        """Test bucket resolution for event actions."""
        config = TimingConfig()

        event_actions = ["place_start", "place_goal", "visit_node", "add_to_queue", "remove_from_queue"]
        for action in event_actions:
            assert config._bucket_for_action(action) == "events"

    def test_bucket_for_action_effect_actions(self):
        """Test bucket resolution for effect actions."""
        config = TimingConfig()

        effect_actions = ["highlight", "animate_path", "fade_out", "pulse"]
        for action in effect_actions:
            assert config._bucket_for_action(action) == "effects"

    def test_bucket_for_action_unknown_actions(self):
        """Test bucket resolution for unknown actions defaults to ui."""
        config = TimingConfig()

        unknown_actions = ["unknown_action", "random_action", "test_action"]
        for action in unknown_actions:
            assert config._bucket_for_action(action) == "ui"

    def test_base_for_normal_mode(self):
        """Test base_for calculation in normal mode."""
        config = TimingConfig(mode=TimingMode.NORMAL)

        # Normal mode has 1.0 multiplier
        assert config.base_for("show_title") == 1.0  # ui * 1.0
        assert config.base_for("visit_node") == 0.8  # events * 1.0
        assert config.base_for("highlight") == 0.5   # effects * 1.0

    def test_base_for_draft_mode(self):
        """Test base_for calculation in draft mode."""
        config = TimingConfig(mode=TimingMode.DRAFT)

        # Draft mode has 0.5 multiplier
        assert config.base_for("show_title") == 0.5  # ui * 0.5
        assert config.base_for("visit_node") == 0.4  # events * 0.5
        assert config.base_for("highlight") == 0.25  # effects * 0.5

    def test_base_for_fast_mode(self):
        """Test base_for calculation in fast mode."""
        config = TimingConfig(mode=TimingMode.FAST)

        # Fast mode has 0.25 multiplier
        assert config.base_for("show_title") == 0.25  # ui * 0.25
        assert config.base_for("visit_node") == 0.2   # events * 0.25
        assert config.base_for("highlight") == 0.125  # effects * 0.25

    def test_base_for_with_mode_override(self):
        """Test base_for with explicit mode override."""
        config = TimingConfig(mode=TimingMode.NORMAL)

        # Override to draft mode
        assert config.base_for("show_title", mode="draft") == 0.5  # ui * 0.5
        assert config.base_for("visit_node", mode="fast") == 0.2   # events * 0.25

    def test_custom_timing_values(self):
        """Test base_for with custom timing values."""
        config = TimingConfig(
            ui=2.0,
            events=1.5,
            effects=1.0,
            waits=0.8
        )

        assert config.base_for("show_title") == 2.0   # ui * 1.0
        assert config.base_for("visit_node") == 1.5   # events * 1.0
        assert config.base_for("highlight") == 1.0    # effects * 1.0

    def test_custom_multipliers(self):
        """Test base_for with custom multipliers."""
        config = TimingConfig(
            multipliers={"draft": 0.3, "normal": 1.2, "fast": 0.1}
        )

        assert config.base_for("show_title", mode="draft") == 0.3  # ui * 0.3
        assert config.base_for("show_title", mode="normal") == 1.2  # ui * 1.2
        assert config.base_for("show_title", mode="fast") == 0.1   # ui * 0.1
