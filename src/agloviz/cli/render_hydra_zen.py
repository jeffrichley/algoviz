"""ALGOViz Render CLI - Proper Hydra-zen Implementation.

This replaces render_app.py with a proper hydra-zen approach that eliminates:
- Manual ConfigStore management
- Manual config loading and instantiation  
- Manual override parsing
- Most Typer CLI code

Based on hydra-zen best practices: https://mit-ll-responsible-ai.github.io/hydra-zen/
"""

from typing import Any, Dict
from pathlib import Path
from hydra_zen import builds, store, zen
from rich.console import Console
from rich.panel import Panel

# Import our actual components
from agloviz.rendering.renderer import SimpleRenderer
from agloviz.rendering.config import RenderConfig, RenderQuality, RenderFormat
from agloviz.config.models import ScenarioConfig, ThemeConfig, TimingConfig, TimingMode

console = Console()


def render_algorithm_video(
    algorithm: str,
    renderer: SimpleRenderer,
    scenario_config: ScenarioConfig,
    theme_config: ThemeConfig, 
    timing_config: TimingConfig,
    output_path: str = "output.mp4"
) -> Dict[str, Any]:
    """Main render function - hydra-zen instantiates everything automatically!
    
    This replaces ALL the manual work in render_app.py:
    - No setup_configstore() calls
    - No _load_config_from_store() calls  
    - No manual instantiate() calls
    - No manual override parsing
    - No Typer CLI boilerplate
    
    Everything is handled automatically by hydra-zen!
    """
    console.print(Panel(f"🎬 Rendering [bold cyan]{algorithm}[/] with hydra-zen", title="ALGOViz Render"))
    
    console.print("✨ All configs automatically instantiated by hydra-zen!")
    console.print(f"📊 Renderer: {renderer.config.quality.value} @ {renderer.config.resolution}")
    console.print(f"🗺️  Scenario: {scenario_config.name}")
    console.print(f"🎨 Theme: {theme_config.name}")
    console.print(f"⏱️  Timing: {timing_config.mode.value}")
    console.print(f"🚀 Output: [bold green]{output_path}[/]")
    
    # Create scene config from our existing scene system
    from agloviz.core.scene import SceneEngine
    
    # For now, create a basic scene config - this would be enhanced later
    scene_config = {
        "name": f"{algorithm}_pathfinding",
        "algorithm": algorithm,
        "widgets": {
            "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
            "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
        }
    }
    
    # All objects are already instantiated by hydra-zen!
    result = renderer.render_algorithm_video(
        algorithm=algorithm,
        scenario_config=scenario_config,
        scene_config=scene_config,
        theme_config=theme_config,
        timing_config=timing_config,
        output_path=output_path
    )
    
    console.print(Panel(
        f"✅ Video rendered successfully!\n"
        f"📁 Output: {output_path}\n"
        f"⏱️  Duration: {result.get('duration', 'N/A')}s\n"
        f"📊 Resolution: {result.get('resolution', 'N/A')}\n"
        f"🎯 Algorithm: {algorithm}",
        title="[green]Render Complete[/]"
    ))
    
    return result


def preview_algorithm(
    algorithm: str,
    scenario_config: ScenarioConfig,
    frames: int = 120,
    output_path: str = "preview.mp4"
) -> Dict[str, Any]:
    """Preview function - also gets automatic hydra-zen instantiation."""
    console.print(Panel(f"👀 Previewing [bold cyan]{algorithm}[/] ({frames} frames)", title="Quick Preview"))
    
    from agloviz.rendering.renderer import create_preview_renderer
    renderer = create_preview_renderer(max_frames=frames)
    result = renderer.render_preview(algorithm, scenario_config.name, output_path)
    
    console.print(Panel(
        f"✅ Preview rendered!\n"
        f"📁 Output: {output_path}\n" 
        f"🎞️  Frames: {frames}\n"
        f"⚡ Mode: Draft quality",
        title="[green]Preview Complete[/]"
    ))
    
    return result


# =====================================================================
# HYDRA-ZEN CONFIGURATION - Replaces all our manual config management
# =====================================================================

# 1. Create renderer configurations using builds() - replaces manual ConfigStore
DraftRenderer = builds(
    SimpleRenderer,
    render_config=builds(
        RenderConfig,
        quality=RenderQuality.DRAFT,
        resolution=(854, 480),
        frame_rate=15,
        format=RenderFormat.MP4
    )
)

MediumRenderer = builds(
    SimpleRenderer,
    render_config=builds(
        RenderConfig,
        quality=RenderQuality.MEDIUM,
        resolution=(1280, 720), 
        frame_rate=30,
        format=RenderFormat.MP4
    )
)

HDRenderer = builds(
    SimpleRenderer,
    render_config=builds(
        RenderConfig,
        quality=RenderQuality.HIGH,
        resolution=(1920, 1080),
        frame_rate=60,
        format=RenderFormat.MP4
    )
)

# 2. Create scenario configurations
MazeSmall = builds(ScenarioConfig, name="maze_small", obstacles=[(1, 1), (2, 2)], start=(0, 0), goal=(9, 9))
MazeLarge = builds(ScenarioConfig, name="maze_large", obstacles=[(1, 1), (2, 2)], start=(0, 0), goal=(19, 19))

# 3. Create theme configurations  
DefaultTheme = builds(ThemeConfig, name="default")
DarkTheme = builds(ThemeConfig, name="dark", colors={"visited": "#BB86FC", "frontier": "#03DAC6"})

# 4. Create timing configurations
NormalTiming = builds(TimingConfig, mode=TimingMode.NORMAL)
FastTiming = builds(TimingConfig, mode=TimingMode.FAST)

# 5. Store all configurations - this replaces our entire ConfigStore system
renderer_store = store(group="renderer")
renderer_store(DraftRenderer, name="draft")
renderer_store(MediumRenderer, name="medium")
renderer_store(HDRenderer, name="hd")

scenario_store = store(group="scenario")
scenario_store(MazeSmall, name="maze_small")
scenario_store(MazeLarge, name="maze_large")

theme_store = store(group="theme")
theme_store(DefaultTheme, name="default")
theme_store(DarkTheme, name="dark")

timing_store = store(group="timing")
timing_store(NormalTiming, name="normal")
timing_store(FastTiming, name="fast")

# 6. Configure main functions with defaults
video_store = store(group="app")
video_store(
    render_algorithm_video,
    algorithm="bfs",
    output_path="output.mp4",
    hydra_defaults=[
        "_self_",
        {"renderer": "medium"},
        {"scenario": "maze_small"},
        {"theme": "default"},
        {"timing": "normal"}
    ],
    name="video"
)

preview_store = store(group="app")
preview_store(
    preview_algorithm,
    algorithm="bfs",
    frames=120,
    output_path="preview.mp4",
    hydra_defaults=[
        "_self_",
        {"scenario": "maze_small"}
    ],
    name="preview"
)


if __name__ == "__main__":
    # Add all configurations to Hydra store
    store.add_to_hydra_store()
    
    # Create CLI using zen().hydra_main() - replaces ALL our Typer code!
    zen(render_algorithm_video).hydra_main(
        config_name="app/video",
        config_path=None,
        version_base="1.3"
    )
    
    # This automatically creates a CLI that supports:
    #
    # Basic usage:
    # python render_hydra_zen.py                           # All defaults
    # python render_hydra_zen.py --help                    # Rich help
    #
    # Simple overrides:
    # python render_hydra_zen.py algorithm=dfs             # Change algorithm
    # python render_hydra_zen.py renderer=hd               # HD quality
    # python render_hydra_zen.py scenario=maze_large       # Large maze
    # python render_hydra_zen.py theme=dark                # Dark theme
    # python render_hydra_zen.py timing=fast               # Fast timing
    # python render_hydra_zen.py output_path=my_video.mp4  # Custom output
    #
    # Deep overrides (nested config changes):
    # python render_hydra_zen.py renderer.render_config.resolution=[1920,1080]
    # python render_hydra_zen.py renderer.render_config.frame_rate=60
    # python render_hydra_zen.py scenario_config.start=[2,2]
    #
    # Multiple overrides:
    # python render_hydra_zen.py algorithm=dfs renderer=hd scenario=maze_large theme=dark
    #
    # All the CLI functionality, config loading, instantiation, and override 
    # handling from our 288-line render_app.py is now automatic!
