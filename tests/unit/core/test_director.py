"""Tests for Director orchestration component."""

from unittest.mock import Mock

import pytest

from agloviz.config.models import TimingConfig
from agloviz.config.timing import TimingTracker
from agloviz.core.director import Director, VoiceoverContext
from agloviz.core.storyboard import Act, Beat, Shot, Storyboard


@pytest.mark.unit
class TestDirector:
    """Test Director functionality."""

    def test_director_initialization(self):
        """Test Director initialization with required components."""
        scene = Mock()
        storyboard = Mock(spec=Storyboard)
        timing = TimingConfig()

        director = Director(
            scene=scene,
            storyboard=storyboard,
            timing=timing,
            algorithm="bfs"
        )

        assert director.scene == scene
        assert director.storyboard == storyboard
        assert director.timing == timing
        assert director.algorithm == "bfs"
        assert director.mode == "normal"
        assert not director.with_voice

    def test_beat_execution_with_timing(self):
        """Test beat execution applies correct timing."""
        scene = Mock()
        beat = Beat(action="show_title", args={"text": "Test"})
        timing = TimingConfig(ui=1.0)

        director = Director(
            scene=scene,
            storyboard=Mock(),
            timing=timing,
            algorithm="bfs"
        )

        # Mock the action handler
        director._actions["show_title"] = Mock()

        director._run_beat(beat, 0, 0, 0)

        # Verify action was called with correct timing
        director._actions["show_title"].assert_called_once()
        call_args = director._actions["show_title"].call_args
        assert call_args[0][2] == 1.0  # run_time parameter

    def test_voiceover_context_scaffolding(self):
        """Test voiceover context manager scaffolding."""
        with VoiceoverContext("Test narration", enabled=False) as ctx:
            assert ctx.text == "Test narration"
            assert not ctx.enabled
            assert ctx.duration == 0.0

    def test_hybrid_timing_with_voiceover(self):
        """Test hybrid timing when voiceover is enabled."""
        scene = Mock()
        beat = Beat(
            action="show_title",
            args={"text": "Test"},
            narration="This is a test"
        )
        timing = TimingConfig(ui=1.0)

        director = Director(
            scene=scene,
            storyboard=Mock(),
            timing=timing,
            algorithm="bfs",
            with_voice=True
        )

        director._actions["show_title"] = Mock()

        # Mock voiceover context with longer duration
        original_context = VoiceoverContext

        class MockVoiceoverContext:
            def __init__(self, text, enabled=False):
                self.text = text
                self.enabled = enabled
                self.duration = 2.5  # Longer than base timing

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        # Temporarily replace VoiceoverContext
        import agloviz.core.director
        agloviz.core.director.VoiceoverContext = MockVoiceoverContext

        try:
            director._run_beat(beat, 0, 0, 0)

            # Verify hybrid timing used longer duration
            call_args = director._actions["show_title"].call_args
            assert call_args[0][2] == 2.5  # Should use voiceover duration
        finally:
            # Restore original
            agloviz.core.director.VoiceoverContext = original_context

    def test_action_resolution_error(self):
        """Test error handling for unknown actions."""
        scene = Mock()
        storyboard = Mock()
        timing = TimingConfig()

        director = Director(
            scene=scene,
            storyboard=storyboard,
            timing=timing,
            algorithm="generic"
        )

        with pytest.raises(KeyError) as exc_info:
            director._resolve_action("unknown_action")

        assert "unknown_action" in str(exc_info.value)
        assert "Available actions" in str(exc_info.value)



    def test_generic_actions_available(self):
        """Test that generic orchestration actions are available."""
        scene = Mock()
        storyboard = Mock()
        timing = TimingConfig()

        director = Director(
            scene=scene,
            storyboard=storyboard,
            timing=timing,
            algorithm="generic"
        )

        # Test that generic actions are registered
        generic_actions = [
            "show_title", "show_grid", "show_widgets",
            "play_events", "outro"
        ]

        for action in generic_actions:
            handler = director._resolve_action(action)
            assert callable(handler)
            assert action in director._actions

    def test_widget_lifecycle_management(self):
        """Test widget show/hide lifecycle during shots."""
        scene = Mock()
        shot = Mock()

        director = Director(
            scene=scene,
            storyboard=Mock(),
            timing=TimingConfig(),
            algorithm="bfs"
        )

        # Mock active widgets
        mock_widget = Mock()
        director._active_widgets["test_widget"] = mock_widget

        director._exit_shot(shot, 0, 0)

        # Verify widget was hidden
        mock_widget.hide.assert_called_once_with(scene)
        assert "test_widget" not in director._active_widgets

    def test_timing_tracker_integration(self):
        """Test timing tracker records beat execution."""
        scene = Mock()
        beat = Beat(action="show_title", args={"text": "Test"})
        timing = TimingConfig()
        tracker = Mock(spec=TimingTracker)

        director = Director(
            scene=scene,
            storyboard=Mock(),
            timing=timing,
            algorithm="bfs",
            timing_tracker=tracker
        )

        director._actions["show_title"] = Mock()
        director._run_beat(beat, 1, 2, 3)

        # Verify timing was logged
        tracker.log.assert_called_once()
        call_args = tracker.log.call_args[1]
        assert call_args["beat_name"] == "1-2-3"
        assert call_args["action"] == "show_title"
        assert call_args["mode"] == "normal"

    def test_show_grid_action(self):
        """Test show_grid action creates and manages grid widget."""
        scene = Mock()
        timing = TimingConfig()

        director = Director(
            scene=scene,
            storyboard=Mock(),
            timing=timing,
            algorithm="bfs"
        )

        # Mock component registry
        from agloviz.widgets import component_registry
        mock_widget = Mock()
        original_get = component_registry.get
        component_registry.get = Mock(return_value=mock_widget)

        try:
            director._action_show_grid(scene, {}, 1.0, {})

            # Verify widget was retrieved and shown
            component_registry.get.assert_called_once_with("grid")
            mock_widget.show.assert_called_once_with(scene)
            assert director._active_widgets["grid"] == mock_widget
        finally:
            component_registry.get = original_get

    def test_show_widgets_action(self):
        """Test show_widgets action manages multiple widgets."""
        scene = Mock()
        timing = TimingConfig()

        director = Director(
            scene=scene,
            storyboard=Mock(),
            timing=timing,
            algorithm="bfs"
        )

        # Mock component registry
        from agloviz.widgets import component_registry
        mock_queue_widget = Mock()
        mock_hud_widget = Mock()

        def mock_get(name):
            if name == "queue":
                return mock_queue_widget
            elif name == "hud":
                return mock_hud_widget
            else:
                raise KeyError(f"Widget '{name}' not found")

        original_get = component_registry.get
        component_registry.get = mock_get

        try:
            args = {"queue": True, "hud": True, "legend": False}
            director._action_show_widgets(scene, args, 1.0, {})

            # Verify enabled widgets were shown
            mock_queue_widget.show.assert_called_once_with(scene)
            mock_hud_widget.show.assert_called_once_with(scene)

            assert director._active_widgets["queue"] == mock_queue_widget
            assert director._active_widgets["hud"] == mock_hud_widget
            assert "legend" not in director._active_widgets
        finally:
            component_registry.get = original_get

    def test_duration_overrides(self):
        """Test min_duration and max_duration overrides."""
        scene = Mock()
        beat = Beat(
            action="show_title",
            args={"text": "Test"},
            min_duration=2.0,
            max_duration=3.0
        )
        timing = TimingConfig(ui=1.0)  # Base timing less than min

        director = Director(
            scene=scene,
            storyboard=Mock(),
            timing=timing,
            algorithm="bfs"
        )

        director._actions["show_title"] = Mock()
        director._run_beat(beat, 0, 0, 0)

        # Verify min_duration was applied
        call_args = director._actions["show_title"].call_args
        assert call_args[0][2] == 2.0  # Should use min_duration

    def test_context_information(self):
        """Test that context information is passed to actions."""
        scene = Mock()
        beat = Beat(action="show_title", args={"text": "Test"})
        timing = TimingConfig()

        director = Director(
            scene=scene,
            storyboard=Mock(),
            timing=timing,
            algorithm="bfs"
        )

        director._actions["show_title"] = Mock()
        director._run_beat(beat, 1, 2, 3)

        # Verify context was passed correctly
        call_args = director._actions["show_title"].call_args
        context = call_args[0][3]
        assert context["ai"] == 1
        assert context["si"] == 2
        assert context["bi"] == 3
        assert context["algorithm"] == "bfs"


@pytest.mark.integration
class TestDirectorIntegration:
    """Integration tests for Director with real components."""

    def test_full_storyboard_execution(self):
        """Test complete storyboard execution flow."""
        # Create minimal storyboard with generic actions only
        beat1 = Beat(action="show_title", args={"text": "Test Title"})
        beat2 = Beat(action="show_widgets", args={"hud": True})
        beat3 = Beat(action="outro", args={"text": "Thanks"})
        shot = Shot(beats=[beat1, beat2, beat3])
        act = Act(title="Test Act", shots=[shot])
        storyboard = Storyboard(acts=[act])

        scene = Mock()
        timing = TimingConfig()

        director = Director(
            scene=scene,
            storyboard=storyboard,
            timing=timing,
            algorithm="generic"
        )

        # Run director
        director.run()

        # Verify execution completed without errors
        assert len(director.timing_tracker.records) == 3

    def test_real_timing_config_integration(self):
        """Test Director with real TimingConfig."""
        from agloviz.config.models import TimingConfig

        beat = Beat(action="show_title", args={"text": "Test"})
        timing = TimingConfig(mode="draft", ui=2.0)

        scene = Mock()
        director = Director(
            scene=scene,
            storyboard=Mock(),
            timing=timing,
            algorithm="bfs",
            mode="draft"
        )

        director._actions["show_title"] = Mock()
        director._run_beat(beat, 0, 0, 0)

        # Verify draft mode multiplier was applied (0.5 * 2.0 = 1.0)
        call_args = director._actions["show_title"].call_args
        expected_time = timing.base_for("show_title", mode="draft")
        assert call_args[0][2] == expected_time

    def test_error_propagation(self):
        """Test that action errors are properly propagated."""
        scene = Mock()
        beat = Beat(action="failing_action")
        timing = TimingConfig()

        director = Director(
            scene=scene,
            storyboard=Mock(),
            timing=timing,
            algorithm="bfs"
        )

        # Register a failing action
        def failing_handler(scene, args, run_time, context):
            raise ValueError("Test error")

        director._actions["failing_action"] = failing_handler

        # Verify error propagates
        with pytest.raises(ValueError, match="Test error"):
            director._run_beat(beat, 0, 0, 0)
