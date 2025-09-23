"""Director orchestration component for ALGOViz.

The Director is the central conductor that executes storyboards, applies timing,
coordinates voiceover, routes algorithm events, and manages transitions.
"""

from typing import Any, Protocol

from agloviz.config.models import SceneConfig, TimingConfig
from agloviz.config.timing import TimingTracker
from agloviz.core.errors import ConfigError
from agloviz.core.scene import SceneEngine
from agloviz.core.storyboard import Act, Beat, Shot, Storyboard


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
        storyboard: Storyboard,
        timing: TimingConfig,
        scene_config: SceneConfig,
        *,
        mode: str = "normal",
        with_voice: bool = False,
        timing_tracker: TimingTracker | None = None
    ):
        # Initialize SceneEngine from scene configuration
        self.scene_engine = SceneEngine(scene_config, timing)
        self.storyboard = storyboard
        self.timing = timing
        self.mode = mode
        self.with_voice = with_voice
        self.timing_tracker = timing_tracker or TimingTracker()

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

    def _run_beat(self, beat: Beat, act_index: int, shot_index: int, beat_index: int) -> None:
        """Execute a single beat - delegate ALL actions to SceneEngine."""
        import time

        # Get timing
        run_time = self.timing.base_for(beat.action, mode=self.mode)

        # Apply duration overrides
        if beat.min_duration:
            run_time = max(run_time, beat.min_duration)
        if beat.max_duration:
            run_time = min(run_time, beat.max_duration)

        # Create context
        context = {"act_index": act_index, "shot_index": shot_index, "beat_index": beat_index}

        # Handle voiceover timing
        if self.with_voice and beat.narration:
            with VoiceoverContext(beat.narration, enabled=self.with_voice) as voiceover:
                run_time = max(run_time, voiceover.duration)
                actual_time = self._execute_with_timing(beat, run_time, context)
        else:
            actual_time = self._execute_with_timing(beat, run_time, context)

        # Log timing
        beat_name = f"{act_index}-{shot_index}-{beat_index}"
        self.timing_tracker.log(
            beat_name, 
            beat.action, 
            run_time, 
            actual_time,
            mode=self.mode,
            act=f"Act {act_index}",
            shot=f"Shot {shot_index}"
        )

    def _execute_with_timing(self, beat: Beat, run_time: float, context: dict) -> float:
        """Execute beat with timing measurement."""
        import time

        start_time = time.time()

        # Delegate ALL action execution to SceneEngine
        self.scene_engine.execute_beat(beat, run_time, context)

        return time.time() - start_time


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
        # SceneEngine handles widget lifecycle
        pass

    def _exit_shot(self, shot: Shot, act_index: int, shot_index: int) -> None:
        """Handle shot exit transition."""
        # SceneEngine handles widget lifecycle
        pass
