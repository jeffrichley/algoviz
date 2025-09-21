"""Widget system for ALGOViz visualizations.

This module provides the widget framework for creating reusable visualization
components that can be composed to build algorithm visualizations.
"""

from .protocol import Widget
from .registry import ComponentRegistry

# Global component registry instance
component_registry = ComponentRegistry()


def register_core_widgets() -> None:
    """Register all core widgets with the component registry."""
    try:
        # Lazy import to avoid Manim dependency issues during testing
        from .grid import GridWidget
        from .queue import QueueWidget
        
        component_registry.register("grid", lambda: GridWidget())
        component_registry.register("queue", lambda: QueueWidget())
    except ImportError:
        # If Manim is not available, register mock widgets for testing
        class MockWidget:
            def show(self, scene, **kwargs): pass
            def update(self, scene, event, run_time): pass
            def hide(self, scene): pass
        
        component_registry.register("grid", lambda: MockWidget())
        component_registry.register("queue", lambda: MockWidget())


def get_available_widgets() -> list[str]:
    """Get list of currently available widgets.
    
    Returns:
        List of registered widget names
    """
    return component_registry.list_widgets()


# Auto-register core widgets on import
register_core_widgets()

__all__ = [
    "Widget",
    "ComponentRegistry", 
    "component_registry",
    "register_core_widgets",
    "get_available_widgets"
]
