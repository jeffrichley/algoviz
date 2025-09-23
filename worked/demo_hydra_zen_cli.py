#!/usr/bin/env python3
"""Standalone Demo: Proper Hydra-zen CLI Implementation

This demonstrates what our render_app.py SHOULD look like using hydra-zen properly.
Based on: https://mit-ll-responsible-ai.github.io/hydra-zen/

Run this to see the difference between our current manual approach and hydra-zen's automatic approach.
"""

from dataclasses import dataclass
from typing import Dict, Any
from hydra_zen import builds, store, zen
from rich.console import Console
from rich.panel import Panel

console = Console()


# =====================================================================
# MOCK CLASSES (representing our actual ALGOViz components)
# =====================================================================

@dataclass 
class MockRenderConfig:
    """Mock of our RenderConfig"""
    quality: str = "medium"
    resolution: tuple[int, int] = (1280, 720)
    frame_rate: int = 30


@dataclass
class MockScenarioConfig:
    """Mock of our ScenarioConfig"""
    name: str = "maze_small"
    size: tuple[int, int] = (10, 10)


class MockRenderer:
    """Mock of our SimpleRenderer"""
    def __init__(self, render_config: MockRenderConfig):
        self.config = render_config
    
    def render_video(self, algorithm: str, scenario: Any, output_path: str) -> Dict[str, Any]:
        return {
            "algorithm": algorithm,
            "output_path": output_path,
            "resolution": self.config.resolution,
            "quality": self.config.quality
        }


# =====================================================================
# MAIN FUNCTION - This is what hydra-zen calls with instantiated objects
# =====================================================================

def render_algorithm_video(
    algorithm: str,
    renderer: MockRenderer,           # ← Automatically instantiated by hydra-zen!
    scenario: MockScenarioConfig,     # ← Automatically instantiated by hydra-zen!
    output_path: str = "output.mp4"
) -> Dict[str, Any]:
    """Main function - receives fully instantiated objects from hydra-zen.
    
    Compare this to our current render_app.py which manually:
    - Calls setup_configstore() 
    - Calls _load_config_from_store() for each config
    - Calls instantiate() manually
    - Parses --override arguments manually
    
    With hydra-zen, ALL of that is automatic!
    """
    console.print(Panel(f"🎬 Rendering [bold cyan]{algorithm}[/] with hydra-zen", title="ALGOViz Demo"))
    
    console.print("✨ All objects were automatically instantiated by hydra-zen!")
    console.print(f"📊 Renderer: {renderer.config}")
    console.print(f"🗺️  Scenario: {scenario}")
    console.print(f"🚀 Output: [bold green]{output_path}[/]")
    
    # All objects are already configured and ready to use!
    result = renderer.render_video(algorithm, scenario, output_path)
    
    console.print(Panel(
        f"✅ Render complete!\n"
        f"📁 Output: {output_path}\n"
        f"📊 Resolution: {result['resolution']}\n"
        f"🎯 Quality: {result['quality']}\n"
        f"🗺️  Scenario: {scenario.name}",
        title="[green]Success[/]"
    ))
    
    return result


# =====================================================================
# HYDRA-ZEN CONFIGURATION SETUP
# =====================================================================

# 1. Create renderer configurations using builds()
DraftRenderer = builds(
    MockRenderer,
    render_config=builds(MockRenderConfig, quality="draft", resolution=(854, 480), frame_rate=15)
)

MediumRenderer = builds(
    MockRenderer, 
    render_config=builds(MockRenderConfig, quality="medium", resolution=(1280, 720), frame_rate=30)
)

HDRenderer = builds(
    MockRenderer,
    render_config=builds(MockRenderConfig, quality="high", resolution=(1920, 1080), frame_rate=60)
)

# 2. Create scenario configurations
SmallMaze = builds(MockScenarioConfig, name="maze_small", size=(10, 10))
LargeMaze = builds(MockScenarioConfig, name="maze_large", size=(20, 20))

# 3. Store all configurations
renderer_store = store(group="renderer")
renderer_store(DraftRenderer, name="draft")
renderer_store(MediumRenderer, name="medium")
renderer_store(HDRenderer, name="hd")

scenario_store = store(group="scenario") 
scenario_store(SmallMaze, name="maze_small")
scenario_store(LargeMaze, name="maze_large")

# 4. Configure the main function with defaults
app_store = store(group="app")
app_store(
    render_algorithm_video,
    algorithm="bfs",  # Default algorithm
    output_path="hydra_zen_demo.mp4",  # Default output
    hydra_defaults=[
        "_self_",
        {"renderer": "medium"},    # Default renderer
        {"scenario": "maze_small"} # Default scenario
    ],
    name="render"
)


if __name__ == "__main__":
    print("🚀 Starting Hydra-zen Demo CLI")
    print("=" * 50)
    
    # Add all configurations to Hydra store
    store.add_to_hydra_store()
    
    # Create CLI using zen().hydra_main() - this replaces ALL our Typer code!
    zen(render_algorithm_video).hydra_main(
        config_name="app/render",  # Use the full path: group/name
        config_path=None, 
        version_base="1.3"
    )
    
    # This automatically creates a CLI that supports:
    #
    # Basic usage:
    # python demo_hydra_zen_cli.py                     # Uses all defaults
    # python demo_hydra_zen_cli.py --help              # Shows help
    #
    # Override parameters:
    # python demo_hydra_zen_cli.py algorithm=dfs       # Change algorithm
    # python demo_hydra_zen_cli.py renderer=hd         # Use HD quality
    # python demo_hydra_zen_cli.py scenario=maze_large # Use large maze
    # python demo_hydra_zen_cli.py output_path=test.mp4 # Custom output
    #
    # Deep overrides (nested config changes):
    # python demo_hydra_zen_cli.py renderer.render_config.resolution=[1920,1080]
    # python demo_hydra_zen_cli.py renderer.render_config.frame_rate=60
    # python demo_hydra_zen_cli.py scenario.size=[25,25]
    #
    # Multiple overrides:
    # python demo_hydra_zen_cli.py algorithm=dfs renderer=hd scenario=maze_large
    #
    # All of this CLI functionality, config loading, instantiation, and override 
    # handling that we manually implement in render_app.py is AUTOMATIC with hydra-zen!
