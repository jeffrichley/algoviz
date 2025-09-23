"""Command-line interface for ALGOViz.

This module provides the CLI application using hydra-zen for rendering
algorithm visualizations and managing configurations.
"""

from .render_pure_zen import main

__all__ = ["main"]
