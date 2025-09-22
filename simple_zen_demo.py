#!/usr/bin/env python3
"""Simplest Hydra-zen Demo - Based on Documentation Example

This shows the minimal hydra-zen setup from:
https://mit-ll-responsible-ai.github.io/hydra-zen/

Compare this automatic approach to our manual render_app.py
"""

from dataclasses import dataclass
from hydra_zen import builds, store, zen
from rich.console import Console

console = Console()


@dataclass
class RenderConfig:
    """Simple render configuration"""
    quality: str = "medium"
    resolution: tuple[int, int] = (1280, 720)


class SimpleRenderer:
    """Simple renderer class"""
    def __init__(self, config: RenderConfig):
        self.config = config
    
    def render(self, algorithm: str) -> str:
        return f"Rendered {algorithm} at {self.config.resolution} with {self.config.quality} quality"


def render_algorithm(algorithm: str, renderer: SimpleRenderer) -> str:
    """Main function - hydra-zen will instantiate renderer automatically"""
    console.print(f"🎬 [bold cyan]Algorithm:[/] {algorithm}")
    console.print(f"📊 [bold green]Renderer:[/] {renderer.config}")
    
    result = renderer.render(algorithm)
    console.print(f"✅ [bold green]Result:[/] {result}")
    return result


# Configure renderer options
draft_renderer = builds(SimpleRenderer, config=builds(RenderConfig, quality="draft", resolution=(854, 480)))
hd_renderer = builds(SimpleRenderer, config=builds(RenderConfig, quality="hd", resolution=(1920, 1080)))

# Store configurations
renderer_store = store(group="renderer")
renderer_store(draft_renderer, name="draft")
renderer_store(hd_renderer, name="hd")

# Store main function with defaults
store(
    render_algorithm,
    algorithm="bfs",
    hydra_defaults=["_self_", {"renderer": "hd"}],
    name="main"
)


if __name__ == "__main__":
    store.add_to_hydra_store()
    
    # This creates a full CLI automatically!
    zen(render_algorithm).hydra_main(
        config_name="main",
        version_base="1.3"
    )
    
    # Usage:
    # python simple_zen_demo.py                    # Uses defaults (bfs, hd)
    # python simple_zen_demo.py algorithm=dfs      # Override algorithm
    # python simple_zen_demo.py renderer=draft     # Use draft quality
    # python simple_zen_demo.py renderer.config.resolution=[1024,768]  # Deep override
