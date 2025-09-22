#!/usr/bin/env python3
"""ALGOViz Render CLI - Proper Hydra-zen Implementation

This demonstrates the correct way to implement our render CLI using hydra-zen.
Compare this to render_app.py to see the differences.

Usage:
    python render_zen_cli.py                    # Use defaults
    python render_zen_cli.py algorithm=dfs      # Override algorithm  
    python render_zen_cli.py renderer=hd        # Use HD quality
    python render_zen_cli.py --help             # Show help
"""

from typing import Any, Dict
from dataclasses import dataclass
from hydra_zen import builds, store, zen
from rich.console import Console
from rich.panel import Panel

console = Console()


# Simple config classes for this demo
@dataclass
class SimpleRenderConfig:
    quality: str = "medium"
    resolution: tuple[int, int] = (1280, 720)
    frame_rate: int = 30


@dataclass 
class SimpleScenarioConfig:
    name: str = "maze_small"
    size: tuple[int, int] = (10, 10)


class MockRenderer:
    def __init__(self, config: SimpleRenderConfig):
        self.config = config
    
    def render_video(self, algorithm: str, scenario: str, output: str) -> Dict[str, Any]:
        return {
            "algorithm": algorithm,
            "scenario": scenario,
            "output": output,
            "quality": self.config.quality,
            "resolution": self.config.resolution
        }


def render_algorithm_video(
    algorithm: str,
    renderer: MockRenderer,
    scenario: SimpleScenarioConfig,
    output_path: str = "zen_output.mp4"
) -> Dict[str, Any]:
    """Main render function - everything instantiated automatically by hydra-zen!
    
    Compare this to render_app.py which does:
    - Manual setup_configstore() calls
    - Manual _load_config_from_store() calls
    - Manual instantiate() calls  
    - Manual override parsing in _apply_overrides()
    
    Here, hydra-zen handles ALL of that automatically!
    """
    console.print(Panel(f"🎬 Rendering [bold cyan]{algorithm}[/] with hydra-zen", title="ALGOViz Zen Demo"))
    
    console.print("✨ All objects automatically instantiated by hydra-zen!")
    console.print(f"📊 Renderer: {renderer.config.quality} @ {renderer.config.resolution}")
    console.print(f"🗺️  Scenario: {scenario.name} ({scenario.size})")
    console.print(f"🚀 Output: [bold green]{output_path}[/]")
    
    # All objects are already configured and ready!
    result = renderer.render_video(algorithm, scenario.name, output_path)
    
    console.print(Panel(
        f"✅ Render complete!\n"
        f"📁 Output: {output_path}\n"
        f"📊 Resolution: {result['resolution']}\n"
        f"🎯 Quality: {result['quality']}\n"
        f"🗺️  Scenario: {result['scenario']}",
        title="[green]Success[/]"
    ))
    
    return result


# Create renderer configurations
DraftRenderer = builds(
    MockRenderer,
    config=builds(SimpleRenderConfig, quality="draft", resolution=(854, 480), frame_rate=15)
)

MediumRenderer = builds(
    MockRenderer,
    config=builds(SimpleRenderConfig, quality="medium", resolution=(1280, 720), frame_rate=30)
)

HDRenderer = builds(
    MockRenderer,
    config=builds(SimpleRenderConfig, quality="hd", resolution=(1920, 1080), frame_rate=60)
)

# Create scenario configurations
SmallMaze = builds(SimpleScenarioConfig, name="maze_small", size=(10, 10))
LargeMaze = builds(SimpleScenarioConfig, name="maze_large", size=(20, 20))

# Store configurations
renderer_store = store(group="renderer")
renderer_store(DraftRenderer, name="draft")
renderer_store(MediumRenderer, name="medium")
renderer_store(HDRenderer, name="hd")

scenario_store = store(group="scenario")
scenario_store(SmallMaze, name="maze_small")
scenario_store(LargeMaze, name="maze_large")

# Configure main function
store(
    render_algorithm_video,
    algorithm="bfs",
    output_path="zen_output.mp4",
    hydra_defaults=[
        "_self_",
        {"renderer": "medium"},
        {"scenario": "maze_small"}
    ],
    name="main"
)


if __name__ == "__main__":
    print("🚀 ALGOViz Hydra-zen CLI Demo")
    print("Compare this to render_app.py (288 lines) vs this file (120 lines)")
    print("=" * 70)
    
    store.add_to_hydra_store()
    
    # This single line replaces ALL our Typer CLI code!
    zen(render_algorithm_video).hydra_main(
        config_name="main",
        version_base="1.3"
    )
    
    # Automatic CLI features:
    # - Rich help with config groups
    # - Native override support  
    # - Deep nested overrides
    # - Config validation
    # - Reproducible runs
    # - Multi-run experiments
    # - All without any manual CLI code!
