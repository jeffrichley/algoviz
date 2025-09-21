# ALGOViz Design Doc — Widgets & Component Registry v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Complete rewrite for Widget Architecture v2.0 - multi-level hierarchy and scene configuration)
**Supersedes:** planning/v1/ALGOViz_Design_Widgets_Registry.md

---

## 1. Purpose

Widgets in ALGOViz v2.0 follow a **multi-level hierarchy** that separates concerns:
- **Level 1**: Pure visual primitives (Manim integration)
- **Level 2**: Generic data structure abstractions
- **Level 3**: Domain-specific extensions for algorithm families

The **Component Registry** manages widget discovery and instantiation, while the **Scene Configuration System** handles event binding and widget lifecycle through declarative configuration.

**Key Principles:**
- Widgets know nothing about algorithms or events
- Event handling is configuration-driven through SceneEngine
- Pure visual operations only
- Manim integration for rendering primitives
- Plugin-extensible architecture

## 2. Widget Architecture v2.0 Overview  

Reference to [ALGOViz_Design_Widget_Architecture_v2.md](../v1/ALGOViz_Design_Widget_Architecture_v2.md) for complete architectural specification.

**Architecture Principles:**
- **Separation of Concerns**: Visual operations separate from algorithm semantics
- **Configuration-Driven**: Event handling through scene configurations
- **Multi-Level Hierarchy**: Progressive abstraction from primitives to domain-specific
- **Plugin-Ready**: Extensible without core code modification

## 3. Multi-Level Widget Hierarchy

### 3.1 Level 1: Primitive Visual Elements (Manim Integration)

**Philosophy**: Ultra-generic visual primitives that wrap Manim mobjects with ALGOViz-specific functionality.

```python
from manim import Rectangle, Circle, Text, Line, Arrow, Dot
from pydantic import BaseModel

class TokenWidget(BaseModel):
    """Wrapper around Manim mobjects for algorithm visualization."""
    mobject: Rectangle | Circle | Text  # Manim primitive
    position: tuple[float, float] = (0.0, 0.0)
    
    def move_to(self, position: tuple[float, float], duration: float = 1.0):
        """Pure visual: move token to position using Manim animation."""
        
    def highlight(self, color: str, duration: float = 1.0):
        """Pure visual: change color using Manim FadeToColor."""
        
    def show(self, scene: Scene, **kwargs) -> None:
        """Initialize and render widget."""
        
    def hide(self, scene: Scene) -> None:
        """Clean teardown and removal."""

class LineWidget(BaseModel):
    """Wrapper around Manim Line/Arrow for connections."""
    mobject: Line | Arrow
    start_pos: tuple[float, float]
    end_pos: tuple[float, float]
    
    def update_endpoints(self, start: tuple[float, float], end: tuple[float, float]):
        """Pure visual: update line endpoints."""
        
    def animate_draw(self, duration: float = 1.0):
        """Pure visual: animate line drawing."""
```

### 3.2 Level 2: Data Structure Abstractions  

**Philosophy**: Generic data structure concepts using Level 1 primitives.

```python
class ArrayWidget(BaseModel):
    """Generic array visualization using TokenWidget elements."""
    elements: list[TokenWidget]
    layout: LinearLayout
    
    def highlight_element(self, index: int, style: str, duration: float = 1.0):
        """Generic visual: highlight array element."""
        if 0 <= index < len(self.elements):
            self.elements[index].highlight(self.get_style_color(style), duration)
    
    def swap_elements(self, i: int, j: int, duration: float = 1.0):
        """Generic visual: swap two array elements."""
        if 0 <= i < len(self.elements) and 0 <= j < len(self.elements):
            # Animate position swap using Manim
            pass
    
    def add_element(self, element: Any, index: int = None, **kwargs):
        """Generic visual: add element to array."""
        
    def remove_element(self, index: int, **kwargs):
        """Generic visual: remove element from array."""

class QueueWidget(BaseModel):
    """Generic queue visualization using TokenWidget elements."""
    elements: list[TokenWidget]
    layout: QueueLayout
    
    def enqueue(self, element: Any, **kwargs):
        """Generic visual: add element to queue rear."""
        
    def dequeue(self, **kwargs) -> Any:
        """Generic visual: remove element from queue front."""
        
    def highlight_element(self, identifier: Any, style: str, **kwargs):
        """Generic visual: highlight specific queue element."""

class StackWidget(BaseModel):
    """Generic stack visualization using TokenWidget elements."""
    elements: list[TokenWidget]
    layout: StackLayout
    
    def push(self, element: Any, **kwargs):
        """Generic visual: add element to stack top."""
        
    def pop(self, **kwargs) -> Any:
        """Generic visual: remove element from stack top."""
        
    def highlight_element(self, identifier: Any, style: str, **kwargs):
        """Generic visual: highlight specific stack element."""
```

### 3.3 Level 3: Domain-Specific Extensions

**Philosophy**: Algorithm-family-specific extensions when patterns are reused.

```python
class PathfindingGrid(ArrayWidget):
    """Grid specialized for pathfinding algorithms."""
    
    def mark_start(self, pos: tuple[int, int]):
        """Pathfinding semantic: mark start position."""
        index = pos[0] * self.width + pos[1]
        self.highlight_element(index, "start")
    
    def mark_goal(self, pos: tuple[int, int]):
        """Pathfinding semantic: mark goal position."""
        index = pos[0] * self.width + pos[1]
        self.highlight_element(index, "goal")
    
    def mark_obstacle(self, pos: tuple[int, int]):
        """Pathfinding semantic: mark obstacle position."""
        index = pos[0] * self.width + pos[1]
        self.highlight_element(index, "obstacle")

class SortingArray(ArrayWidget):
    """Array specialized for sorting algorithms."""
    
    def compare_elements(self, i: int, j: int, result: str):
        """Sorting semantic: show comparison result."""
        self.highlight_element(i, "comparing")
        self.highlight_element(j, "comparing")
        # Show comparison indicator
    
    def mark_sorted(self, start: int, end: int):
        """Sorting semantic: mark range as sorted."""
        for i in range(start, end + 1):
            self.highlight_element(i, "sorted")
```

## 4. Widget Contract (Pure Visual Operations)

### 4.1 Primitive Widget Protocol
```python
class PrimitiveWidget(Protocol):
    """Protocol for Level 1 primitive widgets."""
    def show(self, scene: Scene, **kwargs) -> None:
        """Initialize and render widget."""
        
    def hide(self, scene: Scene) -> None:
        """Clean teardown and removal."""
    
    # NO update() method - no event handling
```

### 4.2 Data Structure Widget Protocol
```python
class DataStructureWidget(Protocol):
    """Protocol for Level 2 data structure widgets."""
    def add_element(self, element: Any, **kwargs) -> None:
        """Add element to data structure."""
        
    def remove_element(self, identifier: Any, **kwargs) -> None:
        """Remove element from data structure."""
        
    def highlight_element(self, identifier: Any, style: str, **kwargs) -> None:
        """Highlight specific element."""
    
    # NO event handling - pure visual operations only
```

### 4.3 Domain Widget Protocol
```python
class DomainWidget(Protocol):
    """Protocol for Level 3 domain-specific widgets."""
    # Inherits from appropriate Level 2 protocol
    # Adds domain-specific semantic methods
    # Still NO event handling - pure visual operations only
```

## 5. Scene Configuration Integration

### 5.1 SceneConfig and WidgetSpec
```python
class WidgetSpec(BaseModel):
    """Configuration for widget instantiation."""
    name: str = Field(..., description="Unique widget name")
    _target_: str = Field(..., description="Widget class path")
    params: dict[str, Any] = Field(default_factory=dict)
    
class SceneConfig(BaseModel):
    """Complete scene configuration."""
    widgets: dict[str, WidgetSpec]
    event_bindings: dict[str, list[EventBinding]]
    layout_config: dict[str, Any] = Field(default_factory=dict)
```

### 5.2 Event Binding System
```python
class EventBinding(BaseModel):
    """Binds algorithm events to widget actions."""
    widget: str = Field(..., description="Target widget name")
    action: str = Field(..., description="Widget method to call")
    params: dict[str, Any] = Field(default_factory=dict)
    order: int = Field(1, description="Execution order")
    conditions: dict[str, Any] = Field(default_factory=dict)

# Example scene configuration
BFSSceneConfig = SceneConfig(
    widgets={
        "grid": WidgetSpec(name="grid", _target_="agloviz.widgets.domains.PathfindingGrid"),
        "queue": WidgetSpec(name="queue", _target_="agloviz.widgets.structures.QueueWidget")
    },
    event_bindings={
        "enqueue": [
            EventBinding(widget="queue", action="enqueue", params={"element": "${event.node}"}, order=1),
            EventBinding(widget="grid", action="highlight_element", params={"index": "${event.pos}", "style": "frontier"}, order=2)
        ]
    }
)
```

### 5.3 Parameter Template Resolution
Templates like `${event.pos}` resolve to actual event data at runtime.

```python
# Template resolution in SceneEngine
def resolve_parameters(self, params: dict, context: dict) -> dict:
    resolved = {}
    for key, value in params.items():
        if isinstance(value, str) and value.startswith("${"):
            template_path = value[2:-1]  # Remove ${ and }
            resolved[key] = self.resolve_template_path(template_path, context)
        else:
            resolved[key] = value
    return resolved
```

## 6. Component Registry (Enhanced)

### 6.1 Multi-Level Registration
```python
class ComponentRegistry:
    def __init__(self):
        self._primitives = {}     # Level 1: Visual primitives
        self._structures = {}     # Level 2: Data structures
        self._domains = {}        # Level 3: Domain-specific
        self._layouts = {}        # Layout engines
        
    def register_primitive(self, name: str, factory: Callable[[], PrimitiveWidget]):
        """Register Level 1 primitive widget."""
        self._primitives[name] = factory
        
    def register_structure(self, name: str, factory: Callable[[], DataStructureWidget]):
        """Register Level 2 data structure widget."""
        self._structures[name] = factory
        
    def register_domain(self, name: str, factory: Callable[[], DomainWidget]):
        """Register Level 3 domain-specific widget."""
        self._domains[name] = factory
    
    def get_widget(self, widget_path: str) -> Widget:
        """Get widget by hierarchical path (e.g., 'structures.queue')."""
        level, name = widget_path.split('.', 1)
        
        if level == "primitives":
            return self._primitives[name]()
        elif level == "structures":
            return self._structures[name]()
        elif level == "domains":
            return self._domains[name]()
        else:
            raise KeyError(f"Unknown widget level: {level}")
```

### 6.2 Plugin Integration
```python
def register_plugin_widgets(self, plugin_widgets: dict[str, Callable]):
    """Register widgets from plugins with namespace."""
    for widget_path, factory in plugin_widgets.items():
        # widget_path format: "plugin_name.level.widget_name"
        parts = widget_path.split('.')
        if len(parts) == 3:
            plugin, level, name = parts
            full_path = f"{level}.{plugin}_{name}"
            self.register_by_level(level, full_path, factory)
```

### 6.3 Widget Discovery and Validation
```python
def validate_widget_hierarchy(self, widget_class: type) -> bool:
    """Validate widget follows proper hierarchy protocols."""
    # Check for event handling methods (forbidden)
    forbidden_methods = ['update', 'handle_event', 'process_event']
    for method in forbidden_methods:
        if hasattr(widget_class, method):
            raise ValueError(f"Widget {widget_class} has forbidden method {method}")
    
    # Check for required visual methods
    required_methods = ['show', 'hide']
    for method in required_methods:
        if not hasattr(widget_class, method):
            raise ValueError(f"Widget {widget_class} missing required method {method}")
    
    return True
```

## 7. Manim Integration Strategy

### 7.1 Primitive Wrapper Classes
```python
class ManimTokenWrapper(TokenWidget):
    """Wrapper around Manim Rectangle/Circle/Text."""
    
    def __init__(self, mobject_type: str = "rectangle", **kwargs):
        if mobject_type == "rectangle":
            self.mobject = Rectangle(**kwargs)
        elif mobject_type == "circle":
            self.mobject = Circle(**kwargs)
        elif mobject_type == "text":
            self.mobject = Text(**kwargs)
    
    def move_to(self, position: tuple[float, float], duration: float = 1.0):
        """Move using Manim animations."""
        return self.mobject.animate.move_to([position[0], position[1], 0])
    
    def highlight(self, color: str, duration: float = 1.0):
        """Change color using Manim FadeToColor."""
        return FadeToColor(self.mobject, color)
```

### 7.2 Layout Engine Integration
```python
class LinearLayout:
    """Layout engine for arranging widgets in lines."""
    
    def arrange_widgets(self, widgets: list[Widget], direction: str = "horizontal"):
        """Arrange widgets using Manim positioning."""
        if direction == "horizontal":
            return VGroup(*[w.mobject for w in widgets]).arrange(RIGHT)
        else:
            return VGroup(*[w.mobject for w in widgets]).arrange(DOWN)

class GridLayout:
    """Layout engine for arranging widgets in grids."""
    
    def arrange_grid(self, widgets: list[list[Widget]], spacing: float = 1.0):
        """Arrange widgets in grid formation."""
        rows = []
        for row in widgets:
            row_group = VGroup(*[w.mobject for w in row]).arrange(RIGHT, buff=spacing)
            rows.append(row_group)
        return VGroup(*rows).arrange(DOWN, buff=spacing)
```

### 7.3 Animation System Integration
```python
class AnimationController:
    """Coordinates Manim animations for widget operations."""
    
    def animate_sequence(self, animations: list[Animation], duration: float):
        """Execute sequence of Manim animations."""
        return Succession(*animations, run_time=duration)
    
    def animate_parallel(self, animations: list[Animation], duration: float):
        """Execute parallel Manim animations."""
        return AnimationGroup(*animations, run_time=duration)
```

## 8. Domain-Specific Extensions

### 8.1 Pathfinding Domain Package
```python
# agloviz/widgets/domains/pathfinding/
class PathfindingGrid(ArrayWidget):
    """Grid specialized for pathfinding algorithms."""
    
    def mark_start(self, pos: tuple[int, int]):
        """Mark start position with pathfinding semantics."""
        
    def mark_goal(self, pos: tuple[int, int]):
        """Mark goal position with pathfinding semantics."""
        
    def show_path(self, path: list[tuple[int, int]]):
        """Highlight discovered path."""

class PathTracer(LineWidget):
    """Animated path visualization for pathfinding."""
    
    def trace_path(self, path: list[tuple[int, int]], duration: float = 2.0):
        """Animate path discovery."""
```

### 8.2 Sorting Domain Package
```python
# agloviz/widgets/domains/sorting/
class SortingArray(ArrayWidget):
    """Array specialized for sorting algorithms."""
    
    def compare_elements(self, i: int, j: int, result: str):
        """Show comparison between elements."""
        
    def mark_sorted(self, start: int, end: int):
        """Mark range as sorted."""
        
    def show_partition(self, pivot_index: int, left: int, right: int):
        """Show partitioning around pivot."""

class ComparisonIndicator(PrimitiveWidget):
    """Visual indicator for element comparisons."""
    
    def show_comparison(self, pos1: tuple[float, float], pos2: tuple[float, float]):
        """Show comparison between two positions."""
```

### 8.3 Tree Domain Package
```python
# agloviz/widgets/domains/trees/
class TreeWidget(BaseModel):
    """Generic tree visualization."""
    nodes: dict[Any, TokenWidget]
    edges: dict[tuple[Any, Any], LineWidget]
    layout: TreeLayout
    
    def highlight_node(self, node_id: Any, style: str, **kwargs):
        """Highlight specific tree node."""
        
    def highlight_edge(self, parent: Any, child: Any, style: str, **kwargs):
        """Highlight edge between nodes."""
        
    def show_traversal_path(self, path: list[Any]):
        """Show traversal path through tree."""
```

## 9. Plugin Integration

### 9.1 Widget Plugin Architecture
```python
class WidgetPlugin(Protocol):
    """Protocol for widget plugins."""
    
    def register_widgets(self, registry: ComponentRegistry) -> None:
        """Register plugin widgets with the component registry."""
        
    def get_scene_configs(self) -> dict[str, type[SceneConfig]]:
        """Return scene configurations provided by plugin."""
        
    def get_widget_factories(self) -> dict[str, Callable]:
        """Return widget factory functions."""

# Plugin registration example
class MyAlgorithmPlugin:
    def register_widgets(self, registry: ComponentRegistry):
        registry.register_structure("my_plugin.priority_queue", PriorityQueueWidget)
        registry.register_domain("my_plugin.graph_visualizer", GraphVisualizerWidget)
```

### 9.2 Scene Configuration Plugins
```python
class PluginSceneConfig(SceneConfig):
    """Base class for plugin scene configurations."""
    
    @classmethod
    def create_for_algorithm(cls, algorithm_name: str) -> SceneConfig:
        """Factory method for algorithm-specific configurations."""
        
# Plugin scene configuration example
class AStarSceneConfig(PluginSceneConfig):
    @staticmethod
    def create() -> SceneConfig:
        return SceneConfig(
            widgets={
                "grid": WidgetSpec(name="grid", _target_="domains.pathfinding.PathfindingGrid"),
                "queue": WidgetSpec(name="queue", _target_="structures.priority_queue.PriorityQueueWidget")
            },
            event_bindings={
                "node_expanded": [
                    EventBinding(widget="grid", action="highlight_element", 
                               params={"index": "${event.pos}", "style": "expanded"}, order=1),
                    EventBinding(widget="queue", action="enqueue", 
                               params={"element": "${event.neighbors}", "priority": "${event.f_score}"}, order=2)
                ]
            }
        )
```

### 9.3 Plugin Discovery and Loading
```python
class PluginManager:
    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
        self.loaded_plugins = {}
    
    def discover_plugins(self) -> list[WidgetPlugin]:
        """Discover widget plugins via entry points."""
        plugins = []
        for entry_point in pkg_resources.iter_entry_points('agloviz.widget_plugins'):
            plugin_class = entry_point.load()
            plugins.append(plugin_class())
        return plugins
    
    def load_plugin_widgets(self, plugin: WidgetPlugin):
        """Load widgets from a plugin."""
        try:
            plugin.register_widgets(self.registry)
            self.loaded_plugins[plugin.__class__.__name__] = plugin
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin}: {e}")
```

## 10. Testing Strategy

### 10.1 Multi-Level Testing Approach
```python
# Level 1: Primitive widget tests
def test_token_widget_manim_integration():
    token = TokenWidget(mobject_type="rectangle")
    scene = Scene()
    token.show(scene)
    assert token.mobject in scene.mobjects

# Level 2: Data structure widget tests  
def test_array_widget_generic_operations():
    array = ArrayWidget(size=10)
    array.highlight_element(5, "visited")
    assert array.elements[5].style == "visited"

# Level 3: Domain widget tests
def test_pathfinding_grid_semantics():
    grid = PathfindingGrid(width=10, height=10)
    grid.mark_start((0, 0))
    assert grid.get_element(0).style == "start"
```

### 10.2 Scene Configuration Testing
```python
def test_scene_configuration_widget_instantiation():
    scene_config = BFSSceneConfig.create()
    scene_engine = SceneEngine(scene_config)
    scene_engine.initialize_widgets()
    
    assert "grid" in scene_engine.widgets
    assert isinstance(scene_engine.widgets["grid"], PathfindingGrid)

def test_event_binding_parameter_resolution():
    event = VizEvent("enqueue", {"node": (5, 5), "pos": 25})
    binding = EventBinding(widget="grid", action="highlight_element", 
                          params={"index": "${event.pos}", "style": "frontier"})
    
    resolved = scene_engine.resolve_parameters(binding.params, {"event": event})
    assert resolved == {"index": 25, "style": "frontier"}
```

### 10.3 Integration Testing
```python
def test_widget_hierarchy_integration():
    """Test that all three levels work together."""
    # Level 1: Create primitive
    token = TokenWidget(mobject_type="circle")
    
    # Level 2: Use in data structure
    queue = QueueWidget()
    queue.elements.append(token)
    
    # Level 3: Use in domain widget
    grid = PathfindingGrid(width=10, height=10)
    grid.elements[0] = token
    
    # Verify hierarchy works
    grid.mark_start((0, 0))
    assert token.style == "start"
```

## 11. Migration from v1.0

### 11.1 Breaking Changes
- **Widget Contract**: Removed `update()` method - no more event handling in widgets
- **Event Routing**: Moved from widgets to scene configuration system
- **Widget Examples**: Removed BFS-specific examples, added generic + domain-specific
- **Registry**: Enhanced for multi-level hierarchy registration

### 11.2 New Concepts
- **Multi-Level Hierarchy**: 3-level widget organization
- **Scene Configuration**: Declarative event binding system
- **SceneEngine**: Widget lifecycle and event routing management
- **Parameter Templates**: Runtime resolution of event data

### 11.3 Implementation Path
1. **Implement Level 1**: Manim wrapper widgets
2. **Implement Level 2**: Generic data structure widgets
3. **Implement SceneEngine**: Widget lifecycle and event routing
4. **Implement Level 3**: Domain-specific extensions
5. **Update Registry**: Multi-level registration system
6. **Plugin Integration**: Widget plugin support

---
