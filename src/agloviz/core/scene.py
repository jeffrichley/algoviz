"""Scene Configuration System for Widget Architecture v2.0 (Hydra-zen First).

This module provides the hydra-zen first declarative scene configuration system that enables
algorithm-agnostic widget management and event routing through structured configs.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field
from hydra_zen import builds, make_config, instantiate
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig, OmegaConf
from ..config.models import SceneConfig


class EventBinding(BaseModel):
    """Binds algorithm events to widget actions with parameter templates.
    
    Example:
        EventBinding(
            widget="grid",
            action="highlight_element", 
            params={"identifier": "${event_data:event.node}", "style": "frontier"},
            order=1
        )
    """
    widget: str = Field(..., description="Target widget name")
    action: str = Field(..., description="Widget method to call")
    params: dict[str, Any] = Field(default_factory=dict, description="Method parameters with template support")
    order: int = Field(default=1, description="Execution order for multiple bindings")
    condition: str | None = Field(default=None, description="Optional condition for execution")


class WidgetSpec(BaseModel):
    """Hydra-zen widget specification with _target_ support.
    
    Example:
        WidgetSpec(
            name="grid",
            target="agloviz.widgets.domains.pathfinding.PathfindingGrid",
            width=10,
            height=10,
            cell_size=0.5
        )
    """
    name: str = Field(..., description="Unique widget identifier")
    target: str = Field(..., description="Full path to widget class")
    
    class Config:
        extra = "allow"  # Allow widget-specific parameters


# SceneConfig is now imported from config.models - no duplicate definition needed


# Hydra-zen structured configs for scene configuration components
EventBindingConfigZen = builds(
    EventBinding,
    zen_partial=True,
    populate_full_signature=True
)

WidgetSpecConfigZen = builds(
    WidgetSpec,
    zen_partial=True,
    populate_full_signature=True
)

SceneConfigZen = builds(
    SceneConfig,
    zen_partial=True,
    populate_full_signature=True
)


# Scene configuration examples using hydra-zen composition
# Simplified scene config using existing widgets
BFSSceneConfigZen = make_config(
    name="bfs_pathfinding",
    algorithm="bfs",
    widgets={
        "grid": {
            "_target_": "agloviz.widgets.grid.GridWidget"
        },
        "queue": {
            "_target_": "agloviz.widgets.queue.QueueWidget"
        }
    },
    event_bindings={
        "enqueue": [
            {
                "widget": "queue",
                "action": "add_element",
                "params": {"element": "node"},
                "order": 1
            },
            {
                "widget": "grid",
                "action": "show_frontier",
                "params": {"positions": ["pos"]},
                "order": 2
            }
        ],
        "dequeue": [
            {
                "widget": "queue",
                "action": "remove_element",
                "params": {"index": 0},
                "order": 1
            }
        ]
    },
    timing_overrides={
        "events": 0.8,
        "effects": 0.5
    },
    hydra_defaults=["_self_"]
)


def register_scene_base_configs(cs: ConfigStore):
    """Register base scene configuration templates."""
    cs.store(name="scene_config_base", node=SceneConfigZen)
    cs.store(name="event_binding_base", node=EventBindingConfigZen)
    cs.store(name="widget_spec_base", node=WidgetSpecConfigZen)


def register_algorithm_scene_configs(cs: ConfigStore):
    """Register algorithm-specific scene configurations."""
    # Pathfinding algorithms
    cs.store(group="scene", name="bfs_pathfinding", node=BFSSceneConfigZen)
    
    # Note: Additional scene configs can be added here as they're developed
    # cs.store(group="scene", name="dfs_pathfinding", node=DFSSceneConfigZen)
    # cs.store(group="scene", name="dijkstra_pathfinding", node=DijkstraSceneConfigZen)


def register_scene_configs():
    """Register all scene structured configs with ConfigStore."""
    cs = ConfigStore.instance()
    
    # Register base scene configuration templates
    register_scene_base_configs(cs)
    
    # Register algorithm-specific scene configurations
    register_algorithm_scene_configs(cs)


class SceneEngine:
    """Manages widget lifecycle and event routing using hydra-zen instantiation."""
    
    def __init__(self, scene_config: SceneConfig, timing_config=None):
        self.timing_config = timing_config
        self.widgets: Dict[str, Any] = {}
        self.event_bindings: Dict[str, list] = {}
        
        # Setup parameter resolvers
        self._setup_resolvers()
        
        # Store the SceneConfig object (zen().hydra_main() provides instantiated objects)
        self.scene_data = scene_config
        
        # Create OmegaConf version for template resolution (excluding widgets that can't serialize)
        config_dict = scene_config.model_dump()
        config_dict.pop('widgets', None)  # Remove widgets - they're already instantiated
        self.scene_config = OmegaConf.create(config_dict)
        
        # Initialize scene
        self._initialize_scene()

    def get_scene_name(self) -> str:
        """Get scene configuration name."""
        return self.scene_data.name

    def get_scene_algorithm(self) -> str:
        """Get scene target algorithm."""
        return self.scene_data.algorithm

    def get_widget_count(self) -> int:
        """Get number of widgets in scene."""
        return len(self.widgets)

    def list_widget_names(self) -> list[str]:
        """Get list of widget names in scene."""
        return list(self.widgets.keys())
    
    def _setup_resolvers(self):
        """Setup OmegaConf resolvers for parameter templates."""
        # Import and register custom resolvers from core.resolvers
        try:
            from agloviz.core.resolvers import register_custom_resolvers
            register_custom_resolvers()
        except ImportError:
            # Fallback to basic resolvers if custom ones not available
            OmegaConf.register_new_resolver("event_data", lambda path: f"${{{path}}}")
            OmegaConf.register_new_resolver("timing_value", lambda key: 1.0)
    
    def _initialize_scene(self):
        """Initialize scene using hydra-zen instantiation."""
        # Get widgets - handle both dict and OmegaConf access patterns
        widgets = None
        if hasattr(self.scene_data, 'widgets'):
            widgets = self.scene_data.widgets
        elif isinstance(self.scene_data, dict) and 'widgets' in self.scene_data:
            widgets = self.scene_data['widgets']
        
        if widgets is None:
            raise ValueError(f"No widgets found in scene_data: {self.scene_data}")
        
        # Initialize widgets from structured configs
        self._initialize_widgets(widgets)
        
        # Get event_bindings - handle both dict and OmegaConf access patterns
        event_bindings = None
        if hasattr(self.scene_data, 'event_bindings'):
            event_bindings = self.scene_data.event_bindings
        elif isinstance(self.scene_data, dict) and 'event_bindings' in self.scene_data:
            event_bindings = self.scene_data['event_bindings']
        
        if event_bindings:
            # Setup event bindings
            self._setup_event_bindings(event_bindings)
    
    def _initialize_widgets(self, widget_specs: Dict[str, Any]):
        """Initialize widgets using hydra-zen instantiation."""
        for widget_name, widget_spec in widget_specs.items():
            try:
                # Check if widget is already instantiated (from ConfigStore resolution)
                if hasattr(widget_spec, 'show') and hasattr(widget_spec, 'hide'):
                    # Already a widget instance
                    widget_instance = widget_spec
                elif hasattr(widget_spec, '_target_'):
                    # Structured config that needs instantiation
                    widget_instance = instantiate(widget_spec)
                elif isinstance(widget_spec, dict) and '_target_' in widget_spec:
                    # Dict config that needs instantiation
                    widget_instance = instantiate(widget_spec)
                else:
                    # Handle WidgetSpec objects or other structured configs
                    if hasattr(widget_spec, '_target_'):
                        widget_instance = instantiate(widget_spec)
                    else:
                        raise ValueError(f"Widget spec for '{widget_name}' missing _target_ or is not a widget instance")
                
                self.widgets[widget_name] = widget_instance
            except Exception as e:
                raise ValueError(f"Failed to initialize widget '{widget_name}': {e}") from e
    
    def _setup_event_bindings(self, binding_specs: Dict[str, list]):
        """Setup event bindings from structured configs."""
        for event_name, bindings in binding_specs.items():
            resolved_bindings = []
            for binding_spec in bindings:
                if hasattr(binding_spec, '_target_'):
                    # Structured config event binding
                    binding = instantiate(binding_spec)
                elif isinstance(binding_spec, dict):
                    # Dictionary representation
                    binding = EventBinding(**binding_spec)
                else:
                    # Direct EventBinding object
                    binding = binding_spec
                resolved_bindings.append(binding)
            
            # Sort by execution order
            self.event_bindings[event_name] = sorted(resolved_bindings, key=lambda b: b.order)
    
    def handle_event(self, event: Any):
        """Route algorithm event to appropriate widget actions."""
        event_type = getattr(event, 'type', str(event))
        
        if event_type not in self.event_bindings:
            return
        
        # Execute bindings in order
        for binding in self.event_bindings[event_type]:
            self._execute_binding(binding, event)
    
    def _execute_binding(self, binding: EventBinding, event: Any):
        """Execute event binding with parameter resolution."""
        # Check condition if specified
        if binding.condition and not self._evaluate_condition(binding.condition, event):
            return
        
        # Get target widget
        if binding.widget not in self.widgets:
            raise ValueError(f"Widget '{binding.widget}' not found in scene")
        
        widget = self.widgets[binding.widget]
        
        # Resolve parameters using OmegaConf with context
        resolved_params = self._resolve_parameters(binding.params, event)
        
        # Execute action
        if not hasattr(widget, binding.action):
            raise ValueError(f"Widget '{binding.widget}' has no action '{binding.action}'")
        
        action_method = getattr(widget, binding.action)
        action_method(**resolved_params)
    
    def _resolve_parameters(self, params: dict, event: Any) -> dict:
        """Resolve parameter templates using OmegaConf."""
        if not params:
            return {}
        
        # Create context for parameter resolution
        context = {
            'event': event,
            'config': self.scene_config,
            'timing': self.timing_config,
            'widgets': {name: widget for name, widget in self.widgets.items()}
        }
        
        # Create parameter config for resolution
        params_config = OmegaConf.create(params)
        
        # Resolve parameters with context
        try:
            with OmegaConf.structured(context):
                resolved_params = OmegaConf.to_container(params_config, resolve=True)
            return resolved_params
        except Exception as e:
            # Fallback to direct parameter passing if resolution fails
            return params
    
    def _evaluate_condition(self, condition: str, event: Any) -> bool:
        """Evaluate condition string for conditional execution."""
        # Simple condition evaluation - can be enhanced
        if not condition:
            return True
        
        try:
            # Resolve condition template
            context = {'event': event, 'config': self.scene_config}
            condition_config = OmegaConf.create({"condition": condition})
            
            with OmegaConf.structured(context):
                resolved_condition = OmegaConf.to_container(condition_config, resolve=True)["condition"]
            
            # Simple boolean evaluation
            if isinstance(resolved_condition, bool):
                return resolved_condition
            elif isinstance(resolved_condition, str):
                return resolved_condition.lower() == 'true'
            else:
                return bool(resolved_condition)
        except Exception:
            return True  # Default to executing if condition evaluation fails
    
    def get_widget(self, name: str) -> Any:
        """Get widget by name."""
        return self.widgets.get(name)
    
    def get_scene_config(self) -> DictConfig:
        """Get the scene configuration."""
        return self.scene_config


def create_scene_from_config_store(scene_name: str, **overrides) -> SceneEngine:
    """Create SceneEngine from ConfigStore configuration."""
    cs = ConfigStore.instance()
    
    # Handle the nested ConfigStore structure
    if "scene" not in cs.repo:
        raise ValueError(f"No scene configurations found in ConfigStore")
    
    scene_config_name = scene_name + ".yaml"
    if scene_config_name not in cs.repo["scene"]:
        available_scenes = list(cs.repo["scene"].keys())
        raise ValueError(f"Scene '{scene_name}' not found in ConfigStore. Available: {available_scenes}")
    
    scene_config = cs.repo["scene"][scene_config_name].node
    
    # Apply overrides if provided
    if overrides:
        override_config = OmegaConf.create(overrides)
        scene_config = OmegaConf.merge(scene_config, override_config)
    
    return SceneEngine(scene_config)
