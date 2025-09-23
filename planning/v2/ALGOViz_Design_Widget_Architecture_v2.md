# ALGOViz Design Doc — Widget Architecture v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0 - Hydra-zen First)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Hydra-zen First Philosophy Integration)
**Supersedes:** planning/v1/ALGOViz_Design_Widget_Architecture_v2.md

---

## 1. Purpose

This document defines a complete architectural redesign of the ALGOViz widget system to address fundamental design flaws discovered during Phase 1.4 Director Implementation. The current widget system has BFS-specific pollution that prevents it from being truly generic and reusable across different algorithm types.

The new architecture establishes a **multi-level widget hierarchy** with **pure visual primitives**, **generic data structure abstractions**, and **domain-specific extensions**, all connected through a **hydra-zen first configuration system** with **declarative event binding** powered by **structured configs and ConfigStore**.

## 2. Integration with Hydra-zen First Philosophy

### 2.1 Alignment with Configuration System

**Consistent Architecture**: This widget architecture fully integrates with the **hydra-zen first** Configuration System (ALGOViz_Design_Config_System.md):
- Widget instantiation uses `builds()` and `instantiate()` patterns
- Scene configurations are structured configs registered with ConfigStore
- Parameter resolution uses OmegaConf templates and resolvers
- All configuration composition follows hydra-zen patterns

### 2.2 Alignment with DI Strategy

**Seamless DI Integration**: Widget system leverages the **hydra-zen first** DI Strategy (ALGOViz_Design_DI_Strategy_v2.md):
- Widget factories use structured config templates
- Scene Engine integrates with DI container patterns
- Event binding system uses hydra-zen parameter resolution
- Plugin system follows DI registration patterns

### 2.3 Enhanced Configuration-Driven Design

**Hydra-zen Native**: All widget configuration uses hydra-zen patterns:
- Widget specifications use `builds()` for type safety
- Scene configurations use `make_config()` for composition
- Event bindings use structured configs with static parameters (hydra-zen first)
- Dynamic parameters resolved at runtime using OmegaConf resolvers with event data
- Plugin integration through ConfigStore groups

## 3. Current Problems (BFS-Specific Pollution)

### 3.1 Director Pollution

The current Director implementation contains algorithm-specific actions that should not be in a generic orchestrator:

```python
# PROBLEMATIC: BFS-specific actions in generic Director
def _register_core_actions(self) -> None:
    self._actions.update({
        "place_start": self._action_place_start,      # Grid pathfinding concept
        "place_goal": self._action_place_goal,        # Goal-seeking algorithms only
        "place_obstacles": self._action_place_obstacles, # Obstacle-based scenarios
        "show_complexity": self._action_show_complexity, # Algorithm analysis
        "celebrate_goal": self._action_celebrate_goal,   # Goal achievement
    })
```

**Problems:**
- Sorting algorithms don't have start/goal/obstacles
- Tree algorithms don't use grids or obstacles  
- Graph algorithms may not have goals
- Director becomes bloated with domain-specific concepts

### 3.2 Widget System Pollution

Current "generic" widgets contain algorithm-specific assumptions:

#### GridWidget Pollution
```python
# PROBLEMATIC: Pathfinding concepts in "generic" grid
class GridWidget:
    def mark_frontier(self, pos):     # BFS/DFS concept
    def flash_goal(self, pos):        # Goal-seeking concept
    def mark_visited(self, pos):      # Traversal concept
```

#### QueueWidget Pollution
```python
# PROBLEMATIC: BFS-specific queue operations
class QueueWidget:
    def highlight_enqueue(self):      # BFS terminology
    def highlight_dequeue(self):      # BFS operations
```

#### Missing Widget Types
- **ArrayWidget**: No generic array visualization for sorting algorithms
- **TreeWidget**: No tree structure visualization
- **GraphWidget**: No arbitrary graph visualization (non-grid)
- **StackWidget**: No stack visualization for DFS
- **PriorityQueueWidget**: No heap visualization for Dijkstra/A*

### 3.3 Configuration System Gaps

- No hydra-zen structured configs for scene compositions
- No ConfigStore registration for widget templates
- No event parameter resolution system with OmegaConf resolvers
- Hard-coded widget relationships instead of composition

## 3.4 Architectural Separation: Widgets vs Events

### **Key Architectural Principle: Static Widget Configs + Dynamic Event Parameters**

The Widget Architecture v2.0 establishes a clear separation of concerns between widget configuration and event parameter resolution:

**Widget Configuration (Static - Hydra-zen First):**
- ✅ **Widget Properties**: Size, appearance, behavior set at configuration time
- ✅ **Widget Methods**: Available actions and their signatures defined in widget classes
- ✅ **Scene Composition**: Which widgets exist and their relationships
- ✅ **Event Bindings**: Which events trigger which widget actions (static routing)

**Event Parameters (Dynamic - Runtime Resolution):**
- ✅ **Dynamic Values**: Node positions, colors, weights resolved from algorithm execution
- ✅ **Event Data**: Algorithm-specific data passed through VizEvents
- ✅ **Parameter Resolution**: OmegaConf resolvers resolve templates with event context
- ✅ **Runtime Context**: Full access to event data, scene config, and timing config

**The Flow:**
1. **Configuration Time**: Widgets configured with static properties and event bindings
2. **Runtime**: Algorithm generates VizEvents with dynamic data
3. **SceneEngine**: Resolves dynamic parameters using OmegaConf resolvers
4. **Widget Methods**: Called with resolved parameters (static + dynamic)

**Benefits:**
- ✅ **Hydra-zen First**: Widget configs are pure and predictable
- ✅ **Runtime Flexibility**: Dynamic parameters resolved with full context
- ✅ **Clear Separation**: Configuration vs runtime behavior
- ✅ **Maintainability**: Single responsibility for each component

## 4. Core Widget Abstractions (Multi-Level Hierarchy)

### 4.1 Level 1: Primitive Visual Elements (Hydra-zen Configured)

**Philosophy**: Ultra-generic visual primitives configured through hydra-zen structured configs.

```python
from pydantic import BaseModel, Field
from hydra_zen import builds
from typing import Any, Protocol

class PrimitiveWidget(BaseModel):
    """Base class for all primitive visual elements."""
    class Config:
        arbitrary_types_allowed = True

class TokenWidget(PrimitiveWidget):
    """Draggable, highlightable visual token."""
    position: tuple[float, float] = (0.0, 0.0)
    size: float = 1.0
    color: str = "#FFFFFF"
    text: str | None = None
    
    def move_to(self, position: tuple[float, float], duration: float = 1.0):
        """Pure visual operation: move token to position."""
        
    def highlight(self, color: str, duration: float = 1.0):
        """Pure visual operation: change color temporarily."""
        
    def set_text(self, text: str):
        """Pure visual operation: update displayed text."""

class MarkerWidget(PrimitiveWidget):
    """Visual markers for special positions."""
    marker_type: str = "circle"  # circle, square, star, etc.
    color: str = "#FF0000"
    size: float = 1.0
    
    def show(self, position: tuple[float, float], duration: float = 1.0):
        """Pure visual operation: show marker at position."""
        
    def hide(self, duration: float = 1.0):
        """Pure visual operation: hide marker."""

class ConnectionWidget(PrimitiveWidget):
    """Visual connections between elements."""
    start_pos: tuple[float, float]
    end_pos: tuple[float, float]
    line_type: str = "solid"  # solid, dashed, dotted
    color: str = "#000000"
    width: float = 2.0
    
    def animate_draw(self, duration: float = 1.0):
        """Pure visual operation: animate line drawing."""
        
    def highlight(self, color: str, duration: float = 1.0):
        """Pure visual operation: temporarily change color."""

# Hydra-zen structured configs for primitives
TokenWidgetConfigZen = builds(
    TokenWidget,
    position="${token.position:[0.0, 0.0]}",
    size="${token.size:1.0}",
    color="${token.color:#FFFFFF}",
    text="${token.text:null}",
    zen_partial=True,
    populate_full_signature=True
)

MarkerWidgetConfigZen = builds(
    MarkerWidget,
    marker_type="${marker.type:circle}",
    color="${marker.color:#FF0000}",
    size="${marker.size:1.0}",
    zen_partial=True,
    populate_full_signature=True
)

ConnectionWidgetConfigZen = builds(
    ConnectionWidget,
    start_pos="${connection.start_pos}",
    end_pos="${connection.end_pos}",
    line_type="${connection.line_type:solid}",
    color="${connection.color:#000000}",
    width="${connection.width:2.0}",
    zen_partial=True,
    populate_full_signature=True
)
```

### 4.2 Level 2: Data Structure Abstractions (Hydra-zen Configured)

**Philosophy**: Generic data structure concepts configured through structured configs.

```python
from hydra_zen import builds, make_config

class LayoutEngine(BaseModel):
    """Base class for spatial arrangement of elements."""
    class Config:
        arbitrary_types_allowed = True

class LinearLayout(LayoutEngine):
    """Arranges elements in a line."""
    orientation: str = "horizontal"  # horizontal, vertical
    spacing: float = 1.0
    alignment: str = "center"  # start, center, end
    
    def position_elements(self, elements: list[TokenWidget]) -> dict[int, tuple[float, float]]:
        """Calculate positions for elements in linear arrangement."""

class Grid2DLayout(LayoutEngine):
    """Arranges elements in 2D grid."""
    width: int
    height: int
    cell_size: float = 1.0
    origin: tuple[float, float] = (0.0, 0.0)
    
    def position_elements(self, elements: list[TokenWidget]) -> dict[int, tuple[float, float]]:
        """Calculate positions for elements in grid arrangement."""
        
    def grid_to_position(self, row: int, col: int) -> tuple[float, float]:
        """Convert grid coordinates to visual position."""

class ContainerWidget(BaseModel):
    """Generic container for ordered elements."""
    elements: list[TokenWidget] = Field(default_factory=list)
    layout: LayoutEngine
    name: str
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_element(self, element: TokenWidget, index: int | None = None, animation: str = "slide_in"):
        """Add element to container with animation."""
        
    def remove_element(self, index: int, animation: str = "slide_out") -> TokenWidget:
        """Remove element from container with animation."""
        
    def highlight_element(self, index: int, style: str, duration: float = 1.0):
        """Highlight specific element in container."""
        
    def swap_elements(self, i: int, j: int, duration: float = 1.0):
        """Swap two elements with animation."""

# Hydra-zen structured configs for layouts
LinearLayoutConfigZen = builds(
    LinearLayout,
    orientation="${layout.orientation:horizontal}",
    spacing="${layout.spacing:1.0}",
    alignment="${layout.alignment:center}",
    zen_partial=True,
    populate_full_signature=True
)

Grid2DLayoutConfigZen = builds(
    Grid2DLayout,
    width="${layout.width:10}",
    height="${layout.height:10}",
    cell_size="${layout.cell_size:1.0}",
    origin="${layout.origin:[0.0, 0.0]}",
    zen_partial=True,
    populate_full_signature=True
)

# Hydra-zen structured configs for data structures
ArrayWidgetConfigZen = builds(
    "agloviz.widgets.structures.ArrayWidget",
    size="${array.size:10}",
    layout=LinearLayoutConfigZen,
    name="${array.name:array}",
    zen_partial=True,
    populate_full_signature=True
)

QueueWidgetConfigZen = builds(
    "agloviz.widgets.structures.QueueWidget",
    layout=LinearLayoutConfigZen,
    name="${queue.name:queue}",
    max_visible="${queue.max_visible:10}",
    zen_partial=True,
    populate_full_signature=True
)

StackWidgetConfigZen = builds(
    "agloviz.widgets.structures.StackWidget",
    layout=LinearLayoutConfigZen,
    name="${stack.name:stack}",
    zen_partial=True,
    populate_full_signature=True
)
```

### 4.3 Level 3: Semantic Data Structures (Domain-Specific Structured Configs)

**Philosophy**: Algorithm-specific patterns configured through specialized structured configs.

```python
from hydra_zen import builds

class PathfindingGrid(BaseModel):
    """Grid specialized for pathfinding algorithms."""
    width: int
    height: int
    layout: Grid2DLayout
    elements: list[TokenWidget]
    
    # Pathfinding-specific state
    start_pos: tuple[int, int] | None = None
    goal_pos: tuple[int, int] | None = None
    obstacles: set[tuple[int, int]] = Field(default_factory=set)
    
    def mark_start(self, pos: tuple[int, int]):
        """Mark position as start (pathfinding semantic)."""
        self.start_pos = pos
        index = pos[0] * self.width + pos[1]
        self.highlight_element(index, "start")
    
    def mark_goal(self, pos: tuple[int, int]):
        """Mark position as goal (pathfinding semantic)."""
        self.goal_pos = pos
        index = pos[0] * self.width + pos[1]
        self.highlight_element(index, "goal")
    
    def show_frontier(self, positions: list[tuple[int, int]]):
        """Show frontier positions (pathfinding semantic)."""
        for pos in positions:
            index = pos[0] * self.width + pos[1]
            self.highlight_element(index, "frontier")

class SortingArray(BaseModel):
    """Array specialized for sorting algorithms."""
    size: int
    layout: LinearLayout
    elements: list[TokenWidget]
    
    def compare_highlight(self, i: int, j: int, result: str, duration: float = 1.0):
        """Highlight comparison between two elements (sorting semantic)."""
        self.highlight_element(i, f"compare_{result}", duration)
        self.highlight_element(j, f"compare_{result}", duration)
    
    def partition_marker(self, pivot_index: int):
        """Show partition marker (sorting semantic)."""
        self.highlight_element(pivot_index, "pivot")
    
    def show_sorted_region(self, start: int, end: int):
        """Highlight sorted region (sorting semantic)."""
        for i in range(start, end + 1):
            self.highlight_element(i, "sorted")

# Domain-specific structured configs
PathfindingGridConfigZen = builds(
    PathfindingGrid,
    width="${grid.width:10}",
    height="${grid.height:10}",
    layout=Grid2DLayoutConfigZen,
    elements="${grid.elements:[]}",
    zen_partial=True,
    populate_full_signature=True
)

SortingArrayConfigZen = builds(
    SortingArray,
    size="${array.size:10}",
    layout=LinearLayoutConfigZen,
    elements="${array.elements:[]}",
    zen_partial=True,
    populate_full_signature=True
)
```

## 5. Hydra-zen Scene Configuration System

### 5.1 Scene Configuration with Structured Configs

```python
from hydra_zen import builds, make_config
from hydra.core.config_store import ConfigStore

class EventBinding(BaseModel):
    """Configuration for binding algorithm events to widget actions."""
    widget: str = Field(..., description="Name of target widget")
    action: str = Field(..., description="Widget method to call")
    params: dict[str, Any] = Field(default_factory=dict, description="Static parameters with dynamic templates")
    order: int = Field(1, description="Execution order")
    condition: str | None = Field(None, description="Optional condition")

class WidgetSpec(BaseModel):
    """Hydra-zen widget specification."""
    name: str = Field(..., description="Unique widget name")
    _target_: str = Field(..., description="Widget class path")
    
    class Config:
        extra = "allow"  # Allow widget-specific parameters

class SceneConfig(BaseModel):
    """Complete scene configuration using hydra-zen patterns."""
    widgets: dict[str, WidgetSpec] = Field(default_factory=dict)
    event_bindings: dict[str, list[EventBinding]] = Field(default_factory=dict)
    timing_overrides: dict[str, float] = Field(default_factory=dict)

# Scene configuration structured configs
EventBindingConfigZen = builds(
    EventBinding,
    widget="${binding.widget}",
    action="${binding.action}",
    params="${binding.params:{}}",
    order="${binding.order:1}",
    condition="${binding.condition:null}",
    zen_partial=True,
    populate_full_signature=True
)

WidgetSpecConfigZen = builds(
    WidgetSpec,
    name="${widget.name}",
    _target_="${widget._target_}",
    zen_partial=True,
    populate_full_signature=True
)

SceneConfigZen = builds(
    SceneConfig,
    widgets="${scene.widgets:{}}",
    event_bindings="${scene.event_bindings:{}}",
    timing_overrides="${scene.timing_overrides:{}}",
    zen_partial=True,
    populate_full_signature=True
)
```

### 5.2 BFS Scene Configuration (Hydra-zen Native)

```python
# BFS scene using hydra-zen composition
BFSSceneConfigZen = make_config(
    name="bfs_pathfinding",
    algorithm="bfs",
    widgets={
        "grid": builds(
            PathfindingGrid,
            width=10,
            height=10,
            layout=Grid2DLayoutConfigZen,
            zen_partial=True
        ),
        "queue": builds(
            "agloviz.widgets.structures.QueueWidget",
            layout=LinearLayoutConfigZen,
            name="queue",
            zen_partial=True
        ),
        "legend": builds(
            "agloviz.widgets.hud.LegendWidget",
            position="top_right",
            items=[
                {"label": "Start", "color": "#00FF00"},
                {"label": "Goal", "color": "#FF0000"},
                {"label": "Frontier", "color": "#FFFF00"},
                {"label": "Visited", "color": "#CCCCCC"}
            ],
            zen_partial=True
        )
    },
    event_bindings={
        "enqueue": [
            builds(EventBinding,
                  widget="queue",
                  action="add_element",
                  params={"element": "${event.node}"},
                  order=1),
            builds(EventBinding,
                  widget="grid",
                  action="show_frontier",
                  params={"positions": ["${event.pos}"]},
                  order=2)
        ],
        "dequeue": [
            builds(EventBinding,
                  widget="queue",
                  action="remove_element",
                  params={"index": 0},
                  order=1)
        ],
        "node_visited": [
            builds(EventBinding,
                  widget="grid",
                  action="highlight_element",
                  params={
                      "index": "${event.pos}",
                      "style": "visited",
                      "duration": "${timing.events}"
                  },
                  order=1)
        ],
        "goal_found": [
            builds(EventBinding,
                  widget="grid",
                  action="mark_goal",
                  params={"pos": "${event.pos}"},
                  order=1),
            builds(EventBinding,
                  widget="legend",
                  action="highlight_item",
                  params={"label": "Goal"},
                  order=2)
        ]
    },
    hydra_defaults=["_self_"]
)
```

### 5.3 ConfigStore Registration

```python
def register_widget_configs():
    """Register all widget structured configs with ConfigStore"""
    cs = ConfigStore.instance()
    
    # Register primitive widget configs
    cs.store(group="widget", name="token", node=TokenWidgetConfigZen)
    cs.store(group="widget", name="marker", node=MarkerWidgetConfigZen)
    cs.store(group="widget", name="connection", node=ConnectionWidgetConfigZen)
    
    # Register layout configs
    cs.store(group="layout", name="linear", node=LinearLayoutConfigZen)
    cs.store(group="layout", name="grid_2d", node=Grid2DLayoutConfigZen)
    
    # Register data structure widget configs
    cs.store(group="widget", name="array", node=ArrayWidgetConfigZen)
    cs.store(group="widget", name="queue", node=QueueWidgetConfigZen)
    cs.store(group="widget", name="stack", node=StackWidgetConfigZen)
    
    # Register domain-specific widget configs
    cs.store(group="widget", name="pathfinding_grid", node=PathfindingGridConfigZen)
    cs.store(group="widget", name="sorting_array", node=SortingArrayConfigZen)
    
    # Register scene configurations
    cs.store(group="scene", name="bfs_pathfinding", node=BFSSceneConfigZen)
    cs.store(group="scene", name="dfs_pathfinding", node=builds(
        BFSSceneConfigZen,  # Inherit from BFS
        name="dfs_pathfinding",
        algorithm="dfs",
        zen_partial=True
    ))
    
    # Register sorting scene configurations
    cs.store(group="scene", name="quicksort", node=make_config(
        name="quicksort",
        algorithm="quicksort",
        widgets={
            "array": SortingArrayConfigZen,
            "call_stack": StackWidgetConfigZen
        },
        event_bindings={
            "compare": [
                builds(EventBinding,
                      widget="array",
                      action="compare_highlight",
                      params={"i": "${event.i}", "j": "${event.j}", "result": "${event.result}"},
                      order=1)
            ],
            "swap": [
                builds(EventBinding,
                      widget="array",
                      action="swap_elements",
                      params={"i": "${event.i}", "j": "${event.j}"},
                      order=1)
            ]
        },
        hydra_defaults=["_self_"]
    ))
```

## 6. Scene Engine with Hydra-zen Integration

### 6.1 Enhanced Scene Engine

```python
from hydra_zen import instantiate
from omegaconf import OmegaConf
from typing import Dict, Any

class SceneEngine:
    """Manages widget lifecycle and event routing using hydra-zen."""
    
    def __init__(self, scene_config: DictConfig, timing_config=None):
        self.scene_config = scene_config
        self.timing_config = timing_config
        self.widgets: Dict[str, Any] = {}
        self.event_bindings: Dict[str, list] = {}
        
        # Initialize parameter resolvers
        self._setup_resolvers()
        
        # Instantiate scene from structured config
        self._initialize_scene()
    
    def _setup_resolvers(self):
        """Setup OmegaConf resolvers for event parameter resolution"""
        from agloviz.core.resolvers import register_event_resolvers
        register_event_resolvers()
    
    def _initialize_scene(self):
        """Initialize scene using hydra-zen instantiation"""
        # Instantiate scene configuration if it's a structured config
        if hasattr(self.scene_config, '_target_'):
            scene_data = instantiate(self.scene_config)
        else:
            scene_data = self.scene_config
        
        # Initialize widgets from structured configs
        self._initialize_widgets(scene_data.widgets)
        
        # Setup event bindings
        self._setup_event_bindings(scene_data.event_bindings)
    
    def _initialize_widgets(self, widget_specs: Dict[str, Any]):
        """Initialize widgets using hydra-zen instantiation"""
        for widget_name, widget_spec in widget_specs.items():
            try:
                # Use hydra-zen to instantiate widget
                if hasattr(widget_spec, '_target_'):
                    widget_instance = instantiate(widget_spec)
                else:
                    # Handle legacy widget specs
                    widget_instance = instantiate(widget_spec)
                
                self.widgets[widget_name] = widget_instance
            except Exception as e:
                raise ValueError(f"Failed to initialize widget '{widget_name}': {e}") from e
    
    def _setup_event_bindings(self, binding_specs: Dict[str, list]):
        """Setup event bindings from structured configs"""
        for event_name, bindings in binding_specs.items():
            resolved_bindings = []
            for binding_spec in bindings:
                if hasattr(binding_spec, '_target_'):
                    # Structured config event binding
                    binding = instantiate(binding_spec)
                else:
                    # Direct binding data
                    binding = binding_spec
                resolved_bindings.append(binding)
            self.event_bindings[event_name] = sorted(resolved_bindings, key=lambda b: b.order)
    
    def handle_event(self, event: Any):
        """Route algorithm event to appropriate widget actions"""
        event_type = getattr(event, 'type', str(event))
        
        if event_type not in self.event_bindings:
            return
        
        # Execute bindings in order
        for binding in self.event_bindings[event_type]:
            self._execute_binding(binding, event)
    
    def _execute_binding(self, binding: EventBinding, event: Any):
        """Execute event binding with parameter resolution"""
        # Check condition if specified
        if binding.condition and not self._evaluate_condition(binding.condition, event):
            return
        
        # Get target widget
        if binding.widget not in self.widgets:
            raise ValueError(f"Widget '{binding.widget}' not found in scene")
        
        widget = self.widgets[binding.widget]
        
        # Resolve parameters using OmegaConf with context
        context = {
            'event': event,
            'config': self.scene_config,
            'timing': self.timing_config,
            'widgets': self.widgets
        }
        
        # Create parameter config for resolution
        params_config = OmegaConf.create(binding.params)
        
        # Resolve parameters
        with OmegaConf.structured(context):
            resolved_params = OmegaConf.to_container(params_config, resolve=True)
        
        # Execute action
        if not hasattr(widget, binding.action):
            raise ValueError(f"Widget '{binding.widget}' has no action '{binding.action}'")
        
        action_method = getattr(widget, binding.action)
        action_method(**resolved_params)
    
    def _evaluate_condition(self, condition: str, event: Any) -> bool:
        """Evaluate condition using OmegaConf resolution"""
        context = {
            'event': event,
            'config': self.scene_config,
            'timing': self.timing_config
        }
        
        # Resolve condition template
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
```

## 6.5 Event Processing Flow with Dynamic Parameter Resolution

### **How SceneEngine Processes Events with Dynamic Parameters**

The SceneEngine implements the core event processing flow that separates static widget configuration from dynamic parameter resolution:

**1. Event Reception:**
```python
def process_event(self, event: VizEvent, run_time: float, context: dict):
    """Process algorithm event with dynamic parameter resolution."""
    event_type = event.type
    
    # Get static event bindings from scene configuration
    if event_type not in self.event_bindings:
        return
    
    # Execute bindings in order with dynamic parameter resolution
    for binding in self.event_bindings[event_type]:
        self._execute_binding_with_dynamic_params(binding, event, context)
```

**2. Dynamic Parameter Resolution:**
```python
def _execute_binding_with_dynamic_params(self, binding: EventBinding, event: VizEvent, context: dict):
    """Execute binding with OmegaConf resolver-based parameter resolution."""
    
    # Create resolution context with event data
    resolution_context = {
        'event': event.data,  # Dynamic event data from algorithm
        'config': self.scene_config,  # Static scene configuration
        'timing': self.timing_config,  # Static timing configuration
        'widgets': self.widgets  # Available widgets
    }
    
    # Set OmegaConf resolvers with dynamic context
    OmegaConf.set_resolver("current_event", lambda: event.data)
    OmegaConf.set_resolver("current_config", lambda: self.scene_config)
    OmegaConf.set_resolver("current_timing", lambda: self.timing_config)
    
    # Resolve parameters using OmegaConf
    params_config = OmegaConf.create(binding.params)
    resolved_params = OmegaConf.to_container(params_config, resolve=True)
    
    # Call widget method with resolved parameters
    widget = self.widgets[binding.widget]
    method = getattr(widget, binding.action)
    method(**resolved_params)
```

**3. Template Resolution Examples:**
```python
# Static event binding configuration
EventBinding(
    widget="grid",
    action="highlight_cell",
    params={
        "position": "${event.position}",  # Resolved from event.data.position
        "style": "visited",              # Static value
        "duration": "${timing.events}"   # Resolved from timing config
    }
)

# Event data from algorithm (dynamic)
event_data = {
    "type": "node_visited",
    "position": [3, 4],  # This becomes the resolved value
    "node_id": "A"
}

# Resolved parameters (what widget method receives)
resolved_params = {
    "position": [3, 4],     # From event.data.position
    "style": "visited",     # Static value
    "duration": 0.5         # From timing.events
}
```

**4. Benefits of This Approach:**
- ✅ **Static Configuration**: Widget properties and event bindings are pure and predictable
- ✅ **Dynamic Parameters**: Event-specific data resolved at runtime with full context
- ✅ **Hydra-zen First**: Scene configs use hydra-zen patterns without runtime dependencies
- ✅ **OmegaConf Integration**: Leverages OmegaConf's powerful resolver system
- ✅ **Clear Separation**: Configuration vs runtime behavior is explicit

## 7. Plugin System with Hydra-zen

### 7.1 Plugin Architecture

```python
from abc import ABC, abstractmethod
from hydra_zen import builds
from hydra.core.config_store import ConfigStore

class WidgetPlugin(ABC):
    """Base class for hydra-zen widget plugins."""
    
    @abstractmethod
    def get_widget_configs(self) -> Dict[str, Any]:
        """Return mapping of widget names to structured configs."""
        pass
    
    @abstractmethod
    def get_scene_configs(self) -> Dict[str, Any]:
        """Return mapping of scene names to structured configs."""
        pass
    
    @abstractmethod
    def register_configs(self, cs: ConfigStore) -> None:
        """Register plugin configs with ConfigStore."""
        pass

class AdvancedGraphsPlugin(WidgetPlugin):
    """Example plugin for advanced graph algorithms."""
    
    def get_widget_configs(self) -> Dict[str, Any]:
        return {
            "network": builds(
                "agloviz_advanced_graphs.widgets.NetworkWidget",
                node_count="${network.node_count:20}",
                layout_algorithm="${network.layout:spring}",
                zen_partial=True,
                populate_full_signature=True
            ),
            "centrality": builds(
                "agloviz_advanced_graphs.widgets.CentralityWidget",
                display_mode="${centrality.mode:bar_chart}",
                zen_partial=True,
                populate_full_signature=True
            )
        }
    
    def get_scene_configs(self) -> Dict[str, Any]:
        return {
            "network_analysis": make_config(
                name="network_analysis",
                algorithm="network_analysis",
                widgets={
                    "network": self.get_widget_configs()["network"],
                    "centrality": self.get_widget_configs()["centrality"]
                },
                event_bindings={
                    "calculate_centrality": [
                        builds(EventBinding,
                              widget="centrality",
                              action="show_centrality",
                              params={"node": "${event.node}", "value": "${event.centrality}"},
                              order=1)
                    ]
                },
                hydra_defaults=["_self_"]
            )
        }
    
    def register_configs(self, cs: ConfigStore) -> None:
        """Register plugin configs with ConfigStore."""
        # Register widget configs
        for widget_name, widget_config in self.get_widget_configs().items():
            cs.store(group="widget", name=f"advanced_graphs_{widget_name}", node=widget_config)
        
        # Register scene configs
        for scene_name, scene_config in self.get_scene_configs().items():
            cs.store(group="scene", name=f"advanced_graphs_{scene_name}", node=scene_config)

class PluginManager:
    """Manages hydra-zen widget plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, WidgetPlugin] = {}
        self.cs = ConfigStore.instance()
    
    def register_plugin(self, plugin_name: str, plugin: WidgetPlugin):
        """Register plugin and its configs."""
        if plugin_name in self.plugins:
            raise ValueError(f"Plugin '{plugin_name}' already registered")
        
        self.plugins[plugin_name] = plugin
        
        # Register plugin's configs with ConfigStore
        plugin.register_configs(self.cs)
    
    def discover_plugins(self):
        """Discover plugins via entry points."""
        try:
            import pkg_resources
            
            for entry_point in pkg_resources.iter_entry_points('agloviz.widget_plugins'):
                try:
                    plugin_class = entry_point.load()
                    plugin = plugin_class()
                    self.register_plugin(entry_point.name, plugin)
                except Exception as e:
                    print(f"Failed to load plugin '{entry_point.name}': {e}")
        except ImportError:
            pass
    
    def get_available_scenes(self) -> Dict[str, str]:
        """Get all available scene configurations from ConfigStore."""
        repo = self.cs.get_repo()
        scenes = {}
        
        for config_name in repo:
            if config_name.startswith("scene/"):
                scene_name = config_name[6:]  # Remove "scene/" prefix
                scenes[scene_name] = config_name
        
        return scenes
    
    def create_scene_from_config(self, scene_name: str, **overrides) -> SceneEngine:
        """Create scene engine from ConfigStore configuration."""
        repo = self.cs.get_repo()
        config_key = f"scene/{scene_name}"
        
        if config_key not in repo:
            raise ValueError(f"Scene '{scene_name}' not found in ConfigStore")
        
        scene_config = repo[config_key].node
        
        # Apply overrides if provided
        if overrides:
            override_config = OmegaConf.create(overrides)
            scene_config = OmegaConf.merge(scene_config, override_config)
        
        return SceneEngine(scene_config)
```

## 8. Configuration Examples

### 8.1 Hydra Configuration Files

```yaml
# config/scene/bfs_pathfinding.yaml
# @package scene
_target_: agloviz.widgets.scenes.BFSSceneConfigZen

widgets:
  grid:
    _target_: agloviz.widgets.domains.pathfinding.PathfindingGrid
    width: 15
    height: 15
    layout:
      _target_: agloviz.widgets.layouts.Grid2DLayout
      cell_size: 0.5
      
  queue:
    _target_: agloviz.widgets.structures.QueueWidget
    max_visible: 8
    layout:
      _target_: agloviz.widgets.layouts.LinearLayout
      orientation: horizontal

event_bindings:
  enqueue:
    - _target_: agloviz.core.events.EventBinding
      widget: "queue"
      action: "add_element"
      params:
        element: "${event.node}"
        animation: "slide_in"
        duration: "${timing.ui}"
      order: 1
      
    - _target_: agloviz.core.events.EventBinding
      widget: "grid"
      action: "show_frontier"
      params:
        positions: ["${event.pos}"]
        style: "frontier"
        duration: "${timing.effects}"
      order: 2
```

### 8.2 CLI Integration

```bash
# Use structured scene configuration
agloviz render scenario=maze_small scene=bfs_pathfinding timing=normal

# Override scene parameters
agloviz render scene=bfs_pathfinding scene.widgets.grid.width=20 scene.widgets.grid.height=20

# Use plugin scene
agloviz render scene=advanced_graphs_network_analysis scenario=social_network

# List available scenes
agloviz scenes list

# Validate scene configuration
agloviz scenes validate bfs_pathfinding
```

## 9. Package Organization (Hydra-zen Native)

```
agloviz/
├── widgets/
│   ├── __init__.py
│   ├── configs.py              # All structured widget configs
│   │
│   ├── primitives/             # Level 1: Pure visual elements
│   │   ├── __init__.py
│   │   ├── token.py           # TokenWidget + TokenWidgetConfigZen
│   │   ├── marker.py          # MarkerWidget + MarkerWidgetConfigZen
│   │   ├── connection.py      # ConnectionWidget + ConnectionWidgetConfigZen
│   │   └── highlight.py       # HighlightWidget + HighlightWidgetConfigZen
│   │
│   ├── layouts/               # Layout engines with configs
│   │   ├── __init__.py
│   │   ├── linear.py          # LinearLayout + LinearLayoutConfigZen
│   │   ├── grid_2d.py         # Grid2DLayout + Grid2DLayoutConfigZen
│   │   └── tree.py            # TreeLayout + TreeLayoutConfigZen
│   │
│   ├── structures/            # Level 2: Data structure abstractions
│   │   ├── __init__.py
│   │   ├── container.py       # ContainerWidget base
│   │   ├── array.py           # ArrayWidget + ArrayWidgetConfigZen
│   │   ├── queue.py           # QueueWidget + QueueWidgetConfigZen
│   │   ├── stack.py           # StackWidget + StackWidgetConfigZen
│   │   ├── tree.py            # TreeWidget + TreeWidgetConfigZen
│   │   └── graph.py           # GraphWidget + GraphWidgetConfigZen
│   │
│   └── domains/               # Level 3: Domain-specific extensions
│       ├── __init__.py
│       ├── pathfinding/
│       │   ├── __init__.py
│       │   ├── grid.py        # PathfindingGrid + PathfindingGridConfigZen
│       │   └── scenes.py      # BFSSceneConfigZen, DijkstraSceneConfigZen
│       │
│       ├── sorting/
│       │   ├── __init__.py
│       │   ├── array.py       # SortingArray + SortingArrayConfigZen
│       │   └── scenes.py      # QuickSortSceneConfigZen, MergeSortSceneConfigZen
│       │
│       └── trees/
│           ├── __init__.py
│           ├── traversal.py   # TraversalTree + TraversalTreeConfigZen
│           └── scenes.py      # BinarySearchSceneConfigZen, AVLSceneConfigZen
├── core/
│   ├── scene.py               # SceneEngine with hydra-zen integration
│   ├── plugins.py             # PluginManager with ConfigStore integration
│   └── resolvers.py           # OmegaConf custom resolvers
└── cli/
    └── scenes.py              # CLI commands for scene management
```

## 10. Migration Strategy

### 10.1 Phase 1: Foundation (Week 1)
**Goal**: Establish hydra-zen widget architecture

**Tasks**:
1. Create all structured widget configs using `builds()`
2. Register configs with ConfigStore using appropriate groups
3. Implement SceneEngine with hydra-zen integration
4. Create BFS scene configuration that replicates current functionality
5. Setup OmegaConf resolvers for event parameter resolution

### 10.2 Phase 2: Integration (Week 2)
**Goal**: Integrate with Director and CLI

**Tasks**:
1. Update Director to use SceneEngine with structured configs
2. Modify CLI to work with ConfigStore scene configurations
3. Remove BFS-specific actions from Director core
4. Test BFS visualization with new hydra-zen architecture
5. Validate parameter resolution and event binding

### 10.3 Phase 3: Widget Implementation (Week 3)
**Goal**: Implement clean widget hierarchy

**Tasks**:
1. Implement all primitive widgets with structured configs
2. Create layout engines with hydra-zen configuration
3. Build data structure widgets using composition
4. Create domain-specific widgets as extensions
5. Update all widget tests for new architecture

### 10.4 Phase 4: Plugin System (Week 4)
**Goal**: Implement plugin architecture

**Tasks**:
1. Create PluginManager with ConfigStore integration
2. Implement example plugin with structured configs
3. Add plugin discovery and CLI integration
4. Test plugin scene configurations
5. Document plugin development process

## 11. Success Criteria

### 11.1 Hydra-zen Integration Success
- ✅ All widget configurations use `builds()` patterns
- ✅ Scene configurations use `make_config()` composition
- ✅ ConfigStore registration works for all widget types
- ✅ Parameter resolution uses OmegaConf templates
- ✅ Event bindings use structured config patterns

### 11.2 Architecture Quality
- ✅ Pure visual widgets with no algorithm knowledge
- ✅ Generic data structure widgets reusable across algorithms
- ✅ Domain-specific widgets only when patterns are reused
- ✅ Configuration-driven event binding system
- ✅ Plugin system supports external extensions

### 11.3 Functionality Excellence
- ✅ BFS visualization works with clean architecture
- ✅ CLI commands work with ConfigStore scene system
- ✅ Performance is maintained or improved
- ✅ Error handling provides helpful messages
- ✅ All tests validate new implementation

---

## Summary

This Widget Architecture v2.0 document defines a complete hydra-zen first widget system that seamlessly integrates with the Configuration System and DI Strategy. The architecture features:

1. **Multi-Level Widget Hierarchy**: Pure visual primitives, generic data structures, and domain-specific extensions, all configured through hydra-zen structured configs
2. **Hydra-zen Native Configuration**: Complete integration with `builds()`, `make_config()`, ConfigStore, and parameter resolution
3. **Scene Engine Integration**: Hydra-zen powered scene management with event binding and dynamic parameter resolution
4. **Plugin Architecture**: Extensible system using ConfigStore groups and structured config registration
5. **Clean Migration Strategy**: Systematic approach to implementing hydra-zen first architecture

The implementation provides a world-class, extensible widget system that supports any algorithm type while maintaining the high engineering standards established in the ALGOViz project vision.
