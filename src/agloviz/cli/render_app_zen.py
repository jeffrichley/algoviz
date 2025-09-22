"""Proper Hydra-zen CLI Implementation.

This demonstrates how to use hydra-zen's native capabilities for automatic:
- CLI generation with zen().hydra_main()
- Config instantiation
- Override handling
- ConfigStore management

Based on hydra-zen documentation: https://mit-ll-responsible-ai.github.io/hydra-zen/
"""

from pathlib import Path
from typing import Any, Dict

from hydra_zen import builds, store, zen, just
from rich.console import Console
from rich.panel import Panel

# Import our core components
from agloviz.rendering.renderer import SimpleRenderer
from agloviz.rendering.config import RenderConfig
from agloviz.core.scene import SceneEngine

console = Console()


def render_algorithm_video(
    algorithm: str,
    renderer: SimpleRenderer,
    scene_engine: SceneEngine,
    scenario_config: Any,
    theme_config: Any,
    timing_config: Any,
    output_path: str = "output.mp4"
) -> Dict[str, Any]:
    """Main render function that hydra-zen will call with instantiated configs.
    
    This function receives fully instantiated objects from hydra-zen,
    eliminating all the manual instantiation we were doing before.
    """
    console.print(Panel(f"🎬 Rendering [bold cyan]{algorithm}[/] visualization", title="ALGOViz Render"))
    
    console.print("🎥 Using hydra-zen instantiated components...")
    console.print(f"🚀 Rendering video to: [bold green]{output_path}[/]")
    
    # All objects are already instantiated by hydra-zen!
    result = renderer.render_algorithm_video(
        algorithm=algorithm,
        scenario_config=scenario_config,
        scene_config=scene_engine.scene_config,
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
    scenario_config: Any,
    frames: int = 120,
    output_path: str = "preview.mp4"
) -> Dict[str, Any]:
    """Preview render function with hydra-zen instantiation."""
    console.print(Panel(f"👀 Previewing [bold cyan]{algorithm}[/] ({frames} frames)", title="Quick Preview"))
    
    from agloviz.rendering.renderer import create_preview_renderer
    renderer = create_preview_renderer(max_frames=frames)
    result = renderer.render_preview(algorithm, "maze_small", output_path)
    
    console.print(Panel(
        f"✅ Preview rendered!\n"
        f"📁 Output: {output_path}\n" 
        f"🎞️  Frames: {frames}\n"
        f"⚡ Mode: Draft quality",
        title="[green]Preview Complete[/]"
    ))
    
    return result


# =====================================================================
# HYDRA-ZEN CONFIGURATION SETUP
# =====================================================================

# Create hydra-zen store for our configurations
render_store = store(group="app")

# 1. Configure the main render function with defaults
render_store(
    render_algorithm_video,
    algorithm="bfs",  # Default algorithm
    output_path="output.mp4",  # Default output
    hydra_defaults=[
        "_self_",
        {"renderer": "medium"},      # Default to medium quality renderer
        {"scene": "bfs_pathfinding"}, # Default scene config
        {"scenario": "maze_small"},   # Default scenario
        {"theme": "default"},         # Default theme
        {"timing": "normal"},         # Default timing
    ],
    name="video"
)

# 2. Configure the preview function
render_store(
    preview_algorithm,
    algorithm="bfs",
    frames=120,
    output_path="preview.mp4",
    hydra_defaults=[
        "_self_",
        {"scenario": "maze_small"},
    ],
    name="preview"
)

# 3. Create renderer configurations (these replace our manual config loading)
renderer_store = store(group="renderer")

# Draft quality renderer
renderer_store(
    builds(
        SimpleRenderer,
        render_config=builds(RenderConfig, quality="draft", resolution=(854, 480), frame_rate=15)
    ),
    name="draft"
)

# Medium quality renderer  
renderer_store(
    builds(
        SimpleRenderer,
        render_config=builds(RenderConfig, quality="medium", resolution=(1280, 720), frame_rate=30)
    ),
    name="medium"
)

# HD quality renderer
renderer_store(
    builds(
        SimpleRenderer,
        render_config=builds(RenderConfig, quality="high", resolution=(1920, 1080), frame_rate=60)
    ),
    name="hd"
)

# 4. Scene configurations (these replace our scene config loading)
scene_store = store(group="scene")

scene_store(
    builds(
        SceneEngine,
        # This would load from our existing scene configs
        scene_config="${hydra:runtime.choices.scene}",  # Hydra will resolve this
        timing_config="${hydra:runtime.choices.timing}"
    ),
    name="bfs_pathfinding"
)

# 5. Import existing configurations from our config system
def setup_existing_configs():
    """Import our existing ConfigStore configurations into hydra-zen store."""
    from agloviz.config.models import setup_configstore
    from agloviz.core.scene import register_scene_configs
    
    # Setup existing ConfigStore
    cs = setup_configstore()
    register_scene_configs()
    
    # Import scenario configs
    scenario_store = store(group="scenario")
    for config_name, config_node in cs.repo.get("scenario", {}).items():
        clean_name = config_name.replace(".yaml", "")
        scenario_store(config_node.node, name=clean_name)
    
    # Import theme configs
    theme_store = store(group="theme")
    for config_name, config_node in cs.repo.get("theme", {}).items():
        clean_name = config_name.replace(".yaml", "")
        theme_store(config_node.node, name=clean_name)
    
    # Import timing configs
    timing_store = store(group="timing")
    for config_name, config_node in cs.repo.get("timing", {}).items():
        clean_name = config_name.replace(".yaml", "")
        timing_store(config_node.node, name=clean_name)


if __name__ == "__main__":
    # Setup all configurations
    setup_existing_configs()
    
    # Add all configurations to Hydra's store
    store.add_to_hydra_store()
    
    # Create the CLI using hydra-zen's zen().hydra_main()
    # This automatically handles:
    # - CLI argument parsing
    # - Config loading and merging
    # - Override processing (key=value syntax)
    # - Object instantiation
    # - Calling our function with instantiated objects
    
    zen(render_algorithm_video).hydra_main(
        config_name="video",
        config_path=None,
        version_base="1.3"
    )
    
    # Now users can run:
    # python render_app_zen.py                     # Uses all defaults
    # python render_app_zen.py algorithm=dfs       # Override algorithm
    # python render_app_zen.py renderer=hd         # Use HD quality
    # python render_app_zen.py output_path=my.mp4  # Custom output
    # python render_app_zen.py renderer.render_config.resolution=[1920,1080]  # Deep override
