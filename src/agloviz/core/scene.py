"""Scene Configuration System for Widget Architecture v2.0 (Hydra-zen First).

This module provides the hydra-zen first declarative scene configuration system that enables
algorithm-agnostic widget management and event routing through structured configs.
"""

from typing import Any

from hydra.core.config_store import ConfigStore
from hydra_zen import builds, instantiate, make_config
from omegaconf import DictConfig, OmegaConf
from pydantic import BaseModel, Field

from ..config.models import SceneConfig
from .storyboard import Beat


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
    params: dict[str, Any] = Field(
        default_factory=dict, description="Method parameters with template support"
    )
    order: int = Field(default=1, description="Execution order for multiple bindings")
    condition: str | None = Field(
        default=None, description="Optional condition for execution"
    )


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
    EventBinding, zen_partial=True, populate_full_signature=True
)

WidgetSpecConfigZen = builds(WidgetSpec, zen_partial=True, populate_full_signature=True)

SceneConfigZen = builds(SceneConfig, zen_partial=True, populate_full_signature=True)


# Scene configuration examples using hydra-zen composition
# Simplified scene config using existing widgets
BFSSceneConfigZen = make_config(
    name="bfs_pathfinding",
    algorithm="bfs",
    widgets={
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"},
    },
    event_bindings={
        "enqueue": [
            {
                "widget": "queue",
                "action": "add_element",
                "params": {"element": "node"},
                "order": 1,
            },
            {
                "widget": "grid",
                "action": "show_frontier",
                "params": {"positions": ["pos"]},
                "order": 2,
            },
        ],
        "dequeue": [
            {
                "widget": "queue",
                "action": "remove_element",
                "params": {"index": 0},
                "order": 1,
            }
        ],
    },
    timing_overrides={"events": 0.8, "effects": 0.5},
    hydra_defaults=["_self_"],
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
        self.widgets: dict[str, Any] = {}
        self.event_bindings: dict[str, list] = {}

        # Setup parameter resolvers
        self._setup_resolvers()

        # Store the SceneConfig object (zen().hydra_main() provides instantiated objects)
        self.scene_data = scene_config

        # Create OmegaConf version for template resolution (excluding widgets that can't serialize)
        config_dict = scene_config.model_dump()
        config_dict.pop(
            "widgets", None
        )  # Remove widgets - they're already instantiated
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
        if hasattr(self.scene_data, "widgets"):
            widgets = self.scene_data.widgets
        elif isinstance(self.scene_data, dict) and "widgets" in self.scene_data:
            widgets = self.scene_data["widgets"]

        if widgets is None:
            raise ValueError(f"No widgets found in scene_data: {self.scene_data}")

        # Initialize widgets from structured configs
        self._initialize_widgets(widgets)

        # Get event_bindings - handle both dict and OmegaConf access patterns
        event_bindings = None
        if hasattr(self.scene_data, "event_bindings"):
            event_bindings = self.scene_data.event_bindings
        elif isinstance(self.scene_data, dict) and "event_bindings" in self.scene_data:
            event_bindings = self.scene_data["event_bindings"]

        if event_bindings:
            # Setup event bindings
            self._setup_event_bindings(event_bindings)

    def _initialize_widgets(self, widget_specs: dict[str, Any]):
        """Initialize widgets using hydra-zen instantiation."""
        for widget_name, widget_spec in widget_specs.items():
            try:
                # Check if widget is already instantiated (from ConfigStore resolution)
                if hasattr(widget_spec, "show") and hasattr(widget_spec, "hide"):
                    # Already a widget instance
                    widget_instance = widget_spec
                elif hasattr(widget_spec, "_target_"):
                    # Structured config that needs instantiation
                    widget_instance = instantiate(widget_spec)
                elif isinstance(widget_spec, dict) and "_target_" in widget_spec:
                    # Dict config that needs instantiation
                    widget_instance = instantiate(widget_spec)
                else:
                    # Handle WidgetSpec objects or other structured configs
                    if hasattr(widget_spec, "_target_"):
                        widget_instance = instantiate(widget_spec)
                    else:
                        raise ValueError(
                            f"Widget spec for '{widget_name}' missing _target_ or is not a widget instance"
                        )

                self.widgets[widget_name] = widget_instance
            except Exception as e:
                raise ValueError(
                    f"Failed to initialize widget '{widget_name}': {e}"
                ) from e

    def _setup_event_bindings(self, binding_specs: dict[str, list]):
        """Setup event bindings from structured configs."""
        for event_name, bindings in binding_specs.items():
            resolved_bindings = []
            for binding_spec in bindings:
                if hasattr(binding_spec, "_target_"):
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
            self.event_bindings[event_name] = sorted(
                resolved_bindings, key=lambda b: b.order
            )

    def handle_event(self, event: Any):
        """Route algorithm event to appropriate widget actions."""
        event_type = getattr(event, "type", str(event))

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

        # Validate parameters before resolution
        self._validate_parameters(binding.params)

        # Resolve parameters using OmegaConf with context
        resolved_params = self._resolve_parameters(binding.params, event)

        # Execute action
        if not hasattr(widget, binding.action):
            raise ValueError(
                f"Widget '{binding.widget}' has no action '{binding.action}'"
            )

        action_method = getattr(widget, binding.action)
        action_method(**resolved_params)

    def _resolve_parameters(self, params: dict, event: Any) -> dict:
        """Resolve parameter templates using OmegaConf with ResolverContext."""
        if not params:
            return {}

        # Import ResolverContext for proper context management
        from agloviz.core.resolvers import ResolverContext

        # Create context for parameter resolution
        context = ResolverContext(
            event=event,
            config=self.scene_config,
            timing=self.timing_config,
            widgets=dict(self.widgets),
        )

        # Create parameter config for resolution
        params_config = OmegaConf.create(params)

        # Resolve parameters with context
        try:
            with context:
                resolved_params = OmegaConf.to_container(params_config, resolve=True)
            return resolved_params
        except Exception:
            # Fallback to direct parameter passing if resolution fails
            return params

    def _validate_parameters(self, params: dict) -> None:
        """Validate parameter templates before resolution."""
        if not params:
            return

        from agloviz.core.resolvers import validate_resolver_syntax

        for _key, value in params.items():
            if (
                isinstance(value, str)
                and value.startswith("${")
                and value.endswith("}")
            ):
                if not validate_resolver_syntax(value):
                    raise ValueError(f"Invalid parameter template syntax: {value}")

    def _evaluate_condition(self, condition: str, event: Any) -> bool:
        """Evaluate condition string for conditional execution."""
        # Simple condition evaluation - can be enhanced
        if not condition:
            return True

        try:
            # Resolve condition template
            context = {"event": event, "config": self.scene_config}
            condition_config = OmegaConf.create({"condition": condition})

            with OmegaConf.structured(context):
                resolved_condition = OmegaConf.to_container(
                    condition_config, resolve=True
                )["condition"]

            # Simple boolean evaluation
            if isinstance(resolved_condition, bool):
                return resolved_condition
            elif isinstance(resolved_condition, str):
                return resolved_condition.lower() == "true"
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

    def _is_scene_action(self, action_name: str) -> bool:
        """Check if action is a scene-level action (show_title, outro, etc.)."""
        scene_actions = {"show_title", "outro", "fade_in", "fade_out", "show_widgets"}
        return action_name in scene_actions

    def _is_algorithm_action(self, action_name: str) -> bool:
        """Check if action is algorithm-specific (place_start, celebrate_goal, etc.)."""
        return (
            hasattr(self.scene_data, "action_handlers")
            and action_name in self.scene_data.action_handlers
        )

    def _is_event_action(self, action_name: str) -> bool:
        """Check if action is event processing (play_events, pause_events, etc.)."""
        event_actions = {"play_events", "pause_events", "resume_events"}
        return action_name in event_actions

    def _get_available_actions(self) -> list[str]:
        """Get list of available actions for error messages."""
        actions = []

        # Add scene actions
        actions.extend(["show_title", "outro", "fade_in", "fade_out", "show_widgets"])

        # Add algorithm actions from scene config
        if hasattr(self.scene_data, "action_handlers"):
            actions.extend(self.scene_data.action_handlers.keys())

        # Add event actions
        actions.extend(["play_events", "pause_events", "resume_events"])

        return sorted(actions)

    def execute_beat(self, beat: Beat, run_time: float, context: dict) -> None:
        """Facade method - handles ALL action types."""

        if self._is_scene_action(beat.action):
            self._execute_scene_action(beat.action, beat.args, run_time, context)

        elif self._is_algorithm_action(beat.action):
            self._execute_algorithm_action(beat.action, beat.args, run_time, context)

        elif self._is_event_action(beat.action):
            self._execute_event_action(beat.action, beat.args, run_time, context)

        else:
            available = self._get_available_actions()
            raise ValueError(f"Unknown action '{beat.action}'. Available: {available}")

    def _execute_scene_action(
        self, action_name: str, args: dict, run_time: float, context: dict
    ):
        """Execute scene-level actions."""

        if action_name == "show_title":
            self._execute_show_title(args, run_time, context)
        elif action_name == "outro":
            self._execute_outro(args, run_time, context)
        elif action_name == "show_widgets":
            self._execute_show_widgets(args, run_time, context)
        else:
            raise ValueError(f"Unknown scene action: {action_name}")

    def _execute_show_title(self, args: dict, run_time: float, context: dict):
        """Show title card - implementation will be added in rendering phase."""
        # Placeholder for rendering integration
        pass

    def _execute_outro(self, args: dict, run_time: float, context: dict):
        """Show outro - implementation will be added in rendering phase."""
        # Placeholder for rendering integration
        pass

    def _execute_show_widgets(self, args: dict, run_time: float, context: dict):
        """Show widgets from scene configuration."""
        for widget_name, enabled in args.items():
            if enabled and isinstance(enabled, bool):
                widget = self.get_widget(widget_name)
                if widget:
                    widget.show(self.scene)

    def _execute_algorithm_action(
        self, action_name: str, args: dict, run_time: float, context: dict
    ):
        """Execute algorithm-specific actions from scene configuration."""

        if not hasattr(self.scene_data, "action_handlers"):
            raise ValueError("Scene configuration has no action handlers")

        if action_name not in self.scene_data.action_handlers:
            available = list(self.scene_data.action_handlers.keys())
            raise ValueError(
                f"Action '{action_name}' not in scene config. Available: {available}"
            )

        # Get handler from scene configuration
        handler = self.scene_data.action_handlers[action_name]

        # Execute with full context
        handler(self.scene, args, run_time, context)

    def _execute_event_action(
        self, action_name: str, args: dict, run_time: float, context: dict
    ):
        """Execute event processing actions."""

        if action_name == "play_events":
            self._execute_play_events(args, run_time, context)
        else:
            raise ValueError(f"Unknown event action: {action_name}")

    def _execute_play_events(self, args: dict, run_time: float, context: dict):
        """Play algorithm events with scene configuration routing."""

        # Get algorithm and scenario
        algorithm = args.get("algorithm")
        scenario_name = args.get("scenario")

        if not algorithm:
            raise ValueError("play_events requires 'algorithm' parameter")

        # Get adapter using hydra-zen
        from agloviz.adapters.registry import AdapterRegistry
        from agloviz.core.scenario import ScenarioLoader

        adapter_class = AdapterRegistry.get(algorithm)
        adapter = adapter_class()

        # Load scenario
        scenario = ScenarioLoader.load(scenario_name) if scenario_name else None

        # Generate events from algorithm
        events = list(adapter.run(scenario))

        # Process each event through scene configuration
        for event in events:
            self.handle_event(event)


def create_scene_from_config_store(scene_name: str, **overrides) -> SceneEngine:
    """Create SceneEngine from ConfigStore configuration."""
    cs = ConfigStore.instance()

    # Handle the nested ConfigStore structure
    if "scene" not in cs.repo:
        raise ValueError("No scene configurations found in ConfigStore")

    scene_config_name = scene_name + ".yaml"
    if scene_config_name not in cs.repo["scene"]:
        available_scenes = list(cs.repo["scene"].keys())
        raise ValueError(
            f"Scene '{scene_name}' not found in ConfigStore. Available: {available_scenes}"
        )

    scene_config = cs.repo["scene"][scene_config_name].node

    # Apply overrides if provided
    if overrides:
        override_config = OmegaConf.create(overrides)
        scene_config = OmegaConf.merge(scene_config, override_config)

    return SceneEngine(scene_config)
