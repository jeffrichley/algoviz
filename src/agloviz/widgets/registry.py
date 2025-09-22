"""Component registry for widget lifecycle management.

This module provides the ComponentRegistry for managing widget factories and instances.
Updated to support hydra-zen instantiation patterns while maintaining backward compatibility.
"""

from collections.abc import Callable
from typing import Any

from hydra_zen import builds, instantiate
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf

from agloviz.core.errors import RegistryError
from .protocol import Widget


class ComponentRegistry:
    """Component registry for widget lifecycle management.
    
    The registry acts as a service locator and dependency injector,
    decoupling visualization logic from algorithm adapters and the Director.
    
    Updated to support both legacy factory patterns and hydra-zen instantiation.
    """

    def __init__(self):
        # Legacy factory pattern support
        self._registry: dict[str, Callable[[], Widget]] = {}
        
        # Hydra-zen pattern support
        self.cs = ConfigStore.instance()
        self._setup_widget_configs()

    def _setup_widget_configs(self):
        """Register widget structured configs with ConfigStore."""
        # Register basic widget configurations
        self._register_basic_widgets()
    
    def _register_basic_widgets(self):
        """Register basic widget configurations."""
        # For STEP 3, we'll register simple widget specs without string targets
        # This avoids the builds() string target issue while demonstrating the pattern
        
        # Grid widget configuration
        self.cs.store(group="widget", name="grid", node={
            "_target_": "agloviz.widgets.grid.GridWidget"
        })
        
        # Queue widget configuration  
        self.cs.store(group="widget", name="queue", node={
            "_target_": "agloviz.widgets.queue.QueueWidget"
        })

    # Legacy factory pattern methods (maintained for backward compatibility)
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
            # Include all available widgets (both legacy and hydra-zen) in error message
            available = self.list_widgets()
            raise RegistryError.missing_component(name, available)
        return self._registry[name]()

    # New hydra-zen pattern methods
    def create_widget(self, name: str, **overrides) -> Widget:
        """Create widget using hydra-zen instantiation.
        
        Args:
            name: Widget name to instantiate
            **overrides: Parameter overrides for widget configuration
            
        Returns:
            Widget instance created via hydra-zen
            
        Raises:
            RegistryError: If widget configuration not found
        """
        # Check if widget config exists in ConfigStore
        if "widget" not in self.cs.repo or name + ".yaml" not in self.cs.repo["widget"]:
            # Fallback to legacy factory pattern
            if name in self._registry:
                return self._registry[name]()
            
            available_zen = list(self.cs.repo.get("widget", {}).keys()) if "widget" in self.cs.repo else []
            available_legacy = list(self._registry.keys())
            available = available_zen + available_legacy
            raise RegistryError.missing_component(name, available)
        
        # Get widget config from ConfigStore
        widget_config = self.cs.repo["widget"][name + ".yaml"].node
        
        # Apply parameter overrides
        if overrides:
            override_config = OmegaConf.create(overrides)
            widget_config = OmegaConf.merge(widget_config, override_config)
        
        # Instantiate using hydra-zen
        return instantiate(widget_config)
    
    def create_widget_from_spec(self, widget_spec: dict[str, Any]) -> Widget:
        """Create widget from widget specification dict.
        
        Args:
            widget_spec: Widget specification with _target_ and parameters
            
        Returns:
            Widget instance created via hydra-zen
        """
        if "_target_" not in widget_spec:
            raise RegistryError(
                issue="Widget spec missing _target_ field",
                component_type="widget_spec",
                suggestions=["Add '_target_' field pointing to widget class"]
            )
        
        return instantiate(widget_spec)

    def list_widgets(self) -> list[str]:
        """List all registered widget names.
        
        Returns:
            Sorted list of registered widget names (both legacy and hydra-zen)
        """
        legacy_widgets = list(self._registry.keys())
        zen_widgets = []
        
        if "widget" in self.cs.repo:
            zen_widgets = [name.replace(".yaml", "") for name in self.cs.repo["widget"].keys()]
        
        all_widgets = list(set(legacy_widgets + zen_widgets))
        return sorted(all_widgets)

    def clear(self) -> None:
        """Clear all registrations (for testing).
        
        This method is primarily used in test cleanup to ensure test isolation.
        """
        self._registry.clear()
        # Note: We don't clear ConfigStore as it's a singleton and may be used elsewhere
