#!/usr/bin/env python3
"""Pure Hydra-zen CLI - Following Documentation Pattern Exactly

This demonstrates the proper hydra-zen approach from the documentation:
https://mit-ll-responsible-ai.github.io/hydra-zen/

No Typer, no manual config management, no complex store handling.
Just pure hydra-zen as intended.
"""

from typing import Any

from hydra_zen import builds, store, zen
from rich.console import Console
from rich.panel import Panel

from agloviz.config.models import SceneConfig
from agloviz.config.store_manager import StoreManager

from ..config.models import ScenarioConfig, ThemeConfig, TimingConfig, TimingMode
from ..rendering.config import RenderConfig, RenderFormat, RenderQuality

# Import our components
from ..rendering.renderer import SimpleRenderer

console = Console()


def render_algorithm_video(
    algorithm: str,
    renderer: SimpleRenderer,
    scenario: ScenarioConfig,  # Must match hydra_defaults key
    theme: ThemeConfig,  # Must match hydra_defaults key
    timing: TimingConfig,  # Must match hydra_defaults key
    scene: SceneConfig,  # Scene config instantiated by zen().hydra_main()
    output_path: str = "output.mp4",
) -> dict[str, Any]:
    """Main render function - receives fully instantiated objects from hydra-zen.

    This is the pure business logic. Hydra-zen handles all configuration
    management, instantiation, and CLI generation automatically.
    """
    console.print(
        Panel(
            f"🎬 Rendering [bold cyan]{algorithm}[/] with Pure Hydra-zen",
            title="ALGOViz",
        )
    )

    console.print("✨ All objects automatically instantiated by hydra-zen!")
    quality = (
        renderer.config.quality.value
        if hasattr(renderer.config.quality, "value")
        else renderer.config.quality
    )
    console.print(f"📊 Renderer: {quality} @ {renderer.config.resolution}")
    console.print(f"🗺️  Scenario: {scenario.name} ({scenario.grid_size})")
    console.print(f"🎨 Theme: {theme.name}")
    mode = timing.mode.value if hasattr(timing.mode, "value") else timing.mode
    console.print(f"⏱️  Timing: {mode}")
    console.print(f"🚀 Output: [bold green]{output_path}[/]")

    # Scene config is already instantiated by zen().hydra_main()!
    console.print(f"🎬 Scene: {scene.name} with {len(scene.widgets)} widgets")
    console.print(f"   Widgets: {list(scene.widgets.keys())}")

    # All objects are already instantiated by hydra-zen!
    result = renderer.render_algorithm_video(
        algorithm=algorithm,
        scenario_config=scenario,
        scene_config=scene,
        theme_config=theme,
        timing_config=timing,
        output_path=output_path,
    )

    console.print(
        Panel(
            f"✅ Video rendered successfully!\n"
            f"📁 Output: {output_path}\n"
            f"⏱️  Duration: {result.get('duration', 'N/A')}s\n"
            f"📊 Resolution: {result.get('resolution', 'N/A')}\n"
            f"🎯 Algorithm: {algorithm}",
            title="[green]Render Complete[/]",
        )
    )

    return result


# =====================================================================
# HYDRA-ZEN CONFIGURATION - Following Documentation Pattern
# =====================================================================

# Create renderer configurations using builds()
DraftRenderer = builds(
    SimpleRenderer,
    render_config=builds(
        RenderConfig,
        quality=RenderQuality.DRAFT,
        resolution=(854, 480),
        frame_rate=15,
        format=RenderFormat.MP4,
    ),
)

MediumRenderer = builds(
    SimpleRenderer,
    render_config=builds(
        RenderConfig,
        quality=RenderQuality.MEDIUM,
        resolution=(1280, 720),
        frame_rate=30,
        format=RenderFormat.MP4,
    ),
)

HDRenderer = builds(
    SimpleRenderer,
    render_config=builds(
        RenderConfig,
        quality=RenderQuality.HIGH,
        resolution=(1920, 1080),
        frame_rate=60,
        format=RenderFormat.MP4,
    ),
)

# Create scenario configurations
MazeSmallConfig = builds(
    ScenarioConfig,
    name="maze_small",
    obstacles=[(1, 1), (2, 2), (3, 1)],
    start=(0, 0),
    goal=(9, 9),
    grid_size=(10, 10),
)

MazeLargeConfig = builds(
    ScenarioConfig,
    name="maze_large",
    obstacles=[(1, 1), (2, 2), (3, 1), (5, 5)],
    start=(0, 0),
    goal=(19, 19),
    grid_size=(20, 20),
)

# Create theme configurations
DefaultThemeConfig = builds(ThemeConfig, name="default")
DarkThemeConfig = builds(
    ThemeConfig,
    name="dark",
    colors={
        "visited": "#BB86FC",
        "frontier": "#03DAC6",
        "goal": "#CF6679",
        "path": "#FF9800",
        "obstacle": "#1F1B24",
        "grid": "#2D2D2D",
    },
)

# Create timing configurations
NormalTimingConfig = builds(TimingConfig, mode=TimingMode.NORMAL)
FastTimingConfig = builds(TimingConfig, mode=TimingMode.FAST)

# Import scene configs from centralized hydra_zen.py

# Store configurations - using centralized StoreManager

# Setup all stores through the centralized manager
StoreManager.setup_store()

# Configure the main function with defaults
store(
    render_algorithm_video,
    algorithm="bfs",  # Default algorithm
    output_path="pure_zen_output.mp4",  # Default output
    hydra_defaults=[
        "_self_",
        {"renderer": "medium"},  # Default to medium quality
        {"scenario": "maze_small"},  # Default scenario
        {"theme": "default"},  # Default theme
        {"timing": "normal"},  # Default timing
        {"scene": "bfs_basic"},  # Default scene (updated to match registered configs)
    ],
    name="main",
)


def main():
    """Entry point for the pure hydra-zen CLI."""
    print("🚀 ALGOViz Pure Hydra-zen CLI")
    print("Following hydra-zen documentation pattern exactly")
    print("=" * 60)

    # Add all configurations to Hydra store
    store.add_to_hydra_store()

    # Create CLI using zen().hydra_main() - this replaces ALL our manual code!
    zen(render_algorithm_video).hydra_main(
        config_name="main", config_path=None, version_base="1.3"
    )


if __name__ == "__main__":
    main()

    # This automatically creates a CLI that supports:
    #
    # Basic usage:
    # python render_pure_zen.py                           # Uses all defaults
    # python render_pure_zen.py --help                    # Rich help
    # python render_pure_zen.py --config-help             # Show config structure
    #
    # Simple overrides:
    # python render_pure_zen.py algorithm=dfs             # Change algorithm
    # python render_pure_zen.py renderer=hd               # Use HD quality
    # python render_pure_zen.py scenario=maze_large       # Large maze
    # python render_pure_zen.py theme=dark                # Dark theme
    # python render_pure_zen.py timing=fast               # Fast timing
    # python render_pure_zen.py output_path=my_video.mp4  # Custom output
    #
    # Deep overrides (automatic!):
    # python render_pure_zen.py renderer.render_config.resolution=[1920,1080]
    # python render_pure_zen.py renderer.render_config.frame_rate=60
    # python render_pure_zen.py scenario_config.start=[2,2]
    #
    # Multi-run experiments (automatic!):
    # python render_pure_zen.py --multirun renderer=draft,medium,hd
    # python render_pure_zen.py --multirun algorithm=bfs,dfs scenario=maze_small,maze_large
    #
    # All the functionality from our 288-line render_app.py is now automatic!
