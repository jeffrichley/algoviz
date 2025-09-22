"""Director orchestration component for ALGOViz.

The Director is the central conductor that executes storyboards, applies timing,
coordinates voiceover, routes algorithm events, and manages transitions.
"""

from typing import Any, Protocol

from agloviz.adapters.registry import AdapterRegistry
from agloviz.config.models import TimingConfig
from agloviz.config.timing import TimingTracker
from agloviz.core.errors import ConfigError
from agloviz.core.events import VizEvent
from agloviz.core.routing import RoutingMap, RoutingRegistry
from agloviz.core.storyboard import Act, Beat, Shot, Storyboard
from agloviz.widgets import component_registry


class ActionHandler(Protocol):
    """Protocol for storyboard action handlers."""
    def __call__(self, scene: Any, args: dict[str, Any], run_time: float, context: dict[str, Any]) -> None:
        """Execute the action with given parameters."""
        ...


class VoiceoverContext:
    """Scaffolded voiceover context manager for Phase 3."""
    def __init__(self, text: str, enabled: bool = False):
        self.text = text
        self.enabled = enabled
        self.duration = 0.0  # Will be set by TTS in Phase 3

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class DirectorError(ConfigError):
    """Errors during Director execution."""
    pass


class Director:
    """Central orchestration component for storyboard execution."""

    def __init__(
        self,
        scene: Any,
        storyboard: Storyboard,
        timing: TimingConfig,
        algorithm: str,
        *,
        mode: str = "normal",
        with_voice: bool = False,
        timing_tracker: TimingTracker | None = None
    ):
        self.scene = scene
        self.storyboard = storyboard
        self.timing = timing
        self.algorithm = algorithm
        self.mode = mode
        self.with_voice = with_voice
        self.timing_tracker = timing_tracker or TimingTracker()

        # Action registry for storyboard actions
        self._actions: dict[str, ActionHandler] = {}
        self._register_core_actions()

        # Widget instances cache (per shot lifecycle)
        self._active_widgets: dict[str, Any] = {}

    def _register_core_actions(self) -> None:
        """Register only generic orchestration actions (v2.0 compliance)."""
        self.core_actions = {
            "show_title": self._action_show_title,
            "show_widgets": self._action_show_widgets,
            "play_events": self._action_play_events,
            "outro": self._action_outro
        }
        self._actions.update(self.core_actions)

    def run(self) -> None:
        """Execute the complete storyboard."""
        for i_act, act in enumerate(self.storyboard.acts):
            self._enter_act(act, i_act)

            for i_shot, shot in enumerate(act.shots):
                self._enter_shot(shot, i_act, i_shot)

                for i_beat, beat in enumerate(shot.beats):
                    self._run_beat(beat, i_act, i_shot, i_beat)

                self._exit_shot(shot, i_act, i_shot)

            self._exit_act(act, i_act)

    def _run_beat(self, beat: Beat, ai: int, si: int, bi: int) -> None:
        """Execute a single beat with timing and voiceover."""
        import time

        # Get base timing from TimingConfig
        base_time = self.timing.base_for(beat.action, mode=self.mode)

        # Create execution context
        context = {"ai": ai, "si": si, "bi": bi, "algorithm": self.algorithm}

        def invoke_action(run_time: float) -> float:
            """Invoke the beat action and return actual duration."""
            start_time = time.time()

            handler = self._resolve_action(beat.action)
            handler(self.scene, beat.args, run_time, context)

            return time.time() - start_time

        # Handle voiceover context (scaffolded)
        if self.with_voice and beat.narration:
            with VoiceoverContext(beat.narration, enabled=self.with_voice) as voiceover:
                # Hybrid timing: max(base, narration_duration)
                run_time = max(base_time, voiceover.duration)

                # Apply duration overrides
                if beat.max_duration:
                    run_time = min(run_time, beat.max_duration)
                if beat.min_duration:
                    run_time = max(run_time, beat.min_duration)

                actual_time = invoke_action(run_time)
        else:
            run_time = base_time
            if beat.min_duration:
                run_time = max(run_time, beat.min_duration)
            if beat.max_duration:
                run_time = min(run_time, beat.max_duration)

            actual_time = invoke_action(run_time)

        # Log timing for analysis
        beat_name = f"{ai}-{si}-{bi}"
        self.timing_tracker.log(
            beat_name=beat_name,
            action=beat.action,
            expected=run_time,
            actual=actual_time,
            mode=self.mode,
            act=f"Act {ai+1}",
            shot=f"Shot {si+1}"
        )

    def _resolve_action(self, action_name: str) -> ActionHandler:
        """Resolve action name to callable handler."""
        if action_name not in self._actions:
            available = ", ".join(self._actions.keys())
            raise KeyError(f"Action '{action_name}' not registered. Available actions: {available}")
        return self._actions[action_name]

    # Action implementations
    def _action_show_title(self, scene: Any, args: dict[str, Any], run_time: float, context: dict[str, Any]) -> None:
        """Show title card action."""
        # Implementation will be added in rendering phase
        pass

    def _action_show_widgets(self, scene: Any, args: dict[str, Any], run_time: float, context: dict[str, Any]) -> None:
        """Show widgets action."""
        for widget_name, enabled in args.items():
            if enabled and isinstance(enabled, bool):
                try:
                    widget = component_registry.get(widget_name)
                    widget.show(scene)
                    self._active_widgets[widget_name] = widget
                    print(f"🎨 Showing widget: {widget_name}")
                except Exception as e:
                    print(f"⚠️ Widget '{widget_name}' not available: {e}")
                    # Continue with other widgets

    def _action_play_events(self, scene: Any, args: dict[str, Any], run_time: float, context: dict[str, Any]) -> None:
        """Play algorithm events with routing."""
        algorithm = context["algorithm"]

        try:
            # Get adapter and routing map
            adapter_class = AdapterRegistry.get(algorithm)
            adapter = adapter_class()
            routing_map = RoutingRegistry.get(algorithm)

            # Override routing if specified in args
            if "routing" in args and isinstance(args["routing"], dict):
                routing_map = args["routing"]

            # For Phase 1.4, we don't have real scenario integration yet
            # Just log that events would be played here
            print(f"🎬 Playing {algorithm} events (Phase 1.4 - mock implementation)")

            # Generate and route events
            # Note: This is a simplified version - full implementation will need scenario
            self._route_events(routing_map, [], run_time)

        except Exception as e:
            # For Phase 1.4, gracefully handle missing components
            print(f"⚠️ Play events not fully implemented yet: {e}")
            pass


    def _action_outro(self, scene: Any, args: dict[str, Any], run_time: float, context: dict[str, Any]) -> None:
        """Outro action."""
        # Implementation will be added in rendering phase
        print("👋 Outro - Thanks for watching!")
        pass

    def _route_events(self, routing_map: RoutingMap, events: list[VizEvent], base_run_time: float) -> None:
        """Route VizEvents to appropriate widget handlers."""
        event_timing = self.timing.base_for("events", mode=self.mode)

        for event in events:
            if event.type in routing_map:
                handlers = routing_map[event.type]

                for handler_name in handlers:
                    widget_name, action = handler_name.split(".", 1)

                    if widget_name in self._active_widgets:
                        widget = self._active_widgets[widget_name]
                        widget.update(self.scene, event, event_timing)

    def _enter_act(self, act: Act, index: int) -> None:
        """Handle act entry transition."""
        # Placeholder for act transitions
        pass

    def _exit_act(self, act: Act, index: int) -> None:
        """Handle act exit transition."""
        # Placeholder for act transitions
        pass

    def _enter_shot(self, shot: Shot, act_index: int, shot_index: int) -> None:
        """Handle shot entry transition."""
        # Clear previous shot widgets
        self._active_widgets.clear()

    def _exit_shot(self, shot: Shot, act_index: int, shot_index: int) -> None:
        """Handle shot exit transition."""
        # Hide all active widgets
        for widget in self._active_widgets.values():
            widget.hide(self.scene)
        self._active_widgets.clear()
