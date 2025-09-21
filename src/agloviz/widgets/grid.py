"""GridWidget for 2D grid visualization.

This module provides the GridWidget for pathfinding algorithm visualization,
supporting colored cells and event-driven updates.
"""

from typing import Any, Dict, Tuple
from manim import *
from agloviz.core.events import VizEvent, PayloadKey
from .protocol import Widget


class GridWidget(Widget):
    """2D grid with colored cells for pathfinding visualization.
    
    The GridWidget provides a visual representation of a 2D grid where algorithms
    can mark cells as frontier, visited, goal, etc. through VizEvent updates.
    """
    
    def __init__(self):
        self.grid_group: VGroup | None = None
        self.cell_map: Dict[Tuple[int, int], Square] = {}
        self.width: int = 0
        self.height: int = 0
    
    def show(self, scene: Any, **kwargs) -> None:
        """Initialize and render grid with enter animation.
        
        Args:
            scene: Manim scene instance
            **kwargs: Configuration parameters including width, height, run_time
        """
        self.width = kwargs.get("width", 10)
        self.height = kwargs.get("height", 10)
        run_time = kwargs.get("run_time", 1.0)
        
        self._create_grid(scene)
        scene.play(FadeIn(self.grid_group), run_time=run_time)
    
    def update(self, scene: Any, event: VizEvent, run_time: float) -> None:
        """React to VizEvents through routing system.
        
        Args:
            scene: Manim scene instance
            event: VizEvent to process
            run_time: Duration for any animations
        """
        if event.type == "enqueue":
            self._mark_frontier(scene, event, run_time)
        elif event.type == "dequeue":
            self._mark_visited(scene, event, run_time)
        elif event.type == "goal_found":
            self._flash_goal(scene, event, run_time)
    
    def hide(self, scene: Any) -> None:
        """Clean teardown with exit animation.
        
        Args:
            scene: Manim scene instance
        """
        if self.grid_group:
            scene.play(FadeOut(self.grid_group))
            self.grid_group = None
            self.cell_map.clear()
            self.width = 0
            self.height = 0
    
    def _create_grid(self, scene: Any) -> None:
        """Create grid visual structure.
        
        Args:
            scene: Manim scene instance
        """
        cells = []
        cell_size = 0.5
        
        for row in range(self.height):
            for col in range(self.width):
                cell = Square(side_length=cell_size)
                cell.set_stroke(WHITE, width=1)
                cell.set_fill(BLACK, opacity=0.1)
                
                # Position cells in a grid centered on origin
                x_pos = (col - (self.width - 1) / 2) * cell_size
                y_pos = ((self.height - 1) / 2 - row) * cell_size
                cell.move_to([x_pos, y_pos, 0])
                
                self.cell_map[(col, row)] = cell
                cells.append(cell)
        
        self.grid_group = VGroup(*cells)
    
    def _mark_frontier(self, scene: Any, event: VizEvent, run_time: float) -> None:
        """Handle grid.mark_frontier routing.
        
        Args:
            scene: Manim scene instance
            event: VizEvent containing node information
            run_time: Animation duration
        """
        if PayloadKey.NODE not in event.payload:
            return
        
        node = event.payload[PayloadKey.NODE]
        if node in self.cell_map:
            cell = self.cell_map[node]
            scene.play(
                cell.animate.set_fill(BLUE, opacity=0.7),
                run_time=run_time
            )
    
    def _mark_visited(self, scene: Any, event: VizEvent, run_time: float) -> None:
        """Handle grid.mark_visited routing.
        
        Args:
            scene: Manim scene instance
            event: VizEvent containing node information
            run_time: Animation duration
        """
        if PayloadKey.NODE not in event.payload:
            return
        
        node = event.payload[PayloadKey.NODE]
        if node in self.cell_map:
            cell = self.cell_map[node]
            scene.play(
                cell.animate.set_fill(GRAY, opacity=0.5),
                run_time=run_time
            )
    
    def _flash_goal(self, scene: Any, event: VizEvent, run_time: float) -> None:
        """Handle grid.flash_goal routing.
        
        Args:
            scene: Manim scene instance
            event: VizEvent containing goal node information
            run_time: Animation duration
        """
        if PayloadKey.NODE not in event.payload:
            return
        
        node = event.payload[PayloadKey.NODE]
        if node in self.cell_map:
            cell = self.cell_map[node]
            scene.play(
                Succession(
                    cell.animate.set_fill(GREEN, opacity=1.0),
                    cell.animate.scale(1.2),
                    cell.animate.scale(1.0),
                ),
                run_time=run_time
            )
