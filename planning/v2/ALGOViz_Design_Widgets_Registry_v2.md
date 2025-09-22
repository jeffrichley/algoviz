# ALGOViz Design Doc — Widgets & Component Registry v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0 - Hydra-zen First)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Complete rewrite for Widget Architecture v2.0 - hydra-zen first multi-level hierarchy)
**Supersedes:** planning/v1/ALGOViz_Design_Widgets_Registry.md

---

## 1. Purpose

Widgets in ALGOViz v2.0 follow a **multi-level hierarchy** that separates concerns using **hydra-zen first** architecture:
- **Level 1**: Pure visual primitives (Manim integration) with structured configs
- **Level 2**: Generic data structure abstractions using `builds()` patterns
- **Level 3**: Domain-specific extensions configured through ConfigStore

The **Component Registry** manages widget discovery and instantiation through **hydra-zen structured configs**, while the **Scene Configuration System** handles event binding and widget lifecycle through declarative ConfigStore-based configuration.

**Key Principles:**
- **Hydra-zen First**: All widget configuration uses `builds()` and `instantiate()`
- **ConfigStore Integration**: Widget templates registered with ConfigStore groups
- **Pure Visual Operations**: Widgets know nothing about algorithms or events
- **Configuration-Driven**: Event handling through hydra-zen scene configurations
- **Plugin-Extensible**: Extensible through ConfigStore without core code modification

## 2. Widget Architecture v2.0 Overview (Hydra-zen First)

Reference to [ALGOViz_Design_Widget_Architecture_v2.md](../v2/ALGOViz_Design_Widget_Architecture_v2.md) for complete architectural specification.

**Architecture Principles:**
- **Hydra-zen Native**: All widget instantiation uses structured configs and `instantiate()`
- **Separation of Concerns**: Visual operations separate from algorithm semantics
- **Configuration-Driven**: Event handling through hydra-zen scene configurations
- **Multi-Level Hierarchy**: Progressive abstraction from primitives to domain-specific
- **Plugin-Ready**: Extensible through ConfigStore groups without core modification

## 3. Multi-Level Widget Hierarchy (Hydra-zen Configured)

### 3.1 Level 1: Primitive Visual Elements (Hydra-zen + Manim Integration)

**Philosophy**: Ultra-generic visual primitives configured through hydra-zen structured configs.

```python
from manim import Rectangle, Circle, Text, Line, Arrow, Dot
from pydantic import BaseModel
from hydra_zen import builds
from hydra.core.config_store import ConfigStore

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

# Hydra-zen structured configs for primitive widgets
TokenWidgetConfigZen = builds(
    TokenWidget,
    mobject_type="${token.mobject_type:rectangle}",
    position="${token.position:[0.0, 0.0]}",
    color="${token.color:#FFFFFF}",
    size="${token.size:1.0}",
    zen_partial=True,
    populate_full_signature=True
)

LineWidgetConfigZen = builds(
    LineWidget,
    start_pos="${line.start_pos:[0.0, 0.0]}",
    end_pos="${line.end_pos:[1.0, 1.0]}",
    line_type="${line.line_type:solid}",
    color="${line.color:#000000}",
    width="${line.width:2.0}",
    zen_partial=True,
    populate_full_signature=True
)
```

### 3.2 Level 2: Data Structure Abstractions (Hydra-zen Configured)

**Philosophy**: Generic data structure concepts using Level 1 primitives, configured through structured configs.

```python
from hydra_zen import builds, make_config

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

class QueueWidget(BaseModel):
    """Generic FIFO queue visualization."""
    elements: list[TokenWidget]
    layout: LinearLayout
    max_visible: int = 10
    
    def add_element(self, element: Any, **kwargs):
        """Generic visual: add element to queue rear."""
        
    def remove_element(self, **kwargs) -> Any:
        """Generic visual: remove element from queue front."""
        
# Hydra-zen structured configs for data structure widgets
ArrayWidgetConfigZen = builds(
    ArrayWidget,
    size="${array.size:10}",
    layout=builds(
        "agloviz.widgets.layouts.LinearLayout",
        orientation="${layout.orientation:horizontal}",
        spacing="${layout.spacing:1.0}",
        zen_partial=True
    ),
    element_template=TokenWidgetConfigZen,
    zen_partial=True,
    populate_full_signature=True
)

QueueWidgetConfigZen = builds(
    QueueWidget,
    max_visible="${queue.max_visible:10}",
    orientation="${queue.orientation:horizontal}",
    layout=builds(
        "agloviz.widgets.layouts.LinearLayout",
        orientation="horizontal",
        spacing=1.0,
        zen_partial=True
    ),
    zen_partial=True,
    populate_full_signature=True
)

StackWidgetConfigZen = builds(
    "agloviz.widgets.structures.StackWidget",
    layout=builds(
        "agloviz.widgets.layouts.LinearLayout",
        orientation="vertical",
        spacing=1.0,
        zen_partial=True
    ),
    zen_partial=True,
    populate_full_signature=True
)
```

### 3.3 Level 3: Domain-Specific Extensions (Hydra-zen Configured)

**Philosophy**: Algorithm-specific patterns configured through specialized structured configs.

```python
class PathfindingGrid(ArrayWidget):
    """Grid specialized for pathfinding algorithms."""
    width: int
    height: int
    start_pos: tuple[int, int] | None = None
    goal_pos: tuple[int, int] | None = None
    
    def mark_start(self, pos: tuple[int, int]):
        """Mark start position with pathfinding semantics."""
    
    def mark_goal(self, pos: tuple[int, int]):
        """Mark goal position with pathfinding semantics."""
        
    def show_frontier(self, positions: list[tuple[int, int]]):
        """Show frontier positions (pathfinding semantic)."""

class SortingArray(ArrayWidget):
    """Array specialized for sorting algorithms."""
    
    def compare_highlight(self, i: int, j: int, result: str, duration: float = 1.0):
        """Highlight comparison between elements (sorting semantic)."""
        
    def partition_marker(self, pivot_index: int):
        """Show partition marker (sorting semantic)."""
        
    def show_sorted_region(self, start: int, end: int):
        """Highlight sorted region (sorting semantic)."""

# Domain-specific structured configs
PathfindingGridConfigZen = builds(
    PathfindingGrid,
    width="${grid.width:10}",
    height="${grid.height:10}",
    cell_size="${grid.cell_size:0.5}",
    layout=builds(
        "agloviz.widgets.layouts.Grid2DLayout",
        width="${grid.width:10}",
        height="${grid.height:10}",
        cell_size="${grid.cell_size:0.5}",
        zen_partial=True
    ),
    zen_partial=True,
    populate_full_signature=True
)

SortingArrayConfigZen = builds(
    SortingArray,
    size="${array.size:10}",
    layout=builds(
        "agloviz.widgets.layouts.LinearLayout",
        orientation="horizontal",
        spacing=1.0,
        zen_partial=True
    ),
    zen_partial=True,
    populate_full_signature=True
)
```

## 4. Widget Protocols (Updated for Hydra-zen)

### 4.1 Primitive Widget Protocol
```python
from typing import Protocol
from hydra_zen import builds

class PrimitiveWidget(Protocol):
    """Protocol for Level 1 primitive widgets with hydra-zen support."""
    def show(self, scene: Scene, **kwargs) -> None:
        """Initialize and render widget."""
        
    def hide(self, scene: Scene) -> None:
        """Clean teardown and removal."""
    
    @classmethod
    def get_structured_config(cls):
        """Return hydra-zen structured config for this widget."""
        return builds(cls, zen_partial=True, populate_full_signature=True)
```

### 4.2 Data Structure Widget Protocol
```python
class DataStructureWidget(Protocol):
    """Protocol for Level 2 data structure widgets."""
    def highlight_element(self, index: int, style: str, duration: float = 1.0) -> None:
        """Generic element highlighting."""
        
    def add_element(self, element: Any, **kwargs) -> None:
        """Generic element addition."""
        
    def remove_element(self, **kwargs) -> Any:
        """Generic element removal."""
        
    @classmethod
    def get_structured_config(cls):
        """Return hydra-zen structured config for this widget."""
        return builds(cls, zen_partial=True, populate_full_signature=True)
```

### 4.3 Domain Widget Protocol
```python
class DomainWidget(Protocol):
    """Protocol for Level 3 domain-specific widgets."""
    # Inherits from appropriate Level 2 protocol
    # Adds domain-specific semantic methods
    # Still NO event handling - pure visual operations only
    
    @classmethod
    def get_structured_config(cls):
        """Return hydra-zen structured config for this widget."""
        return builds(cls, zen_partial=True, populate_full_signature=True)
```

## 5. Scene Configuration Integration (Enhanced for Hydra-zen)

### 5.1 Hydra-zen Scene Configuration
```python
from hydra_zen import builds, make_config
from hydra.core.config_store import ConfigStore

class WidgetSpec(BaseModel):
    """Hydra-zen widget specification with _target_ support."""
    name: str = Field(..., description="Unique widget name")
    _target_: str = Field(..., description="Widget class path")
    
    class Config:
        extra = "allow"  # Allow widget-specific parameters
    
class SceneConfig(BaseModel):
    """Complete scene configuration using hydra-zen patterns."""
    widgets: dict[str, WidgetSpec]
    event_bindings: dict[str, list[EventBinding]]
    timing_overrides: dict[str, float] = Field(default_factory=dict)

# Scene configuration using hydra-zen composition
BFSSceneConfigZen = make_config(
    name="bfs_pathfinding",
    algorithm="bfs",
    widgets={
        "grid": PathfindingGridConfigZen,
        "queue": QueueWidgetConfigZen,
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
            builds("agloviz.core.scene.EventBinding",
                  widget="queue",
                  action="add_element",
                  params={"element": "${event_data:event.node}"},
                  order=1),
            builds("agloviz.core.scene.EventBinding",
                  widget="grid",
                  action="show_frontier",
                  params={"positions": ["${event_data:event.pos}"]},
                  order=2)
        ]
    },
    hydra_defaults=["_self_"]
)
```

### 5.2 Enhanced Event Binding System
```python
class EventBinding(BaseModel):
    """Binds algorithm events to widget actions with hydra-zen parameter resolution."""
    widget: str = Field(..., description="Target widget name")
    action: str = Field(..., description="Widget method to call")
    params: dict[str, Any] = Field(default_factory=dict, description="Parameters with template support")
    order: int = Field(1, description="Execution order")
    condition: str | None = Field(None, description="Optional condition")

# Structured config for event bindings
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
```

## 6. Component Registry (Hydra-zen First)

### 6.1 ConfigStore-Based Widget Registration
```python
from hydra_zen import instantiate
from hydra.core.config_store import ConfigStore

class ComponentRegistry:
    """Hydra-zen first component registry using ConfigStore."""
    
    def __init__(self):
        self.cs = ConfigStore.instance()
        self._setup_core_widgets()
        
    def _setup_core_widgets(self):
        """Register core widget structured configs with ConfigStore."""
        # Register primitive widgets
        self.cs.store(group="widget", name="token", node=TokenWidgetConfigZen)
        self.cs.store(group="widget", name="line", node=LineWidgetConfigZen)
        
        # Register data structure widgets
        self.cs.store(group="widget", name="array", node=ArrayWidgetConfigZen)
        self.cs.store(group="widget", name="queue", node=QueueWidgetConfigZen)
        self.cs.store(group="widget", name="stack", node=StackWidgetConfigZen)
        
        # Register domain-specific widgets
        self.cs.store(group="widget", name="pathfinding_grid", node=PathfindingGridConfigZen)
        self.cs.store(group="widget", name="sorting_array", node=SortingArrayConfigZen)
        
        # Register layout engines
        self.cs.store(group="layout", name="linear", node=builds(
            "agloviz.widgets.layouts.LinearLayout",
            orientation="horizontal",
            spacing=1.0,
            zen_partial=True
        ))
        self.cs.store(group="layout", name="grid_2d", node=builds(
            "agloviz.widgets.layouts.Grid2DLayout",
            width=10,
            height=10,
            cell_size=1.0,
            zen_partial=True
        ))
    
    def get_widget(self, widget_name: str, **overrides):
        """Get widget instance using hydra-zen instantiation."""
        config_key = f"widget/{widget_name}"
        
        repo = self.cs.get_repo()
        if config_key not in repo:
            raise KeyError(f"Widget '{widget_name}' not found in ConfigStore")
        
        widget_config = repo[config_key].node
        
        # Apply overrides if provided
        if overrides:
            from omegaconf import OmegaConf
            override_config = OmegaConf.create(overrides)
            widget_config = OmegaConf.merge(widget_config, override_config)
        
        # Instantiate widget using hydra-zen
        return instantiate(widget_config)
    
    def register_widget(self, name: str, widget_config, group: str = "widget"):
        """Register widget structured config with ConfigStore."""
        self.cs.store(group=group, name=name, node=widget_config)
    
    def get_available_widgets(self) -> dict[str, str]:
        """Get all available widgets from ConfigStore."""
        repo = self.cs.get_repo()
        widgets = {}
        
        for config_name in repo:
            if config_name.startswith("widget/"):
                widget_name = config_name[7:]  # Remove "widget/" prefix
                widgets[widget_name] = config_name
        
        return widgets
```

### 6.2 Plugin Integration (Hydra-zen Native)
```python
def register_plugin_widgets(self, plugin_widgets: dict[str, Any]):
    """Register widgets from plugins using structured configs."""
    for widget_name, widget_config in plugin_widgets.items():
        # Ensure widget_config is a structured config
        if not hasattr(widget_config, '_target_'):
            raise ValueError(f"Plugin widget '{widget_name}' must be a structured config with _target_")
        
        # Register with plugin namespace
        plugin_name = widget_name.split('_')[0]  # Extract plugin name
        self.register_widget(f"{plugin_name}_{widget_name}", widget_config, group="widget")

def discover_plugin_widgets(self):
    """Discover plugin widgets via entry points."""
    try:
        import pkg_resources
        
        for entry_point in pkg_resources.iter_entry_points('agloviz.widget_plugins'):
            try:
                plugin_class = entry_point.load()
                plugin = plugin_class()
                
                # Get widget configs from plugin
                widget_configs = plugin.get_widget_configs()
                self.register_plugin_widgets(widget_configs)
                
            except Exception as e:
                print(f"Failed to load widget plugin '{entry_point.name}': {e}")
    except ImportError:
        pass
```

### 6.3 Widget Discovery and Validation (Enhanced)
```python
def validate_widget_config(self, widget_config) -> bool:
    """Validate widget structured config follows proper patterns."""
    # Check for _target_ field
    if not hasattr(widget_config, '_target_'):
        raise ValueError("Widget config missing _target_ field")
    
    # Check target is valid import path
    target = getattr(widget_config, '_target_')
    if not isinstance(target, str) or '.' not in target:
        raise ValueError(f"Invalid _target_ path: {target}")
    
    # Validate zen_partial is set for flexibility
    if not getattr(widget_config, 'zen_partial', False):
        print(f"Warning: Widget config {target} should use zen_partial=True for flexibility")
    
    return True

def get_widget_hierarchy(self) -> dict[str, list[str]]:
    """Get widget hierarchy organized by levels."""
    repo = self.cs.get_repo()
    hierarchy = {
        "primitives": [],
        "structures": [],
        "domains": [],
        "layouts": []
    }
    
    for config_name in repo:
        if config_name.startswith("widget/"):
            widget_name = config_name[7:]
            widget_config = repo[config_name].node
            target = getattr(widget_config, '_target_', '')
            
            # Categorize by target path
            if 'primitives' in target:
                hierarchy["primitives"].append(widget_name)
            elif 'structures' in target:
                hierarchy["structures"].append(widget_name)
            elif 'domains' in target:
                hierarchy["domains"].append(widget_name)
        elif config_name.startswith("layout/"):
            layout_name = config_name[7:]
            hierarchy["layouts"].append(layout_name)
    
    return hierarchy
```

## 7. Manim Integration Strategy (Hydra-zen Enhanced)

### 7.1 Primitive Wrapper Classes with Structured Configs
```python
class ManimTokenWrapper(TokenWidget):
    """Wrapper around Manim Rectangle/Circle/Text with hydra-zen support."""
    
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

# Structured config for Manim wrapper
ManimTokenWrapperConfigZen = builds(
    ManimTokenWrapper,
    mobject_type="${token.mobject_type:rectangle}",
    color="${token.color:#FFFFFF}",
    size="${token.size:1.0}",
    zen_partial=True,
    populate_full_signature=True
)
```

### 7.2 Layout Engine Integration (Hydra-zen Configured)
```python
class LinearLayout:
    """Layout engine for arranging widgets in lines."""
    
    def __init__(self, orientation: str = "horizontal", spacing: float = 1.0):
        self.orientation = orientation
        self.spacing = spacing
    
    def arrange_widgets(self, widgets: list[Widget]):
        """Arrange widgets using Manim positioning."""
        if self.orientation == "horizontal":
            return VGroup(*[w.mobject for w in widgets]).arrange(RIGHT, buff=self.spacing)
        else:
            return VGroup(*[w.mobject for w in widgets]).arrange(DOWN, buff=self.spacing)

class GridLayout:
    """Layout engine for arranging widgets in grids."""
    
    def __init__(self, width: int, height: int, spacing: float = 1.0):
        self.width = width
        self.height = height
        self.spacing = spacing
    
    def arrange_grid(self, widgets: list[list[Widget]]):
        """Arrange widgets in grid formation."""
        rows = []
        for row in widgets:
            row_group = VGroup(*[w.mobject for w in row]).arrange(RIGHT, buff=self.spacing)
            rows.append(row_group)
        return VGroup(*rows).arrange(DOWN, buff=self.spacing)

# Structured configs for layout engines
LinearLayoutConfigZen = builds(
    LinearLayout,
    orientation="${layout.orientation:horizontal}",
    spacing="${layout.spacing:1.0}",
    zen_partial=True,
    populate_full_signature=True
)

GridLayoutConfigZen = builds(
    GridLayout,
    width="${layout.width:10}",
    height="${layout.height:10}",
    spacing="${layout.spacing:1.0}",
    zen_partial=True,
    populate_full_signature=True
)
```

## 8. Domain-Specific Extensions (Hydra-zen Native)

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

# Domain-specific structured configs
PathfindingDomainConfigZen = make_config(
    grid=PathfindingGridConfigZen,
    path_tracer=builds(
        PathTracer,
        color="${path.color:#00FF00}",
        width="${path.width:3.0}",
        zen_partial=True
    ),
    hydra_defaults=["_self_"]
)
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

# Sorting domain structured configs
SortingDomainConfigZen = make_config(
    array=SortingArrayConfigZen,
    comparison_indicator=builds(
        ComparisonIndicator,
        color="${indicator.color:#FF0000}",
        size="${indicator.size:0.3}",
        zen_partial=True
    ),
    hydra_defaults=["_self_"]
)
```

## 9. Widget Registration and Discovery (Complete Example)

### 9.1 Complete Registry Setup
```python
def register_all_widgets():
    """Register all widget structured configs with ConfigStore."""
    cs = ConfigStore.instance()
    
    # Core primitive widgets
    cs.store(group="widget", name="token", node=TokenWidgetConfigZen)
    cs.store(group="widget", name="line", node=LineWidgetConfigZen)
    cs.store(group="widget", name="manim_token", node=ManimTokenWrapperConfigZen)
    
    # Data structure widgets
    cs.store(group="widget", name="array", node=ArrayWidgetConfigZen)
    cs.store(group="widget", name="queue", node=QueueWidgetConfigZen)
    cs.store(group="widget", name="stack", node=StackWidgetConfigZen)
    
    # Domain-specific widgets
    cs.store(group="widget", name="pathfinding_grid", node=PathfindingGridConfigZen)
    cs.store(group="widget", name="sorting_array", node=SortingArrayConfigZen)
    
    # Layout engines
    cs.store(group="layout", name="linear", node=LinearLayoutConfigZen)
    cs.store(group="layout", name="grid", node=GridLayoutConfigZen)
    
    # Domain packages
    cs.store(group="domain", name="pathfinding", node=PathfindingDomainConfigZen)
    cs.store(group="domain", name="sorting", node=SortingDomainConfigZen)

# Usage example
registry = ComponentRegistry()
registry.discover_plugin_widgets()

# Get widget using hydra-zen instantiation
grid_widget = registry.get_widget("pathfinding_grid", width=15, height=15)
queue_widget = registry.get_widget("queue", max_visible=8)
```

### 9.2 CLI Integration
```python
# CLI commands for widget discovery
def list_available_widgets():
    """CLI command to list all available widgets."""
    registry = ComponentRegistry()
    hierarchy = registry.get_widget_hierarchy()
    
    for level, widgets in hierarchy.items():
        print(f"{level.upper()}:")
        for widget in widgets:
            print(f"  - {widget}")

def create_widget_from_cli(widget_name: str, **overrides):
    """CLI command to create widget with parameter overrides."""
    registry = ComponentRegistry()
    widget = registry.get_widget(widget_name, **overrides)
    return widget
```

## 10. Migration Strategy

### 10.1 Phase 1: Core Widget Structured Configs
**Goal**: Convert all existing widgets to use hydra-zen structured configs

**Tasks**:
1. Create structured configs using `builds()` for all primitive widgets
2. Update data structure widgets to use structured config composition
3. Convert domain-specific widgets to use `builds()` patterns
4. Register all configs with ConfigStore using appropriate groups

### 10.2 Phase 2: Registry Migration
**Goal**: Update ComponentRegistry to use ConfigStore instead of manual factories

**Tasks**:
1. Replace manual factory registration with ConfigStore integration
2. Update widget instantiation to use `instantiate()` instead of factory calls
3. Add plugin discovery through ConfigStore groups
4. Update CLI commands to work with structured configs

### 10.3 Phase 3: Integration Testing
**Goal**: Validate complete hydra-zen widget system

**Tasks**:
1. Test widget instantiation through ConfigStore
2. Validate scene configuration integration
3. Test plugin system with structured configs
4. Performance testing of hydra-zen instantiation

## 11. Success Criteria

### 11.1 Hydra-zen Integration Success
- ✅ All widgets use structured configs with `builds()` patterns
- ✅ ConfigStore registration works for all widget types and levels
- ✅ Widget instantiation uses `instantiate()` throughout
- ✅ Plugin system works with structured configs
- ✅ CLI integration supports ConfigStore widget discovery

### 11.2 Architecture Quality
- ✅ Pure visual widgets with no algorithm knowledge maintained
- ✅ Multi-level hierarchy preserved with structured config support
- ✅ Scene configuration integration enhanced with hydra-zen
- ✅ Plugin system supports external widget extensions
- ✅ Performance maintained or improved with structured configs

---

## Summary

This Widget Registry v2.0 document defines a complete hydra-zen first widget system that seamlessly integrates with the Configuration System, DI Strategy, and Widget Architecture. The registry features:

1. **Hydra-zen Native Widget Configuration**: All widgets use `builds()` and structured configs
2. **ConfigStore Integration**: Complete widget template registration and discovery
3. **Multi-Level Hierarchy**: Primitives, data structures, and domain-specific widgets with structured configs
4. **Plugin Architecture**: Extensible system using ConfigStore groups and structured config registration
5. **Scene Configuration Integration**: Enhanced event binding with hydra-zen parameter resolution

The implementation provides a world-class, extensible widget registry that supports any algorithm type while maintaining the high engineering standards established in the ALGOViz project vision.
