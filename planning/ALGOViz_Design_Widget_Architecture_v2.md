# ALGOViz Design Doc — Widget Architecture v2.0

**Owner:** Development Team  
**Status:** Draft (Architecture Redesign)  
**Last Updated:** 2025-01-20

---

## 1. Purpose

This document defines a complete architectural redesign of the ALGOViz widget system to address fundamental design flaws discovered during Phase 1.4 Director Implementation. The current widget system has BFS-specific pollution that prevents it from being truly generic and reusable across different algorithm types.

The new architecture establishes a **multi-level widget hierarchy** with **pure visual primitives**, **generic data structure abstractions**, and **domain-specific extensions**, all connected through a **declarative, configuration-driven event binding system** powered by **hydra-zen**.

## 2. Departures from Existing Planning Documents

### 2.1 Changes to ALGOViz_Design_Widgets_Registry.md

**Previous Approach:**
- Single-level widget system with mixed concerns
- Widgets directly handle algorithm-specific events
- Hard-coded action methods in widget classes
- BFS-specific assumptions baked into "generic" widgets

**New Approach:**
- Multi-level widget hierarchy (3 distinct layers)
- Pure visual widgets with no event knowledge
- Configuration-driven event binding system
- Complete separation of visual operations from algorithm semantics

### 2.2 Changes to ALGOViz_Design_Director.md

**Previous Approach:**
- Director contains hard-coded algorithm-specific actions
- Actions like `place_start`, `place_goal`, `place_obstacles` in core Director
- Widget lifecycle managed directly by Director
- Event routing through simple routing maps

**New Approach:**
- Director becomes pure orchestrator with minimal core actions
- Algorithm-specific actions provided by scene configurations
- Scene Engine manages widget lifecycle and event binding
- Hydra-zen configuration system drives all instantiation

### 2.3 Changes to ALGOViz_Design_DI_Strategy.md

**Previous Approach:**
- General hydra + hydra-zen + OmegaConf strategy
- Mix of YAML and programmatic configuration
- Traditional DI container patterns

**New Approach:**
- **Hydra-zen first** philosophy with selective Hydra usage
- Typed configuration objects using Pydantic models
- Scene configurations as first-class DI components
- Configuration-driven widget instantiation and event binding

### 2.4 Integration with Existing Systems

This architecture maintains compatibility with:
- **Storyboard DSL**: Acts/Shots/Beats execution flow unchanged
- **VizEvent System**: Events still flow from adapters through routing
- **Timing System**: TimingConfig integration preserved
- **Error Taxonomy**: Enhanced with scene configuration errors

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

### 3.3 Routing System Pollution

Current routing maps assume specific widget types and methods:

```python
# PROBLEMATIC: BFS-specific routing assumptions
BFS_ROUTING = {
    "enqueue": ["queue.highlight_enqueue", "grid.mark_frontier"],
    "dequeue": ["queue.highlight_dequeue"],
    "goal_found": ["grid.flash_goal", "hud.show_success"]
}
```

**Problems:**
- Assumes existence of "grid" and "queue" widgets
- Uses BFS-specific method names
- Cannot handle sorting, tree, or arbitrary graph algorithms
- No support for multiple widgets responding to same event in order

### 3.4 Configuration System Gaps

- No way to declare scene compositions
- No event binding configuration
- No widget instantiation configuration
- Hard-coded widget relationships

## 4. Core Widget Abstractions (Multi-Level Hierarchy)

### 4.1 Level 1: Primitive Visual Elements

**Philosophy**: Ultra-generic visual primitives that know nothing about data structures or algorithms.

```python
from pydantic import BaseModel, Field
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

class HighlightWidget(PrimitiveWidget):
    """Overlay highlighting effects."""
    highlight_type: str = "glow"  # glow, outline, fill, pulse
    color: str = "#FFFF00"
    intensity: float = 1.0
    
    def apply_to(self, target_position: tuple[float, float], duration: float = 1.0):
        """Pure visual operation: apply highlight to position."""
```

**Key Principles:**
- No knowledge of data structures (arrays, queues, trees)
- No knowledge of algorithms (BFS, sorting, etc.)
- Pure visual operations only
- Composable into higher-level widgets
- Leverage Manim primitives where possible

### 4.2 Level 2: Data Structure Abstractions

**Philosophy**: Generic data structure concepts that know about structural relationships but not algorithm semantics.

```python
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

class TreeLayout(LayoutEngine):
    """Arranges elements in tree structure."""
    root_position: tuple[float, float] = (0.0, 0.0)
    level_spacing: float = 2.0
    node_spacing: float = 1.5
    
    def position_nodes(self, tree_structure: dict[str, list[str]]) -> dict[str, tuple[float, float]]:
        """Calculate positions for tree nodes."""

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

class ArrayWidget(ContainerWidget):
    """Generic array/list visualization."""
    
    def __init__(self, size: int, **kwargs):
        layout = LinearLayout(orientation="horizontal")
        elements = [TokenWidget(text=str(i)) for i in range(size)]
        super().__init__(elements=elements, layout=layout, name="array", **kwargs)
    
    def set_value(self, index: int, value: Any, animation: str = "fade"):
        """Set value at specific index."""
        
    def get_value(self, index: int) -> Any:
        """Get value at specific index."""

class QueueWidget(ContainerWidget):
    """Generic FIFO queue visualization."""
    
    def __init__(self, **kwargs):
        layout = LinearLayout(orientation="horizontal")
        super().__init__(layout=layout, name="queue", **kwargs)
    
    def enqueue(self, value: Any, animation: str = "slide_in"):
        """Add element to rear of queue."""
        element = TokenWidget(text=str(value))
        self.add_element(element, animation=animation)
    
    def dequeue(self, animation: str = "slide_out") -> Any:
        """Remove element from front of queue."""
        if self.elements:
            return self.remove_element(0, animation=animation)

class StackWidget(ContainerWidget):
    """Generic LIFO stack visualization."""
    
    def __init__(self, **kwargs):
        layout = LinearLayout(orientation="vertical")
        super().__init__(layout=layout, name="stack", **kwargs)
    
    def push(self, value: Any, animation: str = "slide_in"):
        """Add element to top of stack."""
        element = TokenWidget(text=str(value))
        self.add_element(element, animation=animation)
    
    def pop(self, animation: str = "slide_out") -> Any:
        """Remove element from top of stack."""
        if self.elements:
            return self.remove_element(-1, animation=animation)

class TreeWidget(BaseModel):
    """Generic tree structure visualization."""
    nodes: dict[str, TokenWidget] = Field(default_factory=dict)
    edges: list[ConnectionWidget] = Field(default_factory=list)
    layout: TreeLayout
    name: str = "tree"
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_node(self, node_id: str, parent_id: str | None = None, value: Any = None):
        """Add node to tree structure."""
        
    def remove_node(self, node_id: str):
        """Remove node and all descendants."""
        
    def highlight_node(self, node_id: str, style: str, duration: float = 1.0):
        """Highlight specific node."""
        
    def highlight_path(self, path: list[str], style: str, duration: float = 1.0):
        """Highlight path through tree."""

class GraphWidget(BaseModel):
    """Generic graph/network visualization."""
    nodes: dict[str, TokenWidget] = Field(default_factory=dict)
    edges: dict[tuple[str, str], ConnectionWidget] = Field(default_factory=dict)
    layout: LayoutEngine
    name: str = "graph"
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_node(self, node_id: str, position: tuple[float, float] | None = None, value: Any = None):
        """Add node to graph."""
        
    def add_edge(self, from_node: str, to_node: str, weight: float | None = None):
        """Add edge between nodes."""
        
    def highlight_nodes(self, node_ids: list[str], style: str, duration: float = 1.0):
        """Highlight multiple nodes."""
        
    def highlight_edges(self, edges: list[tuple[str, str]], style: str, duration: float = 1.0):
        """Highlight multiple edges."""
```

**Key Principles:**
- Know about data structure operations (add, remove, access)
- No knowledge of algorithm semantics (visited, frontier, goal)
- Generic method names (highlight, not mark_visited)
- Composable and extensible
- Layout engines separate from data operations

### 4.3 Level 3: Semantic Data Structures (Domain-Specific)

**Philosophy**: When we need algorithm-specific patterns repeatedly, create semantic extensions of Level 2 widgets.

```python
from typing import Protocol

class AlgorithmWidget(Protocol):
    """Protocol for algorithm-specific widget extensions."""
    def handle_algorithm_event(self, event_type: str, event_data: dict) -> None:
        """Handle algorithm-specific events."""

class PathfindingGrid(ArrayWidget):
    """Grid specialized for pathfinding algorithms."""
    
    def __init__(self, width: int, height: int, **kwargs):
        # Create 2D grid layout
        layout = Grid2DLayout(width=width, height=height)
        elements = [TokenWidget() for _ in range(width * height)]
        super().__init__(elements=elements, layout=layout, name="pathfinding_grid", **kwargs)
        
        # Pathfinding-specific state
        self.width = width
        self.height = height
        self.start_pos: tuple[int, int] | None = None
        self.goal_pos: tuple[int, int] | None = None
        self.obstacles: set[tuple[int, int]] = set()
    
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
    
    def mark_obstacle(self, pos: tuple[int, int]):
        """Mark position as obstacle (pathfinding semantic)."""
        self.obstacles.add(pos)
        index = pos[0] * self.width + pos[1]
        self.highlight_element(index, "obstacle")
    
    def show_frontier(self, positions: list[tuple[int, int]]):
        """Show frontier positions (pathfinding semantic)."""
        for pos in positions:
            index = pos[0] * self.width + pos[1]
            self.highlight_element(index, "frontier")

class SortingArray(ArrayWidget):
    """Array specialized for sorting algorithms."""
    
    def compare_highlight(self, i: int, j: int, result: str, duration: float = 1.0):
        """Highlight comparison between two elements (sorting semantic)."""
        # Highlight both elements with comparison result
        self.highlight_element(i, f"compare_{result}", duration)
        self.highlight_element(j, f"compare_{result}", duration)
    
    def partition_marker(self, pivot_index: int):
        """Show partition marker (sorting semantic)."""
        self.highlight_element(pivot_index, "pivot")
    
    def show_sorted_region(self, start: int, end: int):
        """Highlight sorted region (sorting semantic)."""
        for i in range(start, end + 1):
            self.highlight_element(i, "sorted")

class TraversalTree(TreeWidget):
    """Tree specialized for traversal algorithms."""
    
    def mark_current(self, node_id: str):
        """Mark current node in traversal (traversal semantic)."""
        self.highlight_node(node_id, "current")
    
    def show_path(self, path: list[str]):
        """Show path through tree (traversal semantic)."""
        self.highlight_path(path, "path")
    
    def highlight_subtree(self, root_id: str):
        """Highlight entire subtree (traversal semantic)."""
        # Implementation would highlight root and all descendants
        pass
```

**Key Principles:**
- Built on Level 2 data structure widgets
- Add algorithm-specific semantic methods
- Still generic enough for algorithm families (all pathfinding, all sorting)
- Created only when patterns are reused across multiple algorithms

## 5. Extension System Design

### 5.1 Configuration-Driven Event Binding

**Philosophy**: Pure visual widgets know nothing about events. All event handling is configured declaratively through scene configurations.

```python
from pydantic import BaseModel, Field
from typing import Any, Literal

class EventBinding(BaseModel):
    """Configuration for binding algorithm events to widget actions."""
    widget: str = Field(..., description="Name of target widget")
    action: str = Field(..., description="Widget method to call")
    params: dict[str, Any] = Field(default_factory=dict, description="Parameters for action")
    order: int = Field(1, description="Execution order for multiple bindings")
    condition: str | None = Field(None, description="Optional condition for execution")
    
    class Config:
        schema_extra = {
            "examples": [
                {
                    "widget": "grid",
                    "action": "highlight_element",
                    "params": {"index": "${event.pos}", "style": "visited"},
                    "order": 1
                }
            ]
        }

class WidgetSpec(BaseModel):
    """Configuration specification for widget instantiation."""
    name: str = Field(..., description="Unique widget name in scene")
    _target_: str = Field(..., description="Full path to widget class")
    layout: dict[str, Any] | None = Field(None, description="Layout configuration")
    
    class Config:
        extra = "allow"  # Allow additional widget-specific parameters

class SceneConfig(BaseModel):
    """Complete scene configuration including widgets and event bindings."""
    widgets: dict[str, WidgetSpec] = Field(default_factory=dict)
    event_bindings: dict[str, list[EventBinding]] = Field(default_factory=dict)
    timing_overrides: dict[str, float] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "examples": [
                {
                    "widgets": {
                        "grid": {
                            "name": "grid",
                            "_target_": "agloviz.widgets.PathfindingGrid",
                            "width": 10,
                            "height": 10
                        }
                    },
                    "event_bindings": {
                        "node_visited": [
                            {
                                "widget": "grid",
                                "action": "highlight_element",
                                "params": {"index": "${event.pos}", "style": "visited"},
                                "order": 1
                            }
                        ]
                    }
                }
            ]
        }
```

### 5.2 Scene Engine with Event Routing

```python
import re
from typing import Any
from hydra_zen import instantiate

class ParameterResolver:
    """Resolves parameter templates in event bindings."""
    
    @staticmethod
    def resolve_params(params: dict[str, Any], event: Any, config: Any = None) -> dict[str, Any]:
        """Resolve parameter templates like ${event.pos} to actual values."""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("${"):
                resolved[key] = ParameterResolver._resolve_template(value, event, config)
            else:
                resolved[key] = value
        return resolved
    
    @staticmethod
    def _resolve_template(template: str, event: Any, config: Any = None) -> Any:
        """Resolve a single template string."""
        # Extract variable path from ${...}
        match = re.match(r'\$\{(.+)\}', template)
        if not match:
            return template
            
        path = match.group(1)
        
        if path.startswith("event."):
            # Resolve from event object
            attr_path = path[6:]  # Remove "event."
            return ParameterResolver._get_nested_attr(event, attr_path)
        elif path.startswith("config."):
            # Resolve from config object
            attr_path = path[7:]  # Remove "config."
            return ParameterResolver._get_nested_attr(config, attr_path)
        else:
            return template
    
    @staticmethod
    def _get_nested_attr(obj: Any, attr_path: str) -> Any:
        """Get nested attribute like 'pos.x' from object."""
        attrs = attr_path.split('.')
        result = obj
        for attr in attrs:
            result = getattr(result, attr)
        return result

class SceneEngine:
    """Manages widget lifecycle and event routing based on scene configuration."""
    
    def __init__(self, scene_config: SceneConfig):
        self.config = scene_config
        self.widgets: dict[str, Any] = {}
        self.parameter_resolver = ParameterResolver()
        
        # Instantiate widgets from configuration
        self._instantiate_widgets()
    
    def _instantiate_widgets(self):
        """Instantiate all widgets from scene configuration."""
        for widget_name, widget_spec in self.config.widgets.items():
            # Use hydra-zen to instantiate widget from _target_
            widget_config = widget_spec.dict()
            widget = instantiate(widget_config)
            self.widgets[widget_name] = widget
    
    def handle_event(self, event: Any):
        """Route algorithm event to appropriate widget actions."""
        event_type = event.type if hasattr(event, 'type') else str(event)
        
        if event_type not in self.config.event_bindings:
            return
        
        # Get all bindings for this event type, sorted by order
        bindings = sorted(
            self.config.event_bindings[event_type],
            key=lambda b: b.order
        )
        
        # Execute each binding in order
        for binding in bindings:
            self._execute_binding(binding, event)
    
    def _execute_binding(self, binding: EventBinding, event: Any):
        """Execute a single event binding."""
        # Check condition if specified
        if binding.condition and not self._evaluate_condition(binding.condition, event):
            return
        
        # Get target widget
        if binding.widget not in self.widgets:
            raise ValueError(f"Widget '{binding.widget}' not found in scene")
        
        widget = self.widgets[binding.widget]
        
        # Resolve parameters
        resolved_params = self.parameter_resolver.resolve_params(
            binding.params, event, self.config
        )
        
        # Execute action
        if not hasattr(widget, binding.action):
            raise ValueError(f"Widget '{binding.widget}' has no action '{binding.action}'")
        
        action_method = getattr(widget, binding.action)
        action_method(**resolved_params)
    
    def _evaluate_condition(self, condition: str, event: Any) -> bool:
        """Evaluate condition string for conditional execution."""
        # Simple condition evaluation - could be enhanced
        # For now, just support basic comparisons
        return True  # TODO: Implement condition evaluation
    
    def get_widget(self, name: str) -> Any:
        """Get widget by name."""
        return self.widgets.get(name)
    
    def show_widgets(self, widget_names: list[str] | None = None):
        """Show specified widgets or all widgets."""
        names = widget_names or list(self.widgets.keys())
        for name in names:
            if name in self.widgets:
                widget = self.widgets[name]
                if hasattr(widget, 'show'):
                    widget.show()
    
    def hide_widgets(self, widget_names: list[str] | None = None):
        """Hide specified widgets or all widgets."""
        names = widget_names or list(self.widgets.keys())
        for name in names:
            if name in self.widgets:
                widget = self.widgets[name]
                if hasattr(widget, 'hide'):
                    widget.hide()
```

### 5.3 Hydra-Zen Configuration System

```python
from hydra_zen import builds, make_config
from typing import Type

# Widget configuration builders
ArrayWidgetConfig = builds(
    ArrayWidget,
    size=10,
    zen_partial=True  # Allow runtime parameter overrides
)

PathfindingGridConfig = builds(
    PathfindingGrid,
    width=10,
    height=10,
    zen_partial=True
)

QueueWidgetConfig = builds(
    QueueWidget,
    zen_partial=True
)

# Layout configuration builders
Grid2DLayoutConfig = builds(
    Grid2DLayout,
    width=10,
    height=10,
    cell_size=1.0,
    zen_partial=True
)

LinearLayoutConfig = builds(
    LinearLayout,
    orientation="horizontal",
    spacing=1.0,
    zen_partial=True
)

# Scene configuration builders
class BFSSceneConfig(BaseModel):
    """BFS-specific scene configuration."""
    
    @staticmethod
    def create() -> SceneConfig:
        return SceneConfig(
            widgets={
                "grid": WidgetSpec(
                    name="grid",
                    _target_="agloviz.widgets.PathfindingGrid",
                    width=10,
                    height=10
                ),
                "queue": WidgetSpec(
                    name="queue", 
                    _target_="agloviz.widgets.QueueWidget"
                )
            },
            event_bindings={
                "node_visited": [
                    EventBinding(
                        widget="grid",
                        action="highlight_element", 
                        params={"index": "${event.pos}", "style": "visited"},
                        order=1
                    )
                ],
                "enqueue": [
                    EventBinding(
                        widget="grid",
                        action="show_frontier",
                        params={"positions": ["${event.pos}"]},
                        order=1
                    ),
                    EventBinding(
                        widget="queue",
                        action="enqueue",
                        params={"value": "${event.node}"},
                        order=2
                    )
                ],
                "dequeue": [
                    EventBinding(
                        widget="queue",
                        action="dequeue",
                        params={},
                        order=1
                    )
                ],
                "goal_found": [
                    EventBinding(
                        widget="grid",
                        action="mark_goal",
                        params={"pos": "${event.pos}"},
                        order=1
                    )
                ]
            }
        )

class SortingSceneConfig(BaseModel):
    """Sorting algorithm scene configuration."""
    
    @staticmethod
    def create(array_size: int = 10) -> SceneConfig:
        return SceneConfig(
            widgets={
                "array": WidgetSpec(
                    name="array",
                    _target_="agloviz.widgets.domains.sorting.SortingArray",
                    size=array_size
                )
            },
            event_bindings={
                "compare": [
                    EventBinding(
                        widget="array",
                        action="compare_highlight",
                        params={"i": "${event.i}", "j": "${event.j}", "result": "${event.result}"},
                        order=1
                    )
                ],
                "swap": [
                    EventBinding(
                        widget="array",
                        action="swap_elements",
                        params={"i": "${event.i}", "j": "${event.j}"},
                        order=1
                    )
                ],
                "partition": [
                    EventBinding(
                        widget="array",
                        action="partition_marker",
                        params={"pivot_index": "${event.pivot}"},
                        order=1
                    )
                ]
            }
        )

# Director configuration with scene integration
DirectorConfig = builds(
    Director,
    scene_config=BFSSceneConfig.create(),
    zen_partial=True
)
```

## 6. Domain-Specific Packages

### 6.1 Package Organization

```
agloviz/
├── widgets/
│   ├── primitives/          # Level 1: Pure visual elements
│   │   ├── __init__.py
│   │   ├── token.py         # TokenWidget
│   │   ├── marker.py        # MarkerWidget  
│   │   ├── connection.py    # ConnectionWidget
│   │   └── highlight.py     # HighlightWidget
│   │
│   ├── structures/          # Level 2: Data structure abstractions
│   │   ├── __init__.py
│   │   ├── container.py     # ContainerWidget base
│   │   ├── array.py         # ArrayWidget
│   │   ├── queue.py         # QueueWidget
│   │   ├── stack.py         # StackWidget
│   │   ├── tree.py          # TreeWidget
│   │   └── graph.py         # GraphWidget
│   │
│   ├── layouts/             # Layout engines
│   │   ├── __init__.py
│   │   ├── linear.py        # LinearLayout
│   │   ├── grid_2d.py       # Grid2DLayout
│   │   ├── tree.py          # TreeLayout
│   │   └── graph.py         # GraphLayout
│   │
│   └── domains/             # Level 3: Domain-specific extensions
│       ├── __init__.py
│       ├── pathfinding/
│       │   ├── __init__.py
│       │   ├── grid.py      # PathfindingGrid
│       │   └── scenes.py    # BFSSceneConfig, DijkstraSceneConfig
│       │
│       ├── sorting/
│       │   ├── __init__.py
│       │   ├── array.py     # SortingArray
│       │   └── scenes.py    # QuickSortSceneConfig, MergeSortSceneConfig
│       │
│       └── trees/
│           ├── __init__.py
│           ├── traversal.py # TraversalTree
│           └── scenes.py    # BinarySearchSceneConfig, AVLSceneConfig
```

### 6.2 Domain Package Examples

#### Pathfinding Domain Package
```python
# agloviz/widgets/domains/pathfinding/__init__.py
from .grid import PathfindingGrid
from .scenes import BFSSceneConfig, DijkstraSceneConfig, AStarSceneConfig

__all__ = ["PathfindingGrid", "BFSSceneConfig", "DijkstraSceneConfig", "AStarSceneConfig"]

# agloviz/widgets/domains/pathfinding/scenes.py
class DijkstraSceneConfig(BaseModel):
    """Dijkstra algorithm scene configuration."""
    
    @staticmethod
    def create(width: int = 10, height: int = 10) -> SceneConfig:
        return SceneConfig(
            widgets={
                "grid": WidgetSpec(
                    name="grid",
                    _target_="agloviz.widgets.domains.pathfinding.PathfindingGrid",
                    width=width,
                    height=height
                ),
                "priority_queue": WidgetSpec(
                    name="priority_queue",
                    _target_="agloviz.widgets.structures.PriorityQueueWidget"
                )
            },
            event_bindings={
                "node_visited": [
                    EventBinding(
                        widget="grid",
                        action="highlight_element",
                        params={"index": "${event.pos}", "style": "visited"},
                        order=1
                    )
                ],
                "relax_edge": [
                    EventBinding(
                        widget="grid",
                        action="show_edge_relaxation",
                        params={"from_pos": "${event.from_pos}", "to_pos": "${event.to_pos}", "new_distance": "${event.distance}"},
                        order=1
                    )
                ],
                "add_to_queue": [
                    EventBinding(
                        widget="priority_queue",
                        action="add",
                        params={"value": "${event.node}", "priority": "${event.priority}"},
                        order=1
                    )
                ]
            }
        )
```

#### Sorting Domain Package
```python
# agloviz/widgets/domains/sorting/scenes.py
class QuickSortSceneConfig(BaseModel):
    """QuickSort algorithm scene configuration."""
    
    @staticmethod
    def create(array_size: int = 10) -> SceneConfig:
        return SceneConfig(
            widgets={
                "array": WidgetSpec(
                    name="array",
                    _target_="agloviz.widgets.domains.sorting.SortingArray",
                    size=array_size
                ),
                "call_stack": WidgetSpec(
                    name="call_stack",
                    _target_="agloviz.widgets.structures.StackWidget"
                )
            },
            event_bindings={
                "compare": [
                    EventBinding(
                        widget="array",
                        action="compare_highlight",
                        params={"i": "${event.i}", "j": "${event.j}", "result": "${event.result}"},
                        order=1
                    )
                ],
                "swap": [
                    EventBinding(
                        widget="array",
                        action="swap_elements",
                        params={"i": "${event.i}", "j": "${event.j}"},
                        order=1
                    )
                ],
                "partition": [
                    EventBinding(
                        widget="array",
                        action="partition_marker",
                        params={"pivot_index": "${event.pivot}"},
                        order=1
                    )
                ],
                "recursive_call": [
                    EventBinding(
                        widget="call_stack",
                        action="push",
                        params={"value": "quicksort(${event.start}, ${event.end})"},
                        order=1
                    )
                ],
                "return_from_call": [
                    EventBinding(
                        widget="call_stack",
                        action="pop",
                        params={},
                        order=1
                    )
                ]
            }
        )
```

### 6.3 Plugin Integration for Domain Packages

```python
# External plugin: agloviz_advanced_graphs/scenes.py
class NetworkAnalysisSceneConfig(BaseModel):
    """Network analysis algorithms scene configuration."""
    
    @staticmethod
    def create(node_count: int = 20) -> SceneConfig:
        return SceneConfig(
            widgets={
                "network": WidgetSpec(
                    name="network",
                    _target_="agloviz_advanced_graphs.widgets.NetworkWidget",
                    node_count=node_count
                ),
                "centrality_display": WidgetSpec(
                    name="centrality_display",
                    _target_="agloviz_advanced_graphs.widgets.CentralityWidget"
                )
            },
            event_bindings={
                "calculate_centrality": [
                    EventBinding(
                        widget="centrality_display",
                        action="show_centrality",
                        params={"node": "${event.node}", "value": "${event.centrality}"},
                        order=1
                    )
                ],
                "highlight_community": [
                    EventBinding(
                        widget="network",
                        action="highlight_community",
                        params={"nodes": "${event.community_nodes}"},
                        order=1
                    )
                ]
            }
        )

# Plugin registration
from agloviz.core.registry import SceneConfigRegistry

SceneConfigRegistry.register("network_analysis", NetworkAnalysisSceneConfig.create)
```

## 7. Event System Architecture

### 7.1 Event Flow Architecture

```
Algorithm Adapter → VizEvent → Director → Scene Engine → Widget Actions
       ↓               ↓          ↓           ↓              ↓
   BFS.run()     "node_visited"  routing   binding      highlight()
                    payload    to scene   resolution   execution
```

### 7.2 Event Binding Resolution Process

```python
class EventBindingResolver:
    """Resolves event bindings and manages execution order."""
    
    def __init__(self, scene_config: SceneConfig):
        self.scene_config = scene_config
        self.widgets: dict[str, Any] = {}
    
    def resolve_bindings(self, event_type: str) -> list[EventBinding]:
        """Get all bindings for event type, sorted by execution order."""
        if event_type not in self.scene_config.event_bindings:
            return []
        
        bindings = self.scene_config.event_bindings[event_type]
        return sorted(bindings, key=lambda b: (b.order, b.widget, b.action))
    
    def validate_bindings(self) -> list[str]:
        """Validate all event bindings against available widgets and actions."""
        errors = []
        
        for event_type, bindings in self.scene_config.event_bindings.items():
            for binding in bindings:
                # Check widget exists
                if binding.widget not in self.scene_config.widgets:
                    errors.append(f"Event '{event_type}' binding references unknown widget '{binding.widget}'")
                    continue
                
                # Check widget supports action (would need widget introspection)
                widget_spec = self.scene_config.widgets[binding.widget]
                # TODO: Validate action exists on widget class
        
        return errors
    
    def get_execution_plan(self, event_type: str) -> list[dict[str, Any]]:
        """Get detailed execution plan for event type."""
        bindings = self.resolve_bindings(event_type)
        
        plan = []
        for binding in bindings:
            plan.append({
                "order": binding.order,
                "widget": binding.widget,
                "action": binding.action,
                "params": binding.params,
                "condition": binding.condition
            })
        
        return plan
```

### 7.3 Parameter Template System

```python
import re
from typing import Any, Dict

class ParameterTemplateEngine:
    """Advanced parameter template resolution with support for expressions."""
    
    TEMPLATE_PATTERN = re.compile(r'\$\{([^}]+)\}')
    
    def __init__(self):
        self.functions = {
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'abs': abs,
            'max': max,
            'min': min
        }
    
    def resolve_parameters(self, params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Resolve all parameter templates in parameter dictionary."""
        resolved = {}
        
        for key, value in params.items():
            resolved[key] = self._resolve_value(value, context)
        
        return resolved
    
    def _resolve_value(self, value: Any, context: dict[str, Any]) -> Any:
        """Resolve a single parameter value."""
        if isinstance(value, str):
            return self._resolve_string_templates(value, context)
        elif isinstance(value, list):
            return [self._resolve_value(item, context) for item in value]
        elif isinstance(value, dict):
            return {k: self._resolve_value(v, context) for k, v in value.items()}
        else:
            return value
    
    def _resolve_string_templates(self, template: str, context: dict[str, Any]) -> Any:
        """Resolve template strings like ${event.pos} or ${len(event.path)}."""
        
        def replace_template(match):
            expression = match.group(1)
            return str(self._evaluate_expression(expression, context))
        
        # If the entire string is a single template, return the actual type
        if self.TEMPLATE_PATTERN.fullmatch(template):
            expression = self.TEMPLATE_PATTERN.match(template).group(1)
            return self._evaluate_expression(expression, context)
        
        # Otherwise, replace templates within the string
        return self.TEMPLATE_PATTERN.sub(replace_template, template)
    
    def _evaluate_expression(self, expression: str, context: dict[str, Any]) -> Any:
        """Safely evaluate expressions like 'event.pos' or 'len(event.path)'."""
        try:
            # Simple attribute access
            if '(' not in expression:
                return self._get_nested_attribute(expression, context)
            
            # Function calls - very basic support
            func_match = re.match(r'(\w+)\((.+)\)', expression)
            if func_match:
                func_name = func_match.group(1)
                arg_expr = func_match.group(2)
                
                if func_name in self.functions:
                    arg_value = self._get_nested_attribute(arg_expr, context)
                    return self.functions[func_name](arg_value)
            
            # Fallback to string
            return expression
            
        except Exception:
            # If evaluation fails, return the original expression
            return expression
    
    def _get_nested_attribute(self, path: str, context: dict[str, Any]) -> Any:
        """Get nested attribute like 'event.pos.x' from context."""
        parts = path.split('.')
        result = context
        
        for part in parts:
            if isinstance(result, dict):
                result = result.get(part)
            else:
                result = getattr(result, part, None)
            
            if result is None:
                break
        
        return result

# Usage examples:
# "${event.pos}" -> (3, 5)
# "${event.node}" -> "A"  
# "${len(event.path)}" -> 4
# "Node ${event.node} visited" -> "Node A visited"
```

### 7.4 Conditional Event Execution

```python
class ConditionalExecutor:
    """Handles conditional execution of event bindings."""
    
    def __init__(self, template_engine: ParameterTemplateEngine):
        self.template_engine = template_engine
    
    def should_execute(self, binding: EventBinding, context: dict[str, Any]) -> bool:
        """Determine if binding should execute based on condition."""
        if not binding.condition:
            return True
        
        return self._evaluate_condition(binding.condition, context)
    
    def _evaluate_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """Evaluate condition string safely."""
        try:
            # Resolve any templates in the condition
            resolved_condition = self.template_engine._resolve_string_templates(condition, context)
            
            # Simple boolean conditions
            if resolved_condition.lower() in ('true', 'false'):
                return resolved_condition.lower() == 'true'
            
            # Comparison operations
            for op in ['==', '!=', '<=', '>=', '<', '>']:
                if op in resolved_condition:
                    left, right = resolved_condition.split(op, 1)
                    left = left.strip()
                    right = right.strip()
                    
                    # Try to convert to numbers if possible
                    try:
                        left_val = float(left)
                        right_val = float(right)
                    except ValueError:
                        left_val = left.strip('"\'')
                        right_val = right.strip('"\'')
                    
                    if op == '==':
                        return left_val == right_val
                    elif op == '!=':
                        return left_val != right_val
                    elif op == '<':
                        return left_val < right_val
                    elif op == '<=':
                        return left_val <= right_val
                    elif op == '>':
                        return left_val > right_val
                    elif op == '>=':
                        return left_val >= right_val
            
            return False
            
        except Exception:
            return False

# Usage examples:
# condition: "${event.is_goal} == true"
# condition: "${event.distance} > 5"
# condition: "${event.node} == 'target'"
```

## 8. Plugin Integration Architecture

### 8.1 Plugin Widget Registration

```python
from abc import ABC, abstractmethod
from typing import Type, Dict, Any

class WidgetPlugin(ABC):
    """Base class for widget plugins."""
    
    @abstractmethod
    def get_widget_classes(self) -> Dict[str, Type]:
        """Return mapping of widget names to widget classes."""
        pass
    
    @abstractmethod
    def get_scene_configs(self) -> Dict[str, Type]:
        """Return mapping of scene config names to config classes."""
        pass
    
    @abstractmethod
    def get_plugin_info(self) -> Dict[str, Any]:
        """Return plugin metadata."""
        pass

class AdvancedGraphsPlugin(WidgetPlugin):
    """Example plugin for advanced graph algorithms."""
    
    def get_widget_classes(self) -> Dict[str, Type]:
        from .widgets import NetworkWidget, CentralityWidget, CommunityWidget
        
        return {
            "network": NetworkWidget,
            "centrality": CentralityWidget,
            "community": CommunityWidget
        }
    
    def get_scene_configs(self) -> Dict[str, Type]:
        from .scenes import NetworkAnalysisSceneConfig, CommunityDetectionSceneConfig
        
        return {
            "network_analysis": NetworkAnalysisSceneConfig,
            "community_detection": CommunityDetectionSceneConfig
        }
    
    def get_plugin_info(self) -> Dict[str, Any]:
        return {
            "name": "Advanced Graphs",
            "version": "1.0.0",
            "author": "Graph Algorithms Team",
            "description": "Advanced graph algorithm visualizations",
            "requires": ["agloviz>=1.4.0", "networkx>=2.0"]
        }

class PluginRegistry:
    """Registry for managing widget plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, WidgetPlugin] = {}
        self.widget_classes: Dict[str, Type] = {}
        self.scene_configs: Dict[str, Type] = {}
    
    def register_plugin(self, plugin_name: str, plugin: WidgetPlugin):
        """Register a widget plugin."""
        if plugin_name in self.plugins:
            raise ValueError(f"Plugin '{plugin_name}' already registered")
        
        self.plugins[plugin_name] = plugin
        
        # Register widget classes with namespacing
        for widget_name, widget_class in plugin.get_widget_classes().items():
            full_name = f"{plugin_name}.{widget_name}"
            self.widget_classes[full_name] = widget_class
        
        # Register scene configs
        for config_name, config_class in plugin.get_scene_configs().items():
            full_name = f"{plugin_name}.{config_name}"
            self.scene_configs[full_name] = config_class
    
    def get_widget_class(self, widget_name: str) -> Type:
        """Get widget class by name (supports namespaced names)."""
        if widget_name not in self.widget_classes:
            raise ValueError(f"Widget '{widget_name}' not found")
        return self.widget_classes[widget_name]
    
    def get_scene_config(self, config_name: str) -> Type:
        """Get scene config class by name."""
        if config_name not in self.scene_configs:
            raise ValueError(f"Scene config '{config_name}' not found")
        return self.scene_configs[config_name]
    
    def list_widgets(self) -> Dict[str, Dict[str, Any]]:
        """List all available widgets with metadata."""
        widgets = {}
        for widget_name, widget_class in self.widget_classes.items():
            widgets[widget_name] = {
                "class": widget_class.__name__,
                "module": widget_class.__module__,
                "plugin": widget_name.split('.')[0] if '.' in widget_name else "core"
            }
        return widgets
    
    def discover_plugins(self):
        """Discover and load plugins from entry points."""
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
            # pkg_resources not available
            pass

# Global plugin registry
plugin_registry = PluginRegistry()
```

### 8.2 Plugin Entry Points Configuration

```python
# setup.py or pyproject.toml for plugin packages
[project.entry-points."agloviz.widget_plugins"]
advanced_graphs = "agloviz_advanced_graphs:AdvancedGraphsPlugin"
sorting_animations = "agloviz_sorting_plus:SortingAnimationsPlugin"
tree_visualizations = "agloviz_trees:TreeVisualizationsPlugin"
```

### 8.3 Plugin Discovery and Loading

```python
class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""
    
    def __init__(self):
        self.registry = PluginRegistry()
        self.loaded_plugins: Dict[str, Dict[str, Any]] = {}
    
    def discover_and_load_plugins(self):
        """Discover and load all available plugins."""
        self.registry.discover_plugins()
        
        # Update loaded plugins info
        for plugin_name, plugin in self.registry.plugins.items():
            self.loaded_plugins[plugin_name] = plugin.get_plugin_info()
    
    def get_available_widgets(self) -> Dict[str, Any]:
        """Get all available widgets from core and plugins."""
        return self.registry.list_widgets()
    
    def get_available_scenes(self) -> Dict[str, Any]:
        """Get all available scene configurations."""
        scenes = {}
        for config_name, config_class in self.registry.scene_configs.items():
            scenes[config_name] = {
                "class": config_class.__name__,
                "module": config_class.__module__,
                "plugin": config_name.split('.')[0] if '.' in config_name else "core"
            }
        return scenes
    
    def create_scene_config(self, scene_name: str, **kwargs) -> SceneConfig:
        """Create scene configuration by name."""
        config_class = self.registry.get_scene_config(scene_name)
        if hasattr(config_class, 'create'):
            return config_class.create(**kwargs)
        else:
            return config_class(**kwargs)
    
    def validate_plugin_compatibility(self, plugin_name: str) -> bool:
        """Validate plugin compatibility with current ALGOViz version."""
        if plugin_name not in self.loaded_plugins:
            return False
        
        plugin_info = self.loaded_plugins[plugin_name]
        requires = plugin_info.get("requires", [])
        
        # Simple version checking (could be enhanced)
        for requirement in requires:
            if requirement.startswith("agloviz"):
                # Check ALGOViz version compatibility
                pass
        
        return True

# Global plugin manager
plugin_manager = PluginManager()
```

## 9. Migration Strategy

### 9.1 Current State Assessment

**Files Requiring Changes:**
- `src/agloviz/core/director.py` - Remove BFS-specific actions
- `src/agloviz/widgets/grid.py` - Refactor to pure visual operations
- `src/agloviz/widgets/queue.py` - Refactor to generic queue operations
- `src/agloviz/core/routing.py` - Enhance routing system for scene configs
- `src/agloviz/cli/app.py` - Update CLI to use scene configurations
- `storyboards/bfs_demo.yaml` - Update to use new action system

**New Files Required:**
- `src/agloviz/widgets/primitives/` - All primitive widgets
- `src/agloviz/widgets/structures/` - All data structure widgets
- `src/agloviz/widgets/layouts/` - All layout engines
- `src/agloviz/widgets/domains/` - All domain-specific widgets
- `src/agloviz/core/scene.py` - Scene engine and configuration
- `src/agloviz/core/plugins.py` - Plugin management system

### 9.2 Migration Phases

#### Phase 1: Foundation (Week 1)
**Goal**: Establish new widget hierarchy without breaking existing functionality

**Tasks**:
1. Create primitive widget classes (TokenWidget, MarkerWidget, etc.)
2. Create layout engine classes (LinearLayout, Grid2DLayout, etc.)
3. Create base ContainerWidget and data structure widgets
4. Implement SceneConfig and SceneEngine classes
5. Create basic scene configurations for BFS

**Validation**: 
- New widgets can be instantiated
- Scene configurations can be loaded
- SceneEngine can route basic events

#### Phase 2: Scene Integration (Week 2)
**Goal**: Integrate scene system with Director and CLI

**Tasks**:
1. Modify Director to use SceneEngine instead of direct widget management
2. Remove BFS-specific actions from Director core
3. Update CLI commands to accept scene configuration parameters
4. Create BFSSceneConfig that replicates current functionality
5. Update routing system to work with scene configurations

**Validation**:
- Director can execute storyboards using scene configurations
- CLI commands work with new scene system
- BFS visualization works with clean, generic architecture

#### Phase 3: Widget Refactoring (Week 3)
**Goal**: Refactor existing widgets to new architecture

**Tasks**:
1. Refactor GridWidget to use new primitive + layout system
2. Refactor QueueWidget to be purely generic
3. Create PathfindingGrid as domain-specific extension
4. Update BFS routing to use new widget methods
5. Create domain-specific scene configurations

**Validation**:
- All new tests pass with clean widget implementations
- BFS visualization works with new generic architecture
- New widgets are truly generic and reusable across algorithm types

#### Phase 4: Plugin System (Week 4)
**Goal**: Implement plugin architecture and enhance configurability

**Tasks**:
1. Implement PluginRegistry and PluginManager
2. Create example plugin for advanced features
3. Add plugin discovery to CLI
4. Enhance parameter template system
5. Add conditional execution support

**Validation**:
- Plugins can be loaded and registered
- Plugin widgets work in scene configurations
- CLI shows available plugins and their widgets

#### Phase 5: Documentation and Testing (Week 5)
**Goal**: Complete migration with full testing and documentation

**Tasks**:
1. Update all tests to use new architecture
2. Create comprehensive widget tests
3. Write migration guide for existing users
4. Create plugin development guide
5. Update all planning documents

**Validation**:
- All tests pass with new architecture
- Documentation is complete and accurate
- Migration guide successfully helps users transition

### 9.3 Clean Implementation Strategy

**No Backward Compatibility**:
The new architecture will completely replace the existing widget system without backward compatibility concerns. This enables:

- **Clean Architecture**: No legacy code or compatibility layers
- **Simplified Implementation**: Focus on optimal design without constraints
- **Better Performance**: No overhead from compatibility adapters
- **Cleaner APIs**: No deprecated methods or confusing interfaces

**Implementation Approach**:
```python
# Complete replacement of existing widgets
# Old: src/agloviz/widgets/grid.py (BFS-specific)
# New: src/agloviz/widgets/domains/pathfinding/grid.py (domain-specific)

# Old: src/agloviz/widgets/queue.py (BFS-specific)  
# New: src/agloviz/widgets/structures/queue.py (generic)

# Old: Hard-coded routing in Director
# New: Configuration-driven scene system
```

**Migration Approach**:
- **Complete Rewrite**: Existing widgets will be completely rewritten using new architecture
- **Fresh Start**: No attempt to maintain old APIs or interfaces
- **Clean Slate**: Remove all BFS-specific pollution from core components

### 9.4 Testing Strategy for New Architecture

**Comprehensive Testing**:
```python
class NewArchitectureTestSuite:
    """Test suite for validating new widget architecture."""
    
    def test_widget_hierarchy_functionality(self):
        """Ensure all widget levels work correctly."""
        # Test primitive widgets, data structure widgets, domain widgets
        pass
    
    def test_scene_configuration_system(self):
        """Ensure scene configurations work properly."""
        # Test event binding, parameter resolution, widget instantiation
        pass
    
    def test_event_routing_system(self):
        """Ensure events route correctly to widgets."""
        # Test event flow through scene engine
        pass
    
    def test_plugin_system(self):
        """Ensure plugin system works correctly."""
        # Test plugin discovery, registration, widget loading
        pass
```

**Golden Tests**:
- Establish new visual output standards with clean architecture
- Create reference implementations for each algorithm type
- Use image comparison for visual regression testing against new standards

## 10. Implementation Phases

### 10.1 Phase 1: Foundation Architecture (2 weeks)

#### Week 1: Core Widget Hierarchy
**Deliverables**:
- Complete primitive widget implementations (TokenWidget, MarkerWidget, ConnectionWidget, HighlightWidget)
- Layout engine implementations (LinearLayout, Grid2DLayout, TreeLayout)
- Base ContainerWidget with generic operations
- Basic data structure widgets (ArrayWidget, QueueWidget, StackWidget, TreeWidget, GraphWidget)

**Acceptance Criteria**:
- All primitive widgets can be instantiated and perform basic operations
- Layout engines correctly position elements
- Data structure widgets support add/remove/highlight operations
- Unit tests for all new widget classes
- Documentation for widget hierarchy

#### Week 2: Scene Configuration System
**Deliverables**:
- SceneConfig and EventBinding Pydantic models
- SceneEngine with event routing and parameter resolution
- ParameterTemplateEngine with expression support
- ConditionalExecutor for conditional event execution
- Basic hydra-zen configuration builders

**Acceptance Criteria**:
- Scene configurations can be loaded from Python objects
- Event bindings can be resolved and executed
- Parameter templates work with algorithm events
- Scene engine can instantiate widgets from configurations
- Integration tests for scene system

### 10.2 Phase 2: Director Integration (2 weeks)

#### Week 3: Director Refactoring
**Deliverables**:
- Refactored Director to use SceneEngine
- Removal of BFS-specific actions from Director core
- Enhanced Director with scene configuration support
- Updated CLI commands to accept scene parameters
- BFSSceneConfig that replicates current functionality

**Acceptance Criteria**:
- Director executes storyboards using scene configurations
- BFS visualization works with new architecture
- CLI commands accept scene configuration parameters
- All existing Director tests pass
- Performance is maintained or improved

#### Week 4: Routing System Enhancement
**Deliverables**:
- Enhanced routing system for scene configurations
- Updated BFS routing to use new widget methods
- Event binding validation and error handling
- Integration with existing VizEvent system
- CLI commands for scene validation

**Acceptance Criteria**:
- Event routing works through scene configurations
- Multiple widgets can respond to same event in order
- Conditional execution works correctly
- Error handling provides helpful messages
- BFS algorithm produces same visual output

### 10.3 Phase 3: Widget Architecture Implementation (2 weeks)

#### Week 5: Widget Refactoring
**Deliverables**:
- Refactored existing GridWidget to use new architecture
- Refactored existing QueueWidget to be generic
- PathfindingGrid as domain-specific extension
- SortingArray and TraversalTree domain widgets
- Updated widget tests for new architecture

**Acceptance Criteria**:
- All existing widgets work with new architecture
- Domain-specific widgets provide algorithm-specific methods
- Visual output is identical to previous implementation
- Widget tests have high coverage
- Performance benchmarks show no regression

#### Week 6: Domain Package Organization
**Deliverables**:
- Organized widget packages (primitives, structures, layouts, domains)
- Domain-specific scene configurations
- Example scene configurations for multiple algorithms
- Widget factory functions and builders
- Documentation for widget organization

**Acceptance Criteria**:
- Package structure is clean and logical
- Domain packages are self-contained
- Scene configurations work for different algorithm types
- Widget discovery and instantiation works correctly
- Code organization follows established patterns

### 10.4 Phase 4: Plugin System and Advanced Features (2 weeks)

#### Week 7: Plugin Architecture
**Deliverables**:
- PluginRegistry and PluginManager implementations
- WidgetPlugin base class and registration system
- Plugin discovery through entry points
- Example plugin with custom widgets
- CLI commands for plugin management

**Acceptance Criteria**:
- Plugins can be discovered and loaded automatically
- Plugin widgets work in scene configurations
- Plugin system is secure and error-tolerant
- CLI shows available plugins and their widgets
- Plugin development documentation is complete

#### Week 8: Advanced Configuration Features
**Deliverables**:
- Enhanced parameter template system with functions
- Conditional execution with complex expressions
- Scene configuration validation and error reporting
- Performance optimizations for large scenes
- Advanced hydra-zen integration

**Acceptance Criteria**:
- Complex parameter templates work correctly
- Conditional execution supports various comparison operators
- Scene validation provides helpful error messages
- Performance is optimized for complex scenes
- Hydra-zen integration provides type safety

### 10.5 Phase 5: Migration and Documentation (1 week)

#### Week 9: Documentation and Finalization
**Deliverables**:
- Complete implementation guide for new architecture
- Plugin development guide
- Updated planning documents
- Comprehensive testing suite
- Performance benchmarks and optimization

**Acceptance Criteria**:
- Implementation guide provides clear instructions for new architecture
- Plugin development guide enables third-party development
- All planning documents are updated and consistent
- Test suite has high coverage and passes consistently
- Performance benchmarks show optimal results

## 11. Validation and Success Criteria

### 11.1 Technical Success Criteria

**Architecture Quality**:
- ✅ Pure visual widgets with no algorithm knowledge
- ✅ Generic data structure widgets reusable across algorithms
- ✅ Domain-specific widgets only when patterns are reused
- ✅ Configuration-driven event binding system
- ✅ Plugin system supports external extensions
- ✅ Hydra-zen first with selective Hydra usage

**Functionality Excellence**:
- ✅ BFS visualization uses clean, generic architecture
- ✅ All CLI commands work with new scene configuration system
- ✅ Performance is optimized for new architecture
- ✅ All tests validate new implementation thoroughly
- ✅ Error handling is comprehensive and helpful

**Extensibility Validation**:
- ✅ Sorting algorithm can be implemented using new widgets
- ✅ Tree algorithm can be implemented using new widgets
- ✅ Plugin can add custom widgets and scene configurations
- ✅ New algorithms require no changes to core Director
- ✅ Scene configurations can be composed and reused

### 11.2 User Experience Success Criteria

**Developer Experience**:
- ✅ Widget development is simpler and more intuitive
- ✅ Scene configuration is declarative and readable
- ✅ Plugin development is well-documented and supported
- ✅ Error messages are helpful and actionable
- ✅ CLI provides good discoverability of features

**Implementation Experience**:
- ✅ New architecture is clean and well-designed
- ✅ Implementation guide is comprehensive and accurate
- ✅ New features are discoverable and well-documented
- ✅ Performance is optimized for the new architecture
- ✅ No legacy code or compatibility overhead

### 11.3 Long-term Architectural Goals

**Scalability**:
- ✅ System can support 10+ algorithm families
- ✅ Plugin ecosystem can grow without core changes
- ✅ Scene configurations can handle complex visualizations
- ✅ Performance scales with complexity appropriately
- ✅ Memory usage is efficient for large scenes

**Maintainability**:
- ✅ Code is well-organized and follows consistent patterns
- ✅ Dependencies are minimal and well-justified
- ✅ Testing is comprehensive and maintainable
- ✅ Documentation is complete and up-to-date
- ✅ New contributors can understand and extend the system

---

## Summary

This document defines a complete architectural redesign of the ALGOViz widget system to address fundamental design flaws and create a truly generic, extensible, and plugin-friendly visualization framework. The new architecture features:

1. **Multi-Level Widget Hierarchy**: Pure visual primitives, generic data structures, and domain-specific extensions
2. **Configuration-Driven Event Binding**: Declarative scene configurations with parameter templates and conditional execution
3. **Hydra-Zen First Philosophy**: Type-safe configurations with selective Hydra usage for advanced features
4. **Plugin Architecture**: Extensible system for third-party widgets and scene configurations
5. **Clean Migration Strategy**: Backward compatibility with deprecation warnings and migration helpers

The implementation spans 5 phases over 9 weeks, with careful attention to maintaining existing functionality while building a foundation for long-term extensibility and maintainability. This architecture will enable ALGOViz to support any algorithm type while maintaining the high-quality, world-class engineering standards established in the project vision.
