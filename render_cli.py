#!/usr/bin/env python3
"""Standalone CLI entry point for ALGOViz Render App.

PREFERRED: Use 'uv run render' (configured in pyproject.toml)
ALTERNATIVE: Use this script directly with 'python render_cli.py'

This is a new, clean CLI application separate from the legacy CLI system.
Uses Typer and hydra-zen first architecture.
"""

import sys
from pathlib import Path

# Add src to path so we can import agloviz
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agloviz.cli.render_app import app

if __name__ == "__main__":
    print("💡 TIP: You can also run 'uv run render' instead of this script!")
    print("=" * 60)
    app()
