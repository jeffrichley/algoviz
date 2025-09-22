"""New Render CLI App - Hydra-zen First Architecture.

Clean CLI application for rendering algorithm visualizations using Typer and hydra-zen.
Completely separate from the legacy CLI system.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hydra_zen import instantiate
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf

# Create Typer app
app = typer.Typer(
    name="render",
    help="ALGOViz Rendering System - Generate algorithm visualization videos",
    rich_markup_mode="rich"
)

console = Console()


@app.command()
def video(
    algorithm: str = typer.Argument(..., help="Algorithm to visualize (e.g., bfs)"),
    scenario: str = typer.Option("maze_small", "--scenario", "-s", help="Scenario configuration name"),
    render_quality: str = typer.Option("medium", "--quality", "-q", help="Render quality: draft/medium/hd/4k"),
    theme: str = typer.Option("default", "--theme", "-t", help="Visual theme name"),
    timing: str = typer.Option("normal", "--timing", help="Timing mode: draft/normal/fast"),
    output: str = typer.Option("output.mp4", "--output", "-o", help="Output video file path"),
    overrides: Optional[list[str]] = typer.Option(None, "--override", help="Config overrides (key=value)")
):
    """Render algorithm visualization to video using hydra-zen configuration.
    
    Examples:
        render video bfs --scenario maze_large --quality hd
        render video bfs --override scenario.start=[2,2] render.resolution=[1920,1080]
    """
    console.print(Panel(f"🎬 Rendering [bold cyan]{algorithm}[/] visualization", title="ALGOViz Render"))
    
    try:
        # Setup ConfigStore
        from agloviz.config.store_manager import StoreManager
        console.print("📋 Setting up configurations...")
        StoreManager.setup_store()
        cs = ConfigStore.instance()
        
        # Load configurations from ConfigStore
        scenario_config = _load_config_from_store(cs, "scenario", scenario)
        render_config = _load_config_from_store(cs, "render", render_quality)
        theme_config = _load_config_from_store(cs, "theme", theme)
        timing_config = _load_config_from_store(cs, "timing", timing)
        
        # Determine scene configuration
        scene_name = f"{algorithm}_pathfinding"
        scene_config = _load_config_from_store(cs, "scene", scene_name)
        
        console.print(f"✅ Loaded configurations: {scenario}, {render_quality}, {theme}, {timing}")
        
        # Apply CLI overrides
        if overrides:
            console.print(f"🔧 Applying overrides: {overrides}")
            scenario_config, render_config, theme_config, timing_config = _apply_overrides(
                overrides, scenario_config, render_config, theme_config, timing_config
            )
        
        # Create renderer using hydra-zen
        console.print("🎥 Creating renderer...")
        from agloviz.rendering.renderer import create_renderer
        renderer = create_renderer(render_config)
        
        # Render video
        console.print(f"🚀 Rendering video to: [bold green]{output}[/]")
        result = renderer.render_algorithm_video(
            algorithm=algorithm,
            scenario_config=scenario_config,
            scene_config=scene_config,
            theme_config=theme_config,
            timing_config=timing_config,
            output_path=output
        )
        
        # Success report
        console.print(Panel(
            f"✅ Video rendered successfully!\n"
            f"📁 Output: {output}\n"
            f"⏱️  Duration: {result.get('duration', 'N/A')}s\n"
            f"📊 Resolution: {result.get('resolution', 'N/A')}\n"
            f"🎯 Algorithm: {algorithm}",
            title="[green]Render Complete[/]"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"❌ Render failed: {str(e)}",
            title="[red]Render Error[/]",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command()
def list_configs(
    config_type: str = typer.Argument(..., help="Configuration type: scenario/theme/timing/render/scene")
):
    """List available configurations from ConfigStore.
    
    Examples:
        render list-configs scenario
        render list-configs render
    """
    console.print(Panel(f"📋 Available [bold cyan]{config_type}[/] configurations", title="ConfigStore"))
    
    try:
        # Setup ConfigStore
        from agloviz.config.store_manager import StoreManager
        StoreManager.setup_store()
        cs = ConfigStore.instance()
        
        # Get configurations
        if config_type not in cs.repo:
            console.print(f"❌ No configurations found for type: {config_type}")
            available_types = list(cs.repo.keys())
            console.print(f"Available types: {', '.join(available_types)}")
            raise typer.Exit(1)
        
        configs = cs.repo[config_type]
        
        # Create table
        table = Table(title=f"{config_type.title()} Configurations")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        
        for config_name in configs.keys():
            clean_name = config_name.replace(".yaml", "")
            table.add_row(clean_name, f"{config_type} configuration")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error listing configs: {e}")
        raise typer.Exit(1)


@app.command()
def validate_config(
    config_type: str = typer.Argument(..., help="Configuration type"),
    config_name: str = typer.Argument(..., help="Configuration name")
):
    """Validate a specific configuration from ConfigStore.
    
    Examples:
        render validate-config scenario maze_small
        render validate-config render hd
    """
    console.print(Panel(f"🔍 Validating [bold cyan]{config_type}/{config_name}[/]", title="Config Validation"))
    
    try:
        # Setup ConfigStore
        from agloviz.config.store_manager import StoreManager
        StoreManager.setup_store()
        cs = ConfigStore.instance()
        
        # Load and instantiate config
        config = _load_config_from_store(cs, config_type, config_name)
        
        console.print(f"✅ Configuration [bold green]{config_type}/{config_name}[/] is valid!")
        console.print(f"📊 Type: {type(config).__name__}")
        
        # Show some config details
        if hasattr(config, 'name'):
            console.print(f"📝 Name: {config.name}")
        
    except Exception as e:
        console.print(f"❌ Validation failed: {e}")
        raise typer.Exit(1)


@app.command()
def preview(
    algorithm: str = typer.Argument(..., help="Algorithm to preview"),
    scenario: str = typer.Option("maze_small", "--scenario", "-s", help="Scenario name"),
    frames: int = typer.Option(120, "--frames", "-f", help="Number of frames to render"),
    output: str = typer.Option("preview.mp4", "--output", "-o", help="Preview output file")
):
    """Quick preview render with limited frames.
    
    Examples:
        render preview bfs --frames 60
        render preview bfs --scenario maze_large --frames 180
    """
    console.print(Panel(f"👀 Previewing [bold cyan]{algorithm}[/] ({frames} frames)", title="Quick Preview"))
    
    try:
        # Use draft quality for preview
        console.print("🚀 Rendering preview with draft quality...")
        
        # Call main video render with draft settings
        # This reuses the video command logic but with preview settings
        from agloviz.rendering.renderer import create_preview_renderer
        
        renderer = create_preview_renderer(max_frames=frames)
        result = renderer.render_preview(algorithm, scenario, output)
        
        console.print(Panel(
            f"✅ Preview rendered!\n"
            f"📁 Output: {output}\n" 
            f"🎞️  Frames: {frames}\n"
            f"⚡ Mode: Draft quality",
            title="[green]Preview Complete[/]"
        ))
        
    except Exception as e:
        console.print(f"❌ Preview failed: {e}")
        raise typer.Exit(1)


def _load_config_from_store(cs: ConfigStore, config_type: str, config_name: str):
    """Load and instantiate configuration from ConfigStore."""
    if config_type not in cs.repo:
        raise ValueError(f"Configuration type '{config_type}' not found")
    
    config_key = f"{config_name}.yaml"
    if config_key not in cs.repo[config_type]:
        available = list(cs.repo[config_type].keys())
        raise ValueError(f"Configuration '{config_name}' not found in {config_type}. Available: {available}")
    
    config_node = cs.repo[config_type][config_key].node
    return instantiate(config_node)


def _apply_overrides(overrides: list[str], *configs):
    """Apply CLI overrides to configurations using OmegaConf."""
    # Parse overrides into OmegaConf format
    override_dict = {}
    for override in overrides:
        if "=" not in override:
            continue
        key, value = override.split("=", 1)
        
        # Convert string value to appropriate type
        try:
            # Try to parse as list/number
            if value.startswith("[") and value.endswith("]"):
                import ast
                value = ast.literal_eval(value)
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "").isdigit():
                value = float(value)
        except:
            pass  # Keep as string
        
        # Set nested key
        keys = key.split(".")
        current = override_dict
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    
    # Apply overrides to configs
    override_config = OmegaConf.create(override_dict)
    updated_configs = []
    
    for config in configs:
        config_dict = OmegaConf.structured(config)
        merged_config = OmegaConf.merge(config_dict, override_config)
        updated_configs.append(OmegaConf.to_container(merged_config, resolve=True))
    
    return updated_configs


if __name__ == "__main__":
    app()
