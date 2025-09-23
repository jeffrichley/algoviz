"""Pure Visual Primitive Wrappers for Manim Objects.

This module provides thin wrappers around Manim primitives that add ALGOViz-specific
visual operations without any algorithm-specific functionality. Algorithm behavior
comes from scene configuration event bindings, not widget methods.
"""

from typing import Any

from manim import BLACK, WHITE, Circle, Line, Rectangle, Text, VGroup


class TokenWidget(Circle):
    """Pure visual token - circle with basic visual operations.

    NO algorithm-specific methods! Algorithm behavior comes from scene configuration.
    """

    def __init__(self, radius: float = 0.25, **kwargs: Any) -> None:
        super().__init__(radius=radius, **kwargs)
        self.set_stroke(WHITE, width=1)
        self.set_fill(BLACK, opacity=0.1)
        self._label: Text | None = None

    def highlight(self, color: str, opacity: float = 0.7) -> None:
        """Pure visual operation: change fill color."""
        self.set_fill(color, opacity=opacity)

    def set_label(self, text: str, font_size: int = 12) -> None:
        """Pure visual operation: add or update text label."""
        if self._label:
            self._label.become(Text(text, font_size=font_size))
        else:
            self._label = Text(text, font_size=font_size)
            self._label.move_to(self.get_center())

    def remove_label(self) -> None:
        """Pure visual operation: remove text label."""
        if self._label:
            self._label = None

    def pulse(self, scale_factor: float = 1.3, duration: float = 0.5) -> Any:
        """Pure visual operation: pulse animation."""
        # Return animation for scene to play
        return self.animate.scale(scale_factor).set_rate_func(
            lambda t: 1 + 0.3 * (1 - t)
        )


class MarkerWidget(Rectangle):
    """Pure visual marker - rectangle with basic visual operations.

    NO algorithm-specific methods! Algorithm behavior comes from scene configuration.
    """

    def __init__(self, width: float = 0.5, height: float = 0.5, **kwargs: Any) -> None:
        super().__init__(width=width, height=height, **kwargs)
        self.set_stroke(WHITE, width=2)
        self.set_fill(BLACK, opacity=0.1)
        self._label: Text | None = None

    def highlight(self, color: str, opacity: float = 0.8) -> None:
        """Pure visual operation: change fill color."""
        self.set_fill(color, opacity=opacity)

    def set_label(self, text: str, font_size: int = 14) -> None:
        """Pure visual operation: add or update text label."""
        if self._label:
            self._label.become(Text(text, font_size=font_size))
        else:
            self._label = Text(text, font_size=font_size)
            self._label.move_to(self.get_center())

    def flash(self, color: str, duration: float = 0.3) -> list[Any]:
        """Pure visual operation: flash animation."""
        # Return animation for scene to play
        original_color = self.get_fill_color()
        return [
            self.animate.set_fill(color, opacity=1.0).set_duration(duration / 2),
            self.animate.set_fill(original_color).set_duration(duration / 2),
        ]


class ConnectionWidget(Line):
    """Pure visual connection - line with basic visual operations.

    NO algorithm-specific methods! Algorithm behavior comes from scene configuration.
    """

    def __init__(
        self,
        start_point: tuple[float, float, float],
        end_point: tuple[float, float, float],
        **kwargs: Any,
    ) -> None:
        super().__init__(start_point, end_point, **kwargs)
        self.set_stroke(WHITE, width=2)

    def highlight(self, color: str, width: float = 3.0) -> None:
        """Pure visual operation: change line color and width."""
        self.set_stroke(color, width=width)

    def animate_draw(self, duration: float = 1.0) -> Any:
        """Pure visual operation: animate line drawing."""
        from manim import Create

        return Create(self, run_time=duration)

    def animate_fade(self, duration: float = 1.0) -> Any:
        """Pure visual operation: animate line fading."""
        from manim import FadeOut

        return FadeOut(self, run_time=duration)


class ContainerGroup(VGroup):
    """Pure visual container - VGroup with layout operations.

    Uses Manim's built-in arrangement methods instead of custom layouts.
    """

    def __init__(self, *elements: Any, **kwargs: Any) -> None:
        super().__init__(*elements, **kwargs)

    def arrange_horizontal(self, spacing: float = 0.5) -> None:
        """Pure visual operation: arrange elements horizontally."""
        from manim import RIGHT

        self.arrange(RIGHT, buff=spacing)

    def arrange_vertical(self, spacing: float = 0.5) -> None:
        """Pure visual operation: arrange elements vertically."""
        from manim import DOWN

        self.arrange(DOWN, buff=spacing)

    def arrange_in_grid(self, rows: int, cols: int, spacing: float = 0.5) -> None:
        """Pure visual operation: arrange elements in grid."""
        # Use Manim's built-in grid arrangement if available
        # Otherwise, manual grid positioning
        for i, element in enumerate(self):
            row = i // cols
            col = i % cols
            x = (col - (cols - 1) / 2) * spacing
            y = ((rows - 1) / 2 - row) * spacing
            element.move_to([x, y, 0])

    def highlight_element(self, index: int, color: str, opacity: float = 0.7) -> None:
        """Pure visual operation: highlight specific element."""
        if 0 <= index < len(self):
            element = self[index]
            if hasattr(element, "highlight"):
                element.highlight(color, opacity)
            else:
                element.set_fill(color, opacity=opacity)
