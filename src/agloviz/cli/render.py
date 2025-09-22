"""Enhanced CLI commands with Director integration."""

from pathlib import Path

import typer
from rich.console import Console

from agloviz.config.manager import ConfigManager
from agloviz.config.models import TimingConfig
from agloviz.config.timing import TimingTracker
from agloviz.core.director import Director
from agloviz.core.storyboard import StoryboardLoader

console = Console()


def render_with_director(
    algorithm: str,
    scenario_path: Path,
    storyboard_path: Path | None = None,
    timing_mode: str = "normal",
    with_voice: bool = False,
    output_dir: Path = Path("renders/")
) -> None:
    """Render algorithm visualization using Director."""

    try:
        # Load configuration
        config_manager = ConfigManager()

        # For Phase 1.4, create a simple scenario config since full config loading isn't needed yet
        from agloviz.config.models import ScenarioConfig
        scenario_config = ScenarioConfig(
            name="test_scenario",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(5, 5)
        )

        timing_config = TimingConfig(mode=timing_mode)

        # Load storyboard (default to algorithm-specific if not provided)
        if storyboard_path is None:
            storyboard_path = Path(f"storyboards/{algorithm}_demo.yaml")

        # For Phase 1.4, create a simple storyboard if file doesn't exist
        try:
            storyboard_loader = StoryboardLoader()
            storyboard = storyboard_loader.load_from_yaml(str(storyboard_path))
        except FileNotFoundError:
            # Create a basic storyboard for testing
            from agloviz.core.storyboard import Act, Beat, Shot, Storyboard
            beats = [
                Beat(action="show_title", args={"text": f"{algorithm.upper()} Demo"}),
                Beat(action="show_grid"),
                Beat(action="show_widgets", args={"queue": True}),
                Beat(action="play_events"),
                Beat(action="outro")
            ]
            shot = Shot(beats=beats)
            act = Act(title="Algorithm Demo", shots=[shot])
            storyboard = Storyboard(acts=[act])

        # Create timing tracker
        timing_tracker = TimingTracker()

        # Create mock scene for Phase 1.4 (will be replaced with Manim scene in Phase 1.5)
        class MockScene:
            def __init__(self):
                self.objects = []

            def add(self, obj):
                self.objects.append(obj)
                console.print(f"🎭 Mock scene: Added object {type(obj).__name__}")

            def remove(self, obj):
                if obj in self.objects:
                    self.objects.remove(obj)
                    console.print(f"🎭 Mock scene: Removed object {type(obj).__name__}")

            def play(self, *animations, run_time=1.0):
                console.print(f"🎭 Mock scene: Playing {len(animations)} animations (run_time={run_time}s)")

            def wait(self, duration=1.0):
                console.print(f"🎭 Mock scene: Waiting {duration}s")

        scene = MockScene()

        # Create and run Director
        director = Director(
            scene=scene,
            storyboard=storyboard,
            timing=timing_config,
            algorithm=algorithm,
            mode=timing_mode,
            with_voice=with_voice,
            timing_tracker=timing_tracker
        )

        console.print(f"🎬 Starting {algorithm} visualization...")
        director.run()
        console.print("✅ Director execution completed")

        # Export timing data
        output_dir.mkdir(parents=True, exist_ok=True)
        timing_tracker.export_csv(output_dir / "timing_report.csv")
        timing_tracker.export_json(output_dir / "timing_report.json")

        console.print(f"📊 Timing reports exported to {output_dir}")

    except Exception as e:
        console.print(f"❌ Render failed: {e}")
        raise typer.Exit(1)
