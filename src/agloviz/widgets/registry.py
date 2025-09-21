"""Component registry for widget lifecycle management.

This module provides the ComponentRegistry for managing widget factories and instances.
"""

from typing import Callable, Dict
from .protocol import Widget
from agloviz.core.errors import RegistryError


class ComponentRegistry:
    """Component registry for widget lifecycle management.
    
    The registry acts as a service locator and dependency injector,
    decoupling visualization logic from algorithm adapters and the Director.
    """
    
    def __init__(self):
        self._registry: Dict[str, Callable[[], Widget]] = {}
    
    def register(self, name: str, factory: Callable[[], Widget]) -> None:
        """Register widget factory once at startup.
        
        Args:
            name: Widget name for lookup
            factory: Factory function that creates widget instances
            
        Raises:
            RegistryError: If widget name is already registered
        """
        if name in self._registry:
            raise RegistryError.collision(f"Widget '{name}' is already registered")
        self._registry[name] = factory
    
    def get(self, name: str) -> Widget:
        """Retrieve a fresh widget instance for a scene.
        
        Args:
            name: Widget name to instantiate
            
        Returns:
            Fresh widget instance
            
        Raises:
            RegistryError: If widget name is not registered
        """
        if name not in self._registry:
            available = list(self._registry.keys())
            raise RegistryError.missing_component(name, available)
        return self._registry[name]()
    
    def list_widgets(self) -> list[str]:
        """List all registered widget names.
        
        Returns:
            Sorted list of registered widget names
        """
        return sorted(self._registry.keys())
    
    def clear(self) -> None:
        """Clear all registrations (for testing).
        
        This method is primarily used in test cleanup to ensure test isolation.
        """
        self._registry.clear()
