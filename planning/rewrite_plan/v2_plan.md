# ALGOViz Planning Documents v2.0 Migration Plan

**Owner:** Development Team  
**Status:** Execution Plan  
**Created:** 2025-01-20  
**Purpose:** Systematic migration of all planning documents to support Widget Architecture v2.0

---

## 🎯 **Overview**

This document provides a detailed, step-by-step plan to systematically recreate all planning documents in the `planning/v2/` directory with the new Widget Architecture v2.0. The migration addresses fundamental architectural conflicts discovered during Phase 1.4 Director Implementation.

**Migration Structure:**
- `planning/v1/` - Original documents (archived)
- `planning/v2/` - New architecture documents (current)
- Complete rewrite approach with no backward compatibility

**Total Estimated Time:** 7.5 hours  
**Documents to Migrate:** 16 documents

---

## 📋 **Phase 1: Document Analysis and Prioritization (30 minutes)**

### **Step 1.1: Inventory Current Documents (5 minutes)**
```bash
# Verify document structure
ls -la planning/v1/
ls -la planning/v2/

# Count documents to migrate
find planning/v1/ -name "*.md" | wc -l
```

**Expected Output:** 16 markdown files in v1, empty v2 directory

### **Step 1.2: Categorize Documents by Update Type (25 minutes)**

#### **Category A: Complete Rewrite Required (Architecture Changes)**
**Reason:** Fundamental conflicts with Widget Architecture v2.0

1. **ALGOViz_Design_Widgets_Registry.md**
   - **Conflicts:** Single-level widget system, widgets handle events directly, BFS-specific examples
   - **Changes:** Multi-level hierarchy, scene configuration system, generic widgets
   - **Effort:** 90 minutes

2. **ALGOViz_Design_Director.md**
   - **Conflicts:** Algorithm-specific actions, direct widget management, simple routing
   - **Changes:** Pure orchestrator, SceneEngine integration, scene configuration routing
   - **Effort:** 60 minutes

3. **ALGOViz_Design_Storyboard_DSL.md**
   - **Conflicts:** Algorithm-specific actions in core list, no scene configuration
   - **Changes:** Generic actions only, scene configuration action resolution
   - **Effort:** 45 minutes

#### **Category B: Major Section Updates (Examples/Integration Changes)**
**Reason:** Integration points and examples need updating for new architecture

4. **ALGOViz_Design_Adapters_VizEvents.md**
   - **Conflicts:** BFS-specific routing examples, direct widget method calls
   - **Changes:** Generic routing examples, scene configuration integration
   - **Effort:** 30 minutes

5. **ALGOViz_PRD.md**
   - **Conflicts:** Widget naming inconsistencies, phase ordering
   - **Changes:** Consistent naming, updated phase descriptions
   - **Effort:** 30 minutes

6. **ALGOViz_SDD.md**
   - **Conflicts:** Package structure, component diagrams
   - **Changes:** Multi-level widget package structure, updated diagrams
   - **Effort:** 45 minutes

#### **Category C: Minor Updates (Examples/References)**
**Reason:** Examples and references need adjustment for new architecture

7. **ALGOViz_Design_Plugin_System.md**
   - **Conflicts:** Plugin API examples use algorithm-specific actions
   - **Changes:** Scene configuration integration, updated examples
   - **Effort:** 20 minutes

8. **ALGOViz_Design_DI_Strategy.md**
   - **Conflicts:** Widget registry examples, hydra-zen integration examples
   - **Changes:** Scene configuration DI, updated widget examples
   - **Effort:** 25 minutes

#### **Category D: Copy As-Is (No Conflicts)**
**Reason:** No conflicts with Widget Architecture v2.0

9. **ALGOViz_Design_Config_System.md** - Copy unchanged
10. **ALGOViz_Design_TimingConfig.md** - Copy unchanged
11. **ALGOViz_Design_Voiceover.md** - Copy unchanged
12. **ALGOViz_Design_Rendering_Export.md** - Copy unchanged
13. **ALGOViz_Error_Taxonomy.md** - Copy unchanged
14. **ALGOViz_Vision_Goals.md** - Copy unchanged
15. **ALGOViz_Scenario_Theme_Merge_Precedence.md** - Copy unchanged
16. **README_DOCS.md** - Copy and update for v2.0 structure

**Effort:** 15 minutes total

---

## 📋 **Phase 2: Category D - Copy Unchanged Documents (15 minutes)**

### **Step 2.1: Copy No-Conflict Documents (10 minutes)**

**Execute in sequence:**

1. Copy ALGOViz_Design_Config_System.md
2. Copy ALGOViz_Design_TimingConfig.md
3. Copy ALGOViz_Design_Voiceover.md
4. Copy ALGOViz_Design_Rendering_Export.md
5. Copy ALGOViz_Error_Taxonomy.md
6. Copy ALGOViz_Vision_Goals.md
7. Copy ALGOViz_Scenario_Theme_Merge_Precedence.md

### **Step 2.2: Update Headers for v2.0 (5 minutes)**

**For each copied document, add v2.0 header:**
```markdown
# ALGOViz Design Doc — [Component] v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0)  
**Last Updated:** 2025-01-20
**Version:** v2.0 (No changes from v1.0 - no conflicts with Widget Architecture v2.0)
**Supersedes:** planning/v1/ALGOViz_Design_[Component].md

---
```

**Validation:** 7 documents copied with updated headers

---

## 📋 **Phase 3: Category A - Complete Rewrites (3 hours)**

### **Step 3.1: ALGOViz_Design_Widgets_Registry_v2.md (90 minutes)**

#### **Document Structure:**
```markdown
# ALGOViz Design Doc — Widgets & Component Registry v2.0

## 1. Purpose
Multi-level widget hierarchy with pure visual primitives, generic data structures, and domain-specific extensions.

## 2. Widget Architecture v2.0 Overview  
Reference to ALGOViz_Design_Widget_Architecture_v2.md

## 3. Multi-Level Widget Hierarchy
### 3.1 Level 1: Primitive Visual Elements (Manim Integration)
### 3.2 Level 2: Data Structure Abstractions  
### 3.3 Level 3: Domain-Specific Extensions

## 4. Widget Contract (Pure Visual Operations)
### 4.1 Primitive Widget Protocol
### 4.2 Data Structure Widget Protocol
### 4.3 Domain Widget Protocol

## 5. Scene Configuration Integration
### 5.1 SceneConfig and WidgetSpec
### 5.2 Event Binding System
### 5.3 Parameter Template Resolution

## 6. Component Registry (Enhanced)
### 6.1 Multi-Level Registration
### 6.2 Plugin Integration
### 6.3 Widget Discovery and Validation

## 7. Manim Integration Strategy
### 7.1 Primitive Wrapper Classes
### 7.2 Layout Engine Integration
### 7.3 Animation System Integration

## 8. Domain-Specific Extensions
### 8.1 Pathfinding Domain Package
### 8.2 Sorting Domain Package
### 8.3 Tree Domain Package

## 9. Plugin Integration
### 9.1 Widget Plugin Architecture
### 9.2 Scene Configuration Plugins
### 9.3 Plugin Discovery and Loading

## 10. Testing Strategy
### 10.1 Multi-Level Testing Approach
### 10.2 Scene Configuration Testing
### 10.3 Integration Testing

## 11. Migration from v1.0
### 11.1 Breaking Changes
### 11.2 New Concepts
### 11.3 Implementation Path
```

#### **Key Content Updates:**
- **Widget Contract**: Remove `update(scene, event, run_time)` method
- **Examples**: Replace BFS-specific widgets with generic + domain-specific
- **Registry**: Add multi-level registration and plugin support
- **Integration**: Add scene configuration and SceneEngine integration

### **Step 3.2: ALGOViz_Design_Director_v2.md (60 minutes)**

#### **Document Structure:**
```markdown
# ALGOViz Design Doc — Director v2.0

## 1. Purpose
Pure orchestrator that executes storyboards using scene configurations, with no algorithm-specific knowledge.

## 2. Responsibilities (Updated)
### 2.1 Core Orchestration Only
### 2.2 Scene Configuration Integration
### 2.3 Generic Action Resolution

## 3. SceneEngine Integration (New Section)
### 3.1 Scene Configuration Loading
### 3.2 Widget Lifecycle Management
### 3.3 Event Routing Through SceneEngine

## 4. Class Sketch (Updated)
### 4.1 Director Class with SceneEngine
### 4.2 Generic Action Registry
### 4.3 Scene Configuration Support

## 5. Event Playback (Updated)
### 5.1 Scene Configuration Routing
### 5.2 Parameter Template Resolution
### 5.3 Conditional Event Execution

## 6. Actions & Routing (Updated)
### 6.1 Core Generic Actions Only
### 6.2 Scene Configuration Action Resolution
### 6.3 Algorithm-Specific Actions in Scene Configs

## 7. Timing (Unchanged)

## 8. Transitions (Unchanged)

## 9. Error Handling (Updated)
### 9.1 Scene Configuration Errors
### 9.2 Widget Resolution Errors
### 9.3 Event Binding Errors

## 10. Testing (Updated)
### 10.1 Generic Director Testing
### 10.2 Scene Configuration Testing
### 10.3 Multi-Algorithm Validation

## 11. Performance (Updated)

## 12. Migration from v1.0
### 12.1 Removed Algorithm-Specific Actions
### 12.2 New Scene Configuration Requirements
### 12.3 Updated Integration Points
```

#### **Key Content Updates:**
- **Responsibilities**: Remove algorithm-specific items, add scene configuration
- **Class Sketch**: Update to use SceneEngine instead of direct widget management
- **Event Playback**: Update routing to use scene configurations
- **Actions**: Remove algorithm-specific actions, keep only generic orchestration

### **Step 3.3: ALGOViz_Design_Storyboard_DSL_v2.md (45 minutes)**

#### **Document Structure:**
```markdown
# ALGOViz Design Doc — Storyboard DSL v2.0

## 1. Purpose (Updated)
Declarative language for describing algorithm visualizations using scene configurations.

## 2. DSL Structure (Unchanged)

## 3. Core Actions (Updated - Generic Only)
### 3.1 Generic Orchestration Actions
### 3.2 Scene Configuration Integration
### 3.3 Action Resolution Process

## 4. Scene Configuration Actions (New Section)
### 4.1 Algorithm-Specific Actions in Scene Configs
### 4.2 Domain-Specific Action Examples
### 4.3 Event Binding Integration

## 5. Action Resolution (Updated)
### 5.1 Core Action Registry
### 5.2 Scene Configuration Action Resolution
### 5.3 Plugin Action Integration

## 6. Validation & Loading (Updated)

## 7. Examples (Updated)
### 7.1 Generic Storyboard Examples
### 7.2 Scene Configuration Examples
### 7.3 Multi-Algorithm Examples

## 8. Testing (Updated)

## 9. Migration from v1.0
### 9.1 Removed Algorithm-Specific Actions
### 9.2 New Scene Configuration Requirements
### 9.3 Updated Action Resolution
```

#### **Key Content Updates:**
- **Core Actions**: Remove `place_start`, `place_goal`, `place_obstacles`, `show_complexity`, `celebrate_goal`
- **Action Resolution**: Update to use scene configuration system
- **Examples**: Replace BFS-specific examples with generic + scene configuration examples

---

## 📋 **Phase 4: Category B - Major Section Updates (2 hours)**

### **Step 4.1: ALGOViz_Design_Adapters_VizEvents_v2.md (30 minutes)**

#### **Sections to Update:**
- **Section 7: Routing Maps** - Update examples to use generic widget methods
- **Section 8: Director Integration** - Update to use SceneEngine
- **Add Section 9: Scene Configuration Integration**

#### **Key Changes:**
```markdown
## 7. Routing Maps (Updated)
Scene configuration routing replaces simple routing maps:

```python
# OLD v1.0 - Hard-coded BFS-specific methods
routing_map_bfs = {
    "enqueue": ["queue.highlight_enqueue", "grid.mark_frontier"],
    "dequeue": ["queue.highlight_dequeue"],
    "goal_found": ["grid.flash_goal", "hud.show_success"]
}

# NEW v2.0 - Scene configuration with generic methods
BFSSceneConfig.create().event_bindings = {
    "enqueue": [
        EventBinding(widget="queue", action="enqueue", params={"value": "${event.node}"}, order=1),
        EventBinding(widget="grid", action="highlight_element", params={"index": "${event.pos}", "style": "frontier"}, order=2)
    ]
}
```

## 9. Scene Configuration Integration (New Section)
### 9.1 Event Binding Configuration
### 9.2 Parameter Template System
### 9.3 Widget Resolution Process
```

### **Step 4.2: ALGOViz_PRD_v2.md (30 minutes)**

#### **Sections to Update:**
- **Phase Descriptions** - Update to reflect new phase ordering
- **Widget Naming** - Make consistent with new architecture
- **Feature Lists** - Update to reflect scene configuration approach

#### **Key Changes:**
```markdown
### **Phase 1** (Updated)
- **Algorithm Support**: BFS using clean widget architecture
- **Storyboard DSL**: Acts → Shots → Beats with scene configuration integration
- **Director**: Pure orchestrator using SceneEngine
- **Widgets**: Multi-level hierarchy (primitives, data structures, domain-specific)
- **Scene Configuration**: Event binding system with parameter templates

### **Phase 2** (Updated)
- **Widget Architecture Foundation**: Complete multi-level widget hierarchy
- **Plugin System**: Widget plugins with scene configuration integration
- **Framework Completion**: Clean, generic foundation ready for algorithms

### **Phase 3** (New)
- **Additional Algorithms**: DFS, Dijkstra, A* using clean architecture
- **Algorithm-Specific Scene Configurations**: Domain-specific scene configs
- **Multi-Algorithm Validation**: Prove architecture works across algorithm types
```

### **Step 4.3: ALGOViz_SDD_v2.md (45 minutes)**

#### **Sections to Update:**
- **Package Structure** - Update to show multi-level widget hierarchy
- **Component Diagrams** - Update to show scene configuration system
- **Integration Descriptions** - Update Director and widget integration

#### **Key Changes:**
```markdown
## 3. High-Level Architecture (Updated)

```
agloviz/
├─ adapters/         # Algorithm implementations → VizEvents
├─ core/             # Director, SceneEngine, routing, storyboard
├─ widgets/          # Multi-level widget hierarchy
│  ├─ primitives/    # Level 1: Manim wrapper widgets
│  ├─ structures/    # Level 2: Generic data structure widgets
│  ├─ layouts/       # Layout engines for positioning
│  └─ domains/       # Level 3: Algorithm-specific extensions
├─ config/           # Configuration management
└─ cli/              # Command-line interface
```

## 5. Widget Architecture (Updated)
### 5.1 Multi-Level Widget Hierarchy
### 5.2 Scene Configuration System
### 5.3 Event Binding Architecture

## 8. Director Integration (Updated)
### 8.1 SceneEngine Integration
### 8.2 Scene Configuration Loading
### 8.3 Generic Action Resolution
```

### **Step 4.4: Validation for Category B (15 minutes)**
- Verify all major sections updated
- Check cross-references work
- Ensure examples are consistent

---

## 📋 **Phase 5: Category C - Minor Updates (1 hour)**

### **Step 5.1: ALGOViz_Design_Plugin_System_v2.md (20 minutes)**

#### **Sections to Update:**
- **Section 5: Plugin API** - Remove algorithm-specific action examples
- **Add Section 7: Widget Plugin Integration**

#### **Key Changes:**
```markdown
## 5. Plugin API (Updated)
```python
# my_pkg/plugins.py
def register(registry) -> None:
    # Algorithm registration (unchanged)
    registry.register_algorithm("a_star", a_star_adapter_factory)
    
    # Widget registration (updated for scene system)
    registry.register_widget("advanced_grid", AdvancedGridWidget)
    registry.register_scene_config("a_star_scene", AStarSceneConfig)
    
    # Actions now handled by scene configurations
    # No more: registry.register_action("celebrate_goal", celebrate_goal_action)
```

## 7. Widget Plugin Integration (New Section)
### 7.1 Widget Plugin Protocol
### 7.2 Scene Configuration Plugins
### 7.3 Plugin Widget Discovery
```

### **Step 5.2: ALGOViz_Design_DI_Strategy_v2.md (25 minutes)**

#### **Sections to Update:**
- **Section 13: Widget Registry Example** - Update to use multi-level hierarchy
- **Add Section 14: Scene Configuration DI**

#### **Key Changes:**
```markdown
## 13. Widget Registry via DI Factories (Updated)
```python
# core/registry.py  
def build_component_registry(plugins) -> "ComponentRegistry":
    reg = ComponentRegistry()
    
    # Level 2: Data structure widgets
    reg.register("structures.array", lambda: ArrayWidget())
    reg.register("structures.queue", lambda: QueueWidget())
    reg.register("structures.stack", lambda: StackWidget())
    
    # Level 3: Domain-specific widgets
    reg.register("pathfinding.grid", lambda: PathfindingGrid())
    reg.register("sorting.array", lambda: SortingArray())
    
    # Plugin widgets
    for wname, factory in plugins.widget_factories():
        reg.register(f"plugin.{wname}", factory)
    
    return reg
```

## 14. Scene Configuration DI (New Section)
### 14.1 Hydra-Zen Scene Configurations
### 14.2 Widget Instantiation via DI
### 14.3 Parameter Template Resolution
```

### **Step 5.3: Validation for Category C (15 minutes)**
- Check examples are updated correctly
- Verify no algorithm-specific pollution remains
- Ensure plugin integration is consistent

---

## 📋 **Phase 6: Category A - Complete Rewrites (3 hours)**

### **Step 6.1: ALGOViz_Design_Widgets_Registry_v2.md (90 minutes)**

#### **Detailed Content Plan:**

**Section 1: Purpose (15 minutes)**
```markdown
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
```

**Section 3: Multi-Level Widget Hierarchy (30 minutes)**
```markdown
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
        
    def swap_elements(self, i: int, j: int, duration: float = 1.0):
        """Generic visual: swap two array elements."""
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
```
```

**Section 4: Widget Contract (20 minutes)**
```markdown
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
```

**Section 5: Scene Configuration Integration (25 minutes)**
```markdown
## 5. Scene Configuration Integration

### 5.1 SceneConfig and WidgetSpec
```python
class WidgetSpec(BaseModel):
    """Configuration for widget instantiation."""
    name: str = Field(..., description="Unique widget name")
    _target_: str = Field(..., description="Widget class path")
    
class SceneConfig(BaseModel):
    """Complete scene configuration."""
    widgets: dict[str, WidgetSpec]
    event_bindings: dict[str, list[EventBinding]]
```

### 5.2 Event Binding System
```python
class EventBinding(BaseModel):
    """Binds algorithm events to widget actions."""
    widget: str = Field(..., description="Target widget name")
    action: str = Field(..., description="Widget method to call")
    params: dict[str, Any] = Field(default_factory=dict)
    order: int = Field(1, description="Execution order")
```

### 5.3 Parameter Template Resolution
Templates like `${event.pos}` resolve to actual event data at runtime.
```

#### **Validation Criteria:**
- All BFS-specific examples removed
- Multi-level hierarchy clearly explained
- Scene configuration integration documented
- Manim integration strategy defined

### **Step 6.2: ALGOViz_Design_Director_v2.md (60 minutes)**

#### **Detailed Content Plan:**

**Section 2: Responsibilities (15 minutes)**
```markdown
## 2. Responsibilities (Updated for v2.0)

### 2.1 Core Orchestration Only
1. Load & validate `Storyboard`
2. Resolve **generic actions** via action registry
3. Apply **TimingConfig** (modes + categories)
4. Integrate **voiceover** with **hybrid timing**
5. Handle **bookmarks** (scaffold)
6. Record timings via **TimingTracker**
7. Manage act/shot transitions

### 2.2 Scene Configuration Integration (New)
8. Load scene configurations for algorithm-specific behavior
9. Delegate widget lifecycle to SceneEngine
10. Route events through scene configuration system
11. Resolve algorithm-specific actions via scene configs

### 2.3 Removed Responsibilities
- ❌ Algorithm-specific action implementation
- ❌ Direct widget management  
- ❌ Hard-coded routing maps
- ❌ Widget lifecycle management (delegated to SceneEngine)
```

**Section 3: SceneEngine Integration (20 minutes)**
```markdown
## 3. SceneEngine Integration (New Section)

### 3.1 Scene Configuration Loading
```python
class Director:
    def __init__(self, scene, storyboard, timing, scene_config, **kwargs):
        self.scene_engine = SceneEngine(scene_config)
        # Director delegates widget management to SceneEngine
```

### 3.2 Widget Lifecycle Management
- SceneEngine instantiates widgets from scene configuration
- Director calls SceneEngine for widget show/hide
- No direct widget management in Director

### 3.3 Event Routing Through SceneEngine
- Algorithm events routed through scene configuration
- Parameter template resolution in SceneEngine
- Conditional execution support
```

**Section 4: Class Sketch (15 minutes)**
```markdown
## 4. Class Sketch (Updated for v2.0)
```python
class Director:
    def __init__(self, scene, storyboard, timing, scene_config, **kwargs):
        self.scene = scene
        self.storyboard = storyboard
        self.timing = timing
        self.scene_engine = SceneEngine(scene_config)  # NEW
        self.mode = mode
        self.with_voice = with_voice
        
        # Only generic actions registered
        self._register_core_actions()  # show_title, show_widgets, play_events, outro

    def _run_beat(self, beat, ai, si, bi):
        # Resolve action through scene configuration if not core action
        if beat.action in self.core_actions:
            handler = self.core_actions[beat.action]
        else:
            # Delegate to scene configuration
            self.scene_engine.execute_action(beat.action, beat.args, run_time, context)
```
```

**Section 5: Event Playback (10 minutes)**
```markdown
## 5. Event Playback (Updated for Scene Configuration)

- Director obtains **AlgorithmAdapter** from registry
- Adapter yields **VizEvent**s
- Director passes events to **SceneEngine** for routing
- SceneEngine uses **scene configuration** to bind events to widget actions
- Parameter templates resolve event data to widget method parameters
- Multiple widgets can respond to same event in configured order
```

#### **Validation Criteria:**
- No algorithm-specific actions in Director responsibilities
- SceneEngine integration clearly documented
- Event routing updated for scene configuration
- Class sketch shows clean architecture

### **Step 6.3: ALGOViz_Design_Storyboard_DSL_v2.md (45 minutes)**

#### **Detailed Content Plan:**

**Section 3: Core Actions (20 minutes)**
```markdown
## 3. Core Actions (Updated - Generic Only)

### 3.1 Generic Orchestration Actions
| Action | Description | Expected Args |
|---|---|---|
| `show_title` | Show title card | `text: str`, `subtitle: str` |
| `show_widgets` | Show widgets from scene config | widget names: `queue: true`, `grid: true` |
| `play_events` | Stream adapter events via scene routing | `routing_override: dict` (optional) |
| `outro` | Fade out/credits | `text: str` (optional) |

### 3.2 Removed Algorithm-Specific Actions
**No longer in core actions (moved to scene configurations):**
- ❌ `place_start` - Now in PathfindingSceneConfig
- ❌ `place_goal` - Now in PathfindingSceneConfig
- ❌ `place_obstacles` - Now in PathfindingSceneConfig
- ❌ `show_complexity` - Now in AlgorithmAnalysisSceneConfig
- ❌ `celebrate_goal` - Now in PathfindingSceneConfig

### 3.3 Action Resolution Process
1. Check if action is core generic action
2. If not, resolve through scene configuration
3. Scene configuration provides action implementation
4. Parameter templates resolve event data
```

**Section 4: Scene Configuration Actions (15 minutes)**
```markdown
## 4. Scene Configuration Actions (New Section)

### 4.1 Algorithm-Specific Actions in Scene Configs
Algorithm-specific actions are now handled by scene configurations:

```python
class BFSSceneConfig(BaseModel):
    @staticmethod
    def create() -> SceneConfig:
        return SceneConfig(
            action_handlers={
                "place_start": lambda scene, args, run_time, context: 
                    scene_engine.get_widget("grid").mark_start(args["pos"]),
                "place_goal": lambda scene, args, run_time, context:
                    scene_engine.get_widget("grid").mark_goal(args["pos"])
            }
        )
```

### 4.2 Domain-Specific Action Examples
- **Pathfinding**: `place_start`, `place_goal`, `place_obstacles`, `celebrate_goal`
- **Sorting**: `compare_elements`, `swap_elements`, `partition_array`, `show_sorted`
- **Trees**: `highlight_node`, `show_path`, `traverse_subtree`

### 4.3 Event Binding Integration
Scene configurations also handle event binding for `play_events` action.
```

**Section 5: Action Resolution (10 minutes)**
```markdown
## 5. Action Resolution (Updated for Scene Configuration)

### 5.1 Resolution Process
1. **Core Action Check**: Is action in Director's core actions?
2. **Scene Configuration Check**: Is action defined in scene configuration?
3. **Plugin Action Check**: Is action provided by loaded plugins?
4. **Error Handling**: Provide helpful error with available actions

### 5.2 Priority Order
1. Core generic actions (highest priority)
2. Scene configuration actions
3. Plugin-provided actions
4. Error if not found

### 5.3 Parameter Resolution
- Static parameters passed directly
- Template parameters (`${event.pos}`) resolved at runtime
- Context parameters (act/shot/beat indices) available
```

#### **Validation Criteria:**
- Core actions list contains only generic actions
- Algorithm-specific actions documented in scene configuration section
- Action resolution process clearly explained
- Examples updated to use new system

---

## 📋 **Phase 7: Cross-Reference Updates (30 minutes)**

### **Step 7.1: Create Cross-Reference Update Script (10 minutes)**

**Create update script:**
```bash
#!/bin/bash
# planning/v2/update_references.sh

echo "Updating cross-references to v2.0 documents..."

# Update all references in v2 documents to point to v2 versions
find planning/v2/ -name "*.md" -exec sed -i '' \
  's/ALGOViz_Design_Widgets_Registry\.md/ALGOViz_Design_Widgets_Registry_v2.md/g' {} \;

find planning/v2/ -name "*.md" -exec sed -i '' \
  's/ALGOViz_Design_Director\.md/ALGOViz_Design_Director_v2.md/g' {} \;

find planning/v2/ -name "*.md" -exec sed -i '' \
  's/ALGOViz_Design_Storyboard_DSL\.md/ALGOViz_Design_Storyboard_DSL_v2.md/g' {} \;

find planning/v2/ -name "*.md" -exec sed -i '' \
  's/ALGOViz_Design_Adapters_VizEvents\.md/ALGOViz_Design_Adapters_VizEvents_v2.md/g' {} \;

find planning/v2/ -name "*.md" -exec sed -i '' \
  's/ALGOViz_PRD\.md/ALGOViz_PRD_v2.md/g' {} \;

find planning/v2/ -name "*.md" -exec sed -i '' \
  's/ALGOViz_SDD\.md/ALGOViz_SDD_v2.md/g' {} \;

find planning/v2/ -name "*.md" -exec sed -i '' \
  's/ALGOViz_Design_Plugin_System\.md/ALGOViz_Design_Plugin_System_v2.md/g' {} \;

find planning/v2/ -name "*.md" -exec sed -i '' \
  's/ALGOViz_Design_DI_Strategy\.md/ALGOViz_Design_DI_Strategy_v2.md/g' {} \;

echo "Cross-reference updates complete!"
```

### **Step 7.2: Update Implementation Plan References (10 minutes)**

**Update Implementation_Plan.md to reference v2.0 documents:**
```bash
# Update Implementation Plan to use v2 planning docs
sed -i '' 's|planning/v2/ALGOViz_Design_|planning/v2/ALGOViz_Design_|g' Implementation_Plan.md
sed -i '' 's|planning/v2/\.md|planning/v2/ALGOViz_PRD_v2.md|g' Implementation_Plan.md
sed -i '' 's|planning/v2/ALGOViz_SDD\.md|planning/v2/ALGOViz_SDD_v2.md|g' Implementation_Plan.md
```

### **Step 7.3: Execute Cross-Reference Updates (10 minutes)**

**Run the update script and validate:**
```bash
chmod +x planning/v2/update_references.sh
./planning/v2/update_references.sh

# Validate no broken references
grep -r "\[.*\](.*\.md" planning/v2/ | grep -v "_v2.md" | grep -v "v1/"
```

---

## 📋 **Phase 8: Documentation Index and README (30 minutes)**

### **Step 8.1: Create planning/v2/README_DOCS.md (20 minutes)**

```markdown
# ALGOViz Planning Documents v2.0

**Architecture Version:** v2.0 (Widget Architecture Redesign)  
**Status:** Current  
**Previous Version:** planning/v1/ (archived)  
**Key Changes:** Multi-level widget hierarchy, scene configuration system, clean architecture

---

## 🏗️ **Architecture v2.0 Overview**

The v2.0 architecture addresses fundamental design flaws discovered during Phase 1.4:
- **Multi-Level Widget Hierarchy**: Pure visual primitives, generic data structures, domain-specific extensions
- **Configuration-Driven Event Binding**: Declarative scene configurations with parameter templates
- **Clean Architecture**: No algorithm-specific pollution in core components
- **Manim Integration**: Leverage existing Manim primitives, add ALGOViz-specific functionality

## 📚 **Document Categories**

### **Core Architecture Documents (v2.0 - Major Updates)**
- [ALGOViz_Design_Widget_Architecture_v2.md](ALGOViz_Design_Widget_Architecture_v2.md) - **NEW** - Complete architecture redesign
- [ALGOViz_Design_Widgets_Registry_v2.md](ALGOViz_Design_Widgets_Registry_v2.md) - Multi-level widget hierarchy
- [ALGOViz_Design_Director_v2.md](ALGOViz_Design_Director_v2.md) - Pure orchestrator with scene integration
- [ALGOViz_Design_Storyboard_DSL_v2.md](ALGOViz_Design_Storyboard_DSL_v2.md) - Generic actions with scene configuration

### **Integration Documents (v2.0 - Updated Examples)**
- [ALGOViz_Design_Adapters_VizEvents_v2.md](ALGOViz_Design_Adapters_VizEvents_v2.md) - Scene configuration routing
- [ALGOViz_PRD_v2.md](ALGOViz_PRD_v2.md) - Updated phases and widget naming
- [ALGOViz_SDD_v2.md](ALGOViz_SDD_v2.md) - Multi-level package structure

### **Infrastructure Documents (v2.0 - Minor Updates)**
- [ALGOViz_Design_Plugin_System_v2.md](ALGOViz_Design_Plugin_System_v2.md) - Widget plugin integration
- [ALGOViz_Design_DI_Strategy_v2.md](ALGOViz_Design_DI_Strategy_v2.md) - Scene configuration DI

### **Infrastructure Documents (v2.0 - No Changes)**
- [ALGOViz_Design_Config_System.md](ALGOViz_Design_Config_System.md) - No conflicts
- [ALGOViz_Design_TimingConfig.md](ALGOViz_Design_TimingConfig.md) - No conflicts
- [ALGOViz_Design_Voiceover.md](ALGOViz_Design_Voiceover.md) - No conflicts
- [ALGOViz_Design_Rendering_Export.md](ALGOViz_Design_Rendering_Export.md) - No conflicts
- [ALGOViz_Error_Taxonomy.md](ALGOViz_Error_Taxonomy.md) - No conflicts
- [ALGOViz_Vision_Goals.md](ALGOViz_Vision_Goals.md) - No conflicts
- [ALGOViz_Scenario_Theme_Merge_Precedence.md](ALGOViz_Scenario_Theme_Merge_Precedence.md) - No conflicts

## 🔄 **Migration from v1.0**

### **Breaking Changes**
- Widget contract no longer includes event handling
- Algorithm-specific actions moved from Director to scene configurations
- Multi-level widget hierarchy replaces single-level system

### **What's Preserved**
- Storyboard DSL structure (Acts → Shots → Beats)
- VizEvent system and algorithm adapters
- Timing system and configuration management
- Error taxonomy and CLI framework

### **Implementation Impact**
See [Implementation_Plan.md](../../Implementation_Plan.md) Phase 1.4.1-2.1 for implementation details.
```

### **Step 8.2: Update Main README.md (10 minutes)**

**Add planning document versioning note:**
```markdown
## 📚 Planning Documents

**Current Version:** v2.0 (Widget Architecture Redesign)
- **Location:** `planning/v2/` 
- **Status:** Current architecture documents
- **Key Changes:** Multi-level widget hierarchy, scene configuration system

**Previous Version:** v1.0 (Original Architecture)
- **Location:** `planning/v1/`
- **Status:** Archived (contains BFS-specific pollution)
- **Reference:** Historical design decisions and evolution

See `planning/v2/README_DOCS.md` for complete documentation index.
```

---

## 📋 **Phase 9: Validation and Quality Check (30 minutes)**

### **Step 9.1: Document Consistency Check (15 minutes)**

**Validation Script:**
```bash
#!/bin/bash
# planning/v2/validate_docs.sh

echo "=== ALGOViz Planning Documents v2.0 Validation ==="

# Check all cross-references work
echo "Checking cross-references..."
broken_refs=0
grep -r "\[.*\](.*\.md" planning/v2/ | while read line; do
  file=$(echo "$line" | cut -d':' -f1)
  ref=$(echo "$line" | grep -o "([^)]*\.md[^)]*)" | tr -d '()')
  
  # Check if reference exists
  if [[ $ref == *"planning/v2/"* ]]; then
    if [[ ! -f "$ref" ]]; then
      echo "BROKEN: $file references missing $ref"
      broken_refs=$((broken_refs + 1))
    fi
  elif [[ $ref == *".md" ]] && [[ ! $ref == *"http"* ]]; then
    if [[ ! -f "planning/v2/$ref" ]]; then
      echo "BROKEN: $file references missing planning/v2/$ref"
      broken_refs=$((broken_refs + 1))
    fi
  fi
done

# Check for algorithm-specific pollution
echo "Checking for algorithm-specific pollution..."
pollution_count=0
grep -r "place_start\|place_goal\|place_obstacles\|celebrate_goal\|show_complexity" planning/v2/ | grep -v "# OLD\|# PROBLEMATIC\|moved to scene" && {
  echo "WARNING: Found algorithm-specific pollution in v2.0 docs"
  pollution_count=$((pollution_count + 1))
}

# Check for old widget contract usage
echo "Checking for old widget contract..."
grep -r "def update.*VizEvent" planning/v2/ && {
  echo "WARNING: Found old widget contract in v2.0 docs"
  pollution_count=$((pollution_count + 1))
}

# Check for BFS-specific examples
echo "Checking for BFS-specific examples..."
grep -r "highlight_enqueue\|mark_frontier\|flash_goal" planning/v2/ | grep -v "# OLD\|# PROBLEMATIC" && {
  echo "WARNING: Found BFS-specific examples in v2.0 docs"
  pollution_count=$((pollution_count + 1))
}

echo "=== Validation Summary ==="
echo "Broken references: $broken_refs"
echo "Architecture pollution instances: $pollution_count"

if [[ $broken_refs -eq 0 ]] && [[ $pollution_count -eq 0 ]]; then
  echo "✅ All validations passed!"
  exit 0
else
  echo "❌ Validation issues found"
  exit 1
fi
```

### **Step 9.2: Architecture Alignment Check (15 minutes)**

**Check each document aligns with Widget Architecture v2.0:**

1. **Multi-Level Hierarchy**: Verify all documents reference 3-level widget system
2. **Scene Configuration**: Verify all documents use scene configuration approach
3. **Generic Core**: Verify no algorithm-specific pollution in core components
4. **Manim Integration**: Verify appropriate use of Manim primitives
5. **Plugin Architecture**: Verify consistent plugin integration approach

**Manual Checklist:**
- [ ] All widget examples use multi-level hierarchy
- [ ] All event handling uses scene configuration
- [ ] All routing examples use generic widget methods
- [ ] All action examples distinguish core vs scene-specific
- [ ] All plugin examples use scene configuration integration

---

## 📋 **Phase 10: Final Integration (15 minutes)**

### **Step 10.1: Update Implementation Plan Cross-References (10 minutes)**

**Update all planning document references in Implementation_Plan.md:**
```bash
# Update Implementation Plan to reference v2.0 documents
sed -i '' 's|planning/v2/ALGOViz_Design_|planning/v2/ALGOViz_Design_|g' Implementation_Plan.md
sed -i '' 's|\.md\]|_v2.md]|g' Implementation_Plan.md

# Handle special cases for unchanged documents
sed -i '' 's|planning/v2/ALGOViz_Design_Config_System_v2.md|planning/v2/ALGOViz_Design_Config_System.md|g' Implementation_Plan.md
sed -i '' 's|planning/v2/ALGOViz_Design_TimingConfig_v2.md|planning/v2/ALGOViz_Design_TimingConfig.md|g' Implementation_Plan.md
# Continue for all unchanged documents...
```

### **Step 10.2: Final Validation (5 minutes)**

**Run complete validation:**
```bash
# Run validation script
./planning/v2/validate_docs.sh

# Check Implementation Plan references
grep -o "planning/v2/[^)]*\.md" Implementation_Plan.md | sort | uniq | while read ref; do
  if [[ ! -f "$ref" ]]; then
    echo "BROKEN Implementation Plan reference: $ref"
  fi
done

# Verify document count
v1_count=$(find planning/v1/ -name "*.md" | wc -l)
v2_count=$(find planning/v2/ -name "*.md" | wc -l)
echo "Document migration: v1=$v1_count, v2=$v2_count"
```

---

## 📋 **Execution Checklist**

### **Pre-Execution Verification**
- [ ] `planning/v1/` contains all 16 original documents
- [ ] `planning/v2/` is empty and ready
- [ ] `planning/v2/ALGOViz_Design_Widget_Architecture_v2.md` exists as reference

### **Phase Execution Order**
- [ ] **Phase 1**: Document analysis and prioritization (30 min)
- [ ] **Phase 2**: Copy unchanged documents (15 min)
- [ ] **Phase 5**: Minor updates (1 hour)  
- [ ] **Phase 4**: Major section updates (2 hours)
- [ ] **Phase 6**: Complete rewrites (3 hours)
- [ ] **Phase 7**: Cross-reference updates (30 min)
- [ ] **Phase 8**: Documentation index (30 min)
- [ ] **Phase 9**: Validation and quality check (30 min)
- [ ] **Phase 10**: Final integration (15 min)

### **Quality Gates**
- [ ] All 16 documents exist in planning/v2/
- [ ] No broken cross-references
- [ ] No algorithm-specific pollution in core components
- [ ] All examples align with Widget Architecture v2.0
- [ ] Implementation Plan references v2.0 documents
- [ ] Validation script passes completely

### **Success Criteria**
- ✅ Complete v2.0 documentation set ready for implementation
- ✅ All conflicts with Widget Architecture v2.0 resolved
- ✅ Clean, consistent architecture across all documents
- ✅ Implementation Plan aligned with v2.0 architecture
- ✅ Ready to begin Phase 1.4.1 Director Architecture Cleanup

---

## 🚀 **Ready for Execution**

This plan provides a systematic, step-by-step approach to migrate all planning documents to support Widget Architecture v2.0 while preserving the valuable content and ensuring consistency across the entire documentation set.

**Total Time Investment:** 7.5 hours  
**Risk Mitigation:** Systematic validation at each phase  
**Quality Assurance:** Automated validation scripts and manual quality gates  
**Outcome:** Complete, consistent v2.0 documentation ready for pristine architecture implementation
