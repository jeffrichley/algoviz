"""Simple Renderer - Hydra-zen First Architecture.

Minimal video renderer that leverages Manim's built-in rendering capabilities
with hydra-zen configuration and our widget architecture.
"""

from pathlib import Path
from typing import Any

from hydra_zen import builds, instantiate
from manim import Scene
from manim import config as manim_config

from agloviz.core.scene import SceneEngine

from .config import RenderConfig


class SimpleRenderer:
    """Minimal video renderer using Manim's built-in capabilities."""

    def __init__(self, render_config: RenderConfig):
        self.config = render_config
        self._setup_manim_config()

    def _setup_manim_config(self):
        """Configure Manim settings based on render config."""
        # Set Manim global config
        manim_config.frame_width = self.config.resolution[0] / 100  # Manim units
        manim_config.frame_height = self.config.resolution[1] / 100
        manim_config.frame_rate = self.config.frame_rate

        # Quality settings - handle both enum and string values
        quality_value = self.config.quality.value if hasattr(self.config.quality, 'value') else self.config.quality
        if quality_value == "draft":
            manim_config.quality = "low_quality"
        elif quality_value == "medium":
            manim_config.quality = "medium_quality"
        else:
            manim_config.quality = "high_quality"

    def render_algorithm_video(
        self,
        algorithm: str,
        scenario_config: Any,
        scene_config: Any,
        theme_config: Any,
        timing_config: Any,
        output_path: str
    ) -> dict[str, Any]:
        """Render algorithm visualization to video.
        
        Args:
            algorithm: Algorithm name
            scenario_config: Scenario configuration
            scene_config: Scene configuration  
            theme_config: Theme configuration
            timing_config: Timing configuration
            output_path: Output video file path
            
        Returns:
            Render result metadata
        """
        # Create output directory
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Create scene engine
        scene_engine = SceneEngine(scene_config, timing_config)

        # Create Manim scene class
        scene_class = self._create_manim_scene_class(
            scene_engine, scenario_config, theme_config, algorithm
        )

        # Configure Manim output
        manim_config.output_file = output_file.stem
        manim_config.media_dir = str(output_file.parent)

        # Render using Manim
        scene = scene_class()
        scene.render()

        # Return metadata
        return {
            "duration": "N/A",  # TODO: Calculate from timing
            "resolution": self.config.resolution,
            "algorithm": algorithm,
            "output_path": output_path
        }

    def _create_manim_scene_class(self, scene_engine: SceneEngine, scenario_config: Any,
                                 theme_config: Any, algorithm: str):
        """Create Manim Scene class for rendering."""

        class AlgorithmScene(Scene):
            def construct(self):
                # Initialize widgets from scene engine
                for widget_name, widget in scene_engine.widgets.items():
                    if hasattr(widget, 'show'):
                        widget.show(self, width=10, height=10)  # Basic setup
                        if hasattr(widget, 'grid_group') and widget.grid_group:
                            self.add(widget.grid_group)
                        elif hasattr(widget, 'queue_group') and widget.queue_group:
                            self.add(widget.queue_group)

                # Simple animation - just show the widgets
                self.wait(2)  # 2 second video for now

        return AlgorithmScene


class PreviewRenderer:
    """Fast preview renderer for quick iteration."""

    def __init__(self, max_frames: int = 120):
        self.max_frames = max_frames

        # Configure for fast preview
        manim_config.quality = "low_quality"
        manim_config.frame_rate = 15  # Lower FPS for preview

    def render_preview(self, algorithm: str, scenario: str, output_path: str) -> dict[str, Any]:
        """Render quick preview."""
        # Simple preview implementation
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Create minimal scene
        class PreviewScene(Scene):
            def construct(self):
                from manim import Text
                title = Text(f"Preview: {algorithm}")
                self.add(title)
                self.wait(1)

        # Render
        scene = PreviewScene()
        manim_config.output_file = output_file.stem
        manim_config.media_dir = str(output_file.parent)
        scene.render()

        return {
            "algorithm": algorithm,
            "frames": self.max_frames,
            "output_path": output_path
        }


# Hydra-zen structured configs
SimpleRendererConfigZen = builds(
    SimpleRenderer,
    render_config=builds(RenderConfig),
    zen_partial=True,
    populate_full_signature=True
)

PreviewRendererConfigZen = builds(
    PreviewRenderer,
    max_frames=120,
    zen_partial=True,
    populate_full_signature=True
)


def create_renderer(render_config: RenderConfig) -> SimpleRenderer:
    """Factory function to create renderer with hydra-zen."""
    # Direct instantiation since we already have the config instance
    return SimpleRenderer(render_config)


def create_preview_renderer(max_frames: int = 120) -> PreviewRenderer:
    """Factory function to create preview renderer with hydra-zen."""
    return instantiate(PreviewRendererConfigZen, max_frames=max_frames)
