"""Widget protocol for ALGOViz visualizations.

This module defines the Widget protocol that all visualization components must implement.
"""

from typing import Protocol, Any
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
    
    def update(self, scene: Any, event: VizEvent, run_time: float) -> None:
        """React to VizEvents or storyboard beats.
        
        Args:
            scene: Manim scene instance
            event: VizEvent to process
            run_time: Duration for any animations
        """
        ...
    
    def hide(self, scene: Any) -> None:
        """Clean teardown (exit animation).
        
        Args:
            scene: Manim scene instance
        """
        ...
