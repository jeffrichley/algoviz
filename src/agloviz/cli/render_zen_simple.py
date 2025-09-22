"""Simple Hydra-zen CLI - Proper Implementation.

This shows the correct way to use hydra-zen according to the documentation:
https://mit-ll-responsible-ai.github.io/hydra-zen/

Key benefits over our current manual approach:
1. Automatic CLI generation with zen().hydra_main()
2. Automatic config instantiation 
3. Native override support (key=value)
4. No manual ConfigStore management
5. No manual object creation
"""

from typing import Any, Dict
from hydra_zen import builds, store, zen
from rich.console import Console
from rich.panel import Panel

# Import our components
from agloviz.rendering.renderer import SimpleRenderer  
from agloviz.rendering.config import RenderConfig, RenderQuality, RenderFormat

console = Console()


def render_video(
    algorithm: str,
    renderer: SimpleRenderer,
    output_path: str = "output.mp4"
) -> Dict[str, Any]:
    """Main render function - hydra-zen instantiates everything automatically!
    
    Compare this to our current render_app.py:
    - No manual ConfigStore setup
    - No manual _load_config_from_store calls  
    - No manual instantiate() calls
    - No manual override parsing
    
    Hydra-zen handles all of that automatically!
    """
    console.print(Panel(f"🎬 Rendering [bold cyan]{algorithm}[/] with hydra-zen", title="ALGOViz Zen"))
    
    console.print("✨ All objects instantiated automatically by hydra-zen!")
    console.print(f"📊 Renderer config: {renderer.config}")
    console.print(f"🚀 Output: [bold green]{output_path}[/]")
    
    # Renderer is already fully configured and instantiated!
    result = {
        "algorithm": algorithm,
        "output_path": output_path,
        "resolution": renderer.config.resolution,
        "quality": renderer.config.quality.value,
        "success": True
    }
    
    console.print(Panel(
        f"✅ Render complete!\n"
        f"📁 Output: {output_path}\n"
        f"📊 Resolution: {result['resolution']}\n"
        f"🎯 Quality: {result['quality']}\n"
        f"🎯 Algorithm: {algorithm}",
        title="[green]Success[/]"
    ))
    
    return result


# =====================================================================
# HYDRA-ZEN CONFIGURATION - This replaces all our manual config code!
# =====================================================================

# Create renderer configurations using builds()
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

# Store configurations - this replaces our ConfigStore registration
renderer_store = store(group="renderer")
renderer_store(DraftRenderer, name="draft")
renderer_store(MediumRenderer, name="medium") 
renderer_store(HDRenderer, name="hd")

# Configure main function with defaults
app_store = store(group="app")
app_store(
    render_video,
    algorithm="bfs",
    output_path="hydra_zen_output.mp4",
    hydra_defaults=[
        "_self_",
        {"renderer": "medium"}  # Default to medium quality
    ],
    name="render"
)


if __name__ == "__main__":
    # Add all configs to Hydra store
    store.add_to_hydra_store()
    
    # Create CLI with zen().hydra_main() - this replaces all our Typer code!
    zen(render_video).hydra_main(
        config_name="render", 
        config_path=None,
        version_base="1.3"
    )
    
    # Usage examples (all automatic!):
    # python render_zen_simple.py                    # Uses defaults (bfs, medium)
    # python render_zen_simple.py algorithm=dfs      # Override algorithm  
    # python render_zen_simple.py renderer=hd        # Use HD quality
    # python render_zen_simple.py renderer=draft     # Use draft quality
    # python render_zen_simple.py output_path=test.mp4  # Custom output
    # 
    # Deep overrides (automatic!):
    # python render_zen_simple.py renderer.render_config.resolution=[1920,1080]
    # python render_zen_simple.py renderer.render_config.frame_rate=60
    #
    # All the CLI parsing, config loading, instantiation, and override 
    # handling that we do manually in render_app.py is automatic here!
