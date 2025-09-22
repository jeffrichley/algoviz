"""ALGOViz Rendering System - Hydra-zen First.

This package provides video rendering capabilities using hydra-zen configuration
and Manim's built-in rendering engine.
"""

from .renderer import SimpleRenderer, create_renderer, create_preview_renderer
from .config import RenderConfig, RenderQuality, RenderFormat

__all__ = [
    "SimpleRenderer",
    "create_renderer", 
    "create_preview_renderer",
    "RenderConfig",
    "RenderQuality",
    "RenderFormat"
]
