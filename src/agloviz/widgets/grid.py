"""GridWidget for 2D grid visualization.

This module provides the GridWidget using pure visual primitives.
Algorithm-specific behavior comes from scene configuration event bindings.
"""

from typing import Any

from manim import *

from .primitives import ContainerGroup, TokenWidget
from .protocol import Widget


class GridWidget(Widget):
    """2D grid with colored cells for pathfinding visualization.
    
    The GridWidget provides a visual representation of a 2D grid where algorithms
    can mark cells as frontier, visited, goal, etc. through VizEvent updates.
    """

    def __init__(self, width: int = 10, height: int = 10):
        self.grid_group: VGroup | None = None
        self.cell_map: dict[tuple[int, int], Square] = {}
        self.width: int = width
        self.height: int = height

    def show(self, scene: Any, **kwargs) -> None:
        """Initialize and render grid with enter animation.
        
        Args:
            scene: Manim scene instance
            **kwargs: Optional runtime parameters like run_time
        """
        run_time = kwargs.get("run_time", 1.0)

        self._create_grid(scene)
        scene.play(FadeIn(self.grid_group), run_time=run_time)

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
        """Create grid visual structure using pure visual primitives.
        
        Args:
            scene: Manim scene instance
        """
        cells = []
        cell_size = 0.5

        for row in range(self.height):
            for col in range(self.width):
                # Use TokenWidget instead of raw Square
                cell = TokenWidget(radius=cell_size/2)

                # Position cells in a grid centered on origin
                x_pos = (col - (self.width - 1) / 2) * cell_size
                y_pos = ((self.height - 1) / 2 - row) * cell_size
                cell.move_to([x_pos, y_pos, 0])

                self.cell_map[(col, row)] = cell
                cells.append(cell)

        # Use ContainerGroup with grid arrangement
        self.grid_group = ContainerGroup(*cells)
        self.grid_group.arrange_in_grid(self.height, self.width, cell_size)

    def highlight_cell(self, pos: tuple[int, int], color: str, opacity: float = 0.7):
        """Pure visual operation: highlight cell at position with color.
        
        Args:
            pos: Grid position (col, row)
            color: Color to highlight with
            opacity: Fill opacity
        """
        if pos in self.cell_map:
            cell = self.cell_map[pos]
            cell.highlight(color, opacity)

    def flash_cell(self, pos: tuple[int, int], color: str, scale_factor: float = 1.2):
        """Pure visual operation: flash cell at position with color and scaling.
        
        Args:
            pos: Grid position (col, row)
            color: Color to flash with
            scale_factor: Scale factor for pulse effect
        """
        if pos in self.cell_map:
            cell = self.cell_map[pos]
            cell.highlight(color, opacity=1.0)
            return cell.pulse(scale_factor=scale_factor)

    def set_cell_label(self, pos: tuple[int, int], text: str):
        """Pure visual operation: set text label on cell.
        
        Args:
            pos: Grid position (col, row)
            text: Text to display
        """
        if pos in self.cell_map:
            cell = self.cell_map[pos]
            cell.set_label(text)

    def get_cell_positions(self) -> list[tuple[int, int]]:
        """Pure visual operation: get all cell positions.
        
        Returns:
            List of all cell positions in the grid
        """
        return list(self.cell_map.keys())
