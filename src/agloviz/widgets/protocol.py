"""Widget protocol for ALGOViz visualizations.

This module defines the Widget protocol that all visualization components must implement.
"""

from typing import Any, Protocol

from agloviz.core.events import VizEvent


class Widget(Protocol):
    """Widget contract as specified in design document.
    
    All widgets are stateless at creation and hold internal state only while active in a scene.
    """

    def show(self, scene: Any, **kwargs) -> None:
        """Initialize and render widget (enter animation).
        
        Args:
            scene: Manim scene instance
            **kwargs: Widget-specific configuration parameters
        """
        ...

    def hide(self, scene: Any) -> None:
        """Clean teardown (exit animation).
        
        Args:
            scene: Manim scene instance
        """
        ...


class WidgetAdapter(Protocol):
    """Event processing adapter for widgets.
    
    Adapters handle VizEvents and call appropriate widget visual methods.
    This separates event processing logic from pure visual operations.
    """

    def update(self, widget: Widget, scene: Any, event: VizEvent, run_time: float) -> None:
        """Process VizEvent and call appropriate widget methods.
        
        Args:
            widget: Target widget instance
            scene: Manim scene instance
            event: VizEvent to process
            run_time: Duration for any animations
        """
        ...

    def get_supported_events(self) -> list[str]:
        """Get list of VizEvent types this adapter can handle.
        
        Returns:
            List of event type strings
        """
        ...

