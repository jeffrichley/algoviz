I'll systematically review all planning documents to identify conflicts with the new widget architecture v2.0 plan. Let me analyze each document.

[8 tools called]

## 🚨 **CONFLICTS FOUND IN PLANNING DOCUMENTS**

Here are all the conflicts I found between the existing planning documents and the new Widget Architecture v2.0:

---

## **1. ALGOViz_Design_Widgets_Registry.md - MAJOR CONFLICTS**

### **Widget Contract Conflicts**
**Current Doc Says:**
```python
class Widget(Protocol):
    def show(self, scene, **kwargs): ...
    def update(self, scene, event: VizEvent, run_time: float): ...  # ❌ CONFLICT
    def hide(self, scene): ...
```

**Widget Architecture v2.0 Says:**
- Widgets should NOT handle events directly
- Event handling should be configuration-driven through SceneEngine
- Widgets should only have pure visual operations

### **Widget Examples Conflicts**
**Current Doc Lists:**
- `QueueWidget`: Visual representation of BFS queue ❌ (BFS-specific)
- `GridWidget`: 2D grid with colored cells ❌ (Should be generic ArrayWidget)
- `HUDWidget`: Overlay for complexity/time counters ❌ (Algorithm-specific)

**Should Be:**
- Generic data structure widgets (ArrayWidget, QueueWidget)
- Domain-specific extensions (PathfindingGrid, SortingArray)

### **Storyboard Actions Conflicts**
**Current Doc Shows:**
```
| `show_widgets` | QueueWidget, HUDWidget, LegendWidget | BFS intro |
| `play_events` | GridWidget, QueueWidget | Node expansions |
| `show_complexity` | HUDWidget | Show O(n) |
```

**Conflicts:**
- Assumes specific widget types exist
- Uses algorithm-specific actions (`show_complexity`)
- No scene configuration system

---

## **2. ALGOViz_Design_Director.md - MODERATE CONFLICTS**

### **Action Resolution Conflicts**
**Current Doc Says:**
```python
handler = self.registry.resolve_action(beat.action)  # ❌ CONFLICT
```

**Widget Architecture v2.0 Says:**
- Actions should be resolved through scene configurations
- Director should use SceneEngine for event routing
- Algorithm-specific actions should not be in Director core

### **Event Playback Conflicts**
**Current Doc Says:**
```python
# Director looks up routing map (dict EventType -> [handler_names])
# For each event, call handlers (widgets/grid/HUD)
```

**Widget Architecture v2.0 Says:**
- Event routing should go through SceneEngine
- No direct widget method calls from Director
- Configuration-driven event binding system

---

## **3. ALGOViz_Design_Storyboard_DSL.md - MAJOR CONFLICTS**

### **Actions List Conflicts**
**Current Doc Defines:**
```
| `place_start` | Place start token | optional: pos |     # ❌ Pathfinding-specific
| `place_goal` | Place goal token | optional: pos |      # ❌ Pathfinding-specific  
| `place_obstacles` | Render obstacles | list of cells |   # ❌ Pathfinding-specific
| `show_complexity` | Display complexity text | O-notations | # ❌ Algorithm-specific
| `celebrate_goal` | Confetti/pulse | optional |           # ❌ Goal-seeking specific
```

**Widget Architecture v2.0 Says:**
- These should be handled by scene configurations, not core actions
- Director should only have generic orchestration actions
- Algorithm-specific actions belong in domain packages

---

## **4. ALGOViz_Design_Adapters_VizEvents.md - MODERATE CONFLICTS**

### **Routing Maps Conflicts**
**Current Doc Shows:**
```python
routing_map_bfs = {
    "enqueue": ["queue.highlight_enqueue", "grid.mark_frontier"],  # ❌ BFS-specific methods
    "dequeue": ["queue.highlight_dequeue"],                       # ❌ BFS-specific methods
    "goal_found": ["grid.flash_goal", "hud.show_success"]         # ❌ BFS-specific methods
}
```

**Widget Architecture v2.0 Says:**
- Routing should use generic widget methods
- Event binding should be configuration-driven
- No hard-coded method names in routing maps

---

## **5. ALGOViz_PRD.md - MINOR CONFLICTS**

### **Widget Naming Conflicts**
**Current Doc Says:**
- `QueueView, Grid, HUD, Legend` ❌ (Inconsistent naming, BFS-specific)

**Widget Architecture v2.0 Says:**
- Consistent naming: ArrayWidget, QueueWidget, etc.
- Generic data structure widgets, not algorithm-specific

### **Phase Ordering Conflicts**
**Current Doc Says:**
- Phase 2: Additional Algorithms + Reusable Widgets

**New Implementation Plan Says:**
- Phase 2: Widget Architecture Foundation (no algorithms until framework is clean)
- Phase 3: Additional Algorithms

---

## **6. ALGOViz_Design_Plugin_System.md - MINOR CONFLICTS**

### **Plugin API Conflicts**
**Current Doc Shows:**
```python
registry.register_widget("priority_queue", PriorityQueueWidget)
registry.register_action("celebrate_goal", celebrate_goal_action)  # ❌ Algorithm-specific
```

**Widget Architecture v2.0 Says:**
- Plugin widgets should integrate with scene configuration system
- Algorithm-specific actions should be in scene configs, not global registry

---

## **7. ALGOViz_Design_DI_Strategy.md - MINOR CONFLICTS**

### **Widget Registry Example Conflicts**
**Current Doc Shows:**
```python
reg.register("grid", lambda: GridWidget())      # ❌ Should be generic
reg.register("queue", lambda: QueueWidget())    # ❌ Should specify data structure vs domain
reg.register("legend", lambda: LegendWidget())  # ❌ Algorithm-specific
```

**Widget Architecture v2.0 Says:**
- Should register with full paths: `agloviz.widgets.structures.ArrayWidget`
- Should distinguish between generic and domain-specific widgets
- Should use scene configurations for widget composition

---

## **8. ALGOViz_SDD.md - MINOR CONFLICTS**

### **Package Structure Conflicts**
**Current Doc Shows:**
```
├─ widgets/           # QueueView, StackView, HUD, PathTracer, etc.
```

**Widget Architecture v2.0 Says:**
```
├─ widgets/
│   ├─ primitives/    # Level 1: Pure visual elements
│   ├─ structures/    # Level 2: Data structure abstractions  
│   ├─ layouts/       # Layout engines
│   └─ domains/       # Level 3: Domain-specific extensions
```

---

## **📋 SUMMARY OF CONFLICTS**

### **High Priority Conflicts (Must Update)**
1. **ALGOViz_Design_Widgets_Registry.md** - Complete rewrite needed
2. **ALGOViz_Design_Storyboard_DSL.md** - Actions list needs major revision
3. **ALGOViz_Design_Director.md** - Event routing section needs update

### **Medium Priority Conflicts (Should Update)**
4. **ALGOViz_Design_Adapters_VizEvents.md** - Routing maps examples need revision
5. **ALGOViz_PRD.md** - Phase descriptions and widget naming needs update

### **Low Priority Conflicts (Minor Updates)**
6. **ALGOViz_Design_Plugin_System.md** - Plugin API examples need adjustment
7. **ALGOViz_Design_DI_Strategy.md** - Widget registry examples need update  
8. **ALGOViz_SDD.md** - Package structure needs update

### **No Conflicts Found**
- ALGOViz_Design_Config_System.md ✅
- ALGOViz_Design_TimingConfig.md ✅
- ALGOViz_Design_Voiceover.md ✅
- ALGOViz_Design_Rendering_Export.md ✅
- ALGOViz_Error_Taxonomy.md ✅
- ALGOViz_Vision_Goals.md ✅
- ALGOViz_Scenario_Theme_Merge_Precedence.md ✅

**Total Documents Requiring Updates: 8 out of 16**

The conflicts are significant but manageable - they primarily involve updating examples and removing BFS-specific assumptions from what should be generic components.