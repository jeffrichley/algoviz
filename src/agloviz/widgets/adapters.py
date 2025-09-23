"""Widget Adapters for Event Processing.

Widget adapters handle VizEvents and translate them to pure visual widget operations.
This separates event processing logic from pure visual widgets.
"""

from typing import Any

from agloviz.core.events import PayloadKey, VizEvent

from .grid import GridWidget
from .protocol import WidgetAdapter
from .queue import QueueWidget


class GridWidgetAdapter:
    """Adapter that processes VizEvents for GridWidget."""

    def update(
        self, widget: GridWidget, scene: Any, event: VizEvent, run_time: float
    ) -> None:
        """Process VizEvent and call appropriate GridWidget visual methods.

        Args:
            widget: GridWidget instance
            scene: Manim scene instance
            event: VizEvent to process
            run_time: Duration for any animations
        """
        if event.type == "enqueue":
            self._handle_enqueue(widget, scene, event, run_time)
        elif event.type == "dequeue":
            self._handle_dequeue(widget, scene, event, run_time)
        elif event.type == "goal_found":
            self._handle_goal_found(widget, scene, event, run_time)

    def get_supported_events(self) -> list[str]:
        """Get VizEvent types this adapter handles."""
        return ["enqueue", "dequeue", "goal_found"]

    def _handle_enqueue(
        self, widget: GridWidget, scene: Any, event: VizEvent, run_time: float
    ):
        """Handle enqueue event by calling widget's visual methods."""
        if PayloadKey.NODE in event.payload:
            pos = event.payload[PayloadKey.NODE]
            # Call pure visual method
            widget.highlight_cell(pos, "#0000FF", opacity=0.7)
            scene.play(widget.cell_map[pos].animate, run_time=run_time)

    def _handle_dequeue(
        self, widget: GridWidget, scene: Any, event: VizEvent, run_time: float
    ):
        """Handle dequeue event by calling widget's visual methods."""
        if PayloadKey.NODE in event.payload:
            pos = event.payload[PayloadKey.NODE]
            # Call pure visual method
            widget.highlight_cell(pos, "#808080", opacity=0.5)
            scene.play(widget.cell_map[pos].animate, run_time=run_time)

    def _handle_goal_found(
        self, widget: GridWidget, scene: Any, event: VizEvent, run_time: float
    ):
        """Handle goal_found event by calling widget's visual methods."""
        if PayloadKey.NODE in event.payload:
            pos = event.payload[PayloadKey.NODE]
            # Call pure visual method
            flash_anim = widget.flash_cell(pos, "#FFA500", scale_factor=1.3)
            scene.play(flash_anim, run_time=run_time)


class QueueWidgetAdapter:
    """Adapter that processes VizEvents for QueueWidget."""

    def update(
        self, widget: QueueWidget, scene: Any, event: VizEvent, run_time: float
    ) -> None:
        """Process VizEvent and call appropriate QueueWidget visual methods.

        Args:
            widget: QueueWidget instance
            scene: Manim scene instance
            event: VizEvent to process
            run_time: Duration for any animations
        """
        if event.type == "enqueue":
            self._handle_enqueue(widget, scene, event, run_time)
        elif event.type == "dequeue":
            self._handle_dequeue(widget, scene, event, run_time)

    def get_supported_events(self) -> list[str]:
        """Get VizEvent types this adapter handles."""
        return ["enqueue", "dequeue"]

    def _handle_enqueue(
        self, widget: QueueWidget, scene: Any, event: VizEvent, run_time: float
    ):
        """Handle enqueue event by calling widget's visual methods."""
        if PayloadKey.NODE in event.payload:
            node = event.payload[PayloadKey.NODE]
            # Call pure visual method
            label = f"({node[0]},{node[1]})"
            element_widget = widget.add_element(node, label=label)

            # Animate the new element
            if element_widget:
                scene.add(element_widget)
                scene.play(element_widget.animate, run_time=run_time)

    def _handle_dequeue(
        self, widget: QueueWidget, scene: Any, event: VizEvent, run_time: float
    ):
        """Handle dequeue event by calling widget's visual methods."""
        # Call pure visual method
        removed_data, removed_widget = widget.remove_element(0)

        if removed_widget:
            # Animate removal
            from manim import FadeOut

            scene.play(FadeOut(removed_widget), run_time=run_time)


class WidgetAdapterRegistry:
    """Registry for widget adapters."""

    def __init__(self):
        self._adapters: dict[str, WidgetAdapter] = {}
        self._setup_default_adapters()

    def _setup_default_adapters(self):
        """Register default widget adapters."""
        self.register("grid", GridWidgetAdapter())
        self.register("queue", QueueWidgetAdapter())

    def register(self, widget_type: str, adapter: WidgetAdapter):
        """Register adapter for widget type."""
        self._adapters[widget_type] = adapter

    def get_adapter(self, widget_type: str) -> WidgetAdapter:
        """Get adapter for widget type."""
        if widget_type not in self._adapters:
            raise ValueError(f"No adapter registered for widget type: {widget_type}")
        return self._adapters[widget_type]

    def get_supported_events(self, widget_type: str) -> list[str]:
        """Get supported events for widget type."""
        adapter = self.get_adapter(widget_type)
        return adapter.get_supported_events()


# Global adapter registry instance
adapter_registry = WidgetAdapterRegistry()
