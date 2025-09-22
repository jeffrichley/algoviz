# ALGOViz Next Steps: Architecture Cleanup Plan 🚀

## 🎯 **Current Status**
- ✅ **Phase 0 & 1.1-1.4 COMPLETED** - You have a working foundation (33 Python files)
- ✅ **v2.0 Architecture Documentation COMPLETE** - Perfect architectural specifications
- ⚠️ **Architecture Cleanup Needed** - Remove BFS-specific pollution from existing code

## 🛠️ **Immediate Action Plan (2-3 days)**

### **Day 1: Assessment & Director Cleanup**

#### **Step 1.1: Audit Current Code (2 hours)**
```bash
# Find BFS-specific pollution in your current code
grep -r "place_start\|place_goal\|place_obstacles\|celebrate_goal" src/
grep -r "highlight_enqueue\|mark_frontier\|flash_goal" src/
grep -r "update.*event\|handle_event" src/agloviz/widgets/
```

#### **Step 1.2: Clean Director Actions (4 hours)**
**File: `src/agloviz/core/director.py`**

**BEFORE (Current - BFS Polluted):**
```python
# Probably has BFS-specific actions
self.actions = {
    "show_title": ...,
    "place_start": ...,     # ❌ REMOVE
    "place_goal": ...,      # ❌ REMOVE  
    "play_events": ...,
    # ... other BFS-specific actions
}
```

**AFTER (v2.0 - Clean):**
```python
# Only 4 generic orchestration actions
self.core_actions = {
    "show_title": self._action_show_title,
    "show_widgets": self._action_show_widgets,
    "play_events": self._action_play_events,
    "outro": self._action_outro
}
```

### **Day 2: SceneEngine & Widget Cleanup**

#### **Step 2.1: Create SceneEngine (4 hours)**
**File: `src/agloviz/core/scene_engine.py` (NEW)**

```python
from typing import Any, Dict, List
from dataclasses import dataclass
from agloviz.core.events import VizEvent

@dataclass
class EventBinding:
    widget: str
    action: str
    params: Dict[str, Any]
    order: int = 1

@dataclass 
class SceneConfig:
    widgets: Dict[str, Any]
    event_bindings: Dict[str, List[EventBinding]]

class SceneEngine:
    def __init__(self, scene_config: SceneConfig):
        self.scene_config = scene_config
        self.widgets = {}
    
    def process_event(self, event: VizEvent, run_time: float, context: dict):
        """Route event through scene configuration."""
        bindings = self.scene_config.event_bindings.get(event.type, [])
        for binding in sorted(bindings, key=lambda b: b.order):
            widget = self.widgets[binding.widget]
            resolved_params = self._resolve_params(binding.params, event, context)
            method = getattr(widget, binding.action)
            method(**resolved_params)
```

#### **Step 2.2: Clean Widget Contracts (4 hours)**
**Files: `src/agloviz/widgets/*.py`**

**Remove any `update()` methods from widgets:**
```python
# ❌ REMOVE from widgets
def update(self, scene, event: VizEvent, run_time: float):
    # This violates v2.0 architecture

# ✅ KEEP only pure visual operations  
def highlight_element(self, index: int, style: str, **kwargs):
    # Pure visual operation - GOOD
```

### **Day 3: Scene Configuration & Integration**

#### **Step 3.1: Create BFS Scene Configuration (3 hours)**
**File: `src/agloviz/scenes/bfs_scene.py` (NEW)**

```python
from agloviz.core.scene_engine import SceneConfig, EventBinding

class BFSSceneConfig:
    @staticmethod
    def create() -> SceneConfig:
        return SceneConfig(
            widgets={
                "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
                "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
            },
            event_bindings={
                "enqueue": [
                    EventBinding(widget="queue", action="add_element", 
                               params={"element": "${event.node}"}, order=1),
                    EventBinding(widget="grid", action="highlight_element", 
                               params={"index": "${event.pos}", "style": "frontier"}, order=2)
                ],
                "dequeue": [
                    EventBinding(widget="queue", action="remove_element", params={})
                ]
            }
        )
```

#### **Step 3.2: Update Director Integration (2 hours)**
**File: `src/agloviz/core/director.py`**

```python
# Add SceneEngine to Director
class Director:
    def __init__(self, scene, storyboard, timing, scene_config, **kwargs):
        self.scene_engine = SceneEngine(scene_config)  # NEW
        # ... existing code
    
    def _action_play_events(self, scene, args, run_time, context):
        """Route events through SceneEngine instead of direct widget calls."""
        adapter = self.adapter_registry.get_algorithm(context['algorithm'])
        for event in adapter.run(context['scenario']):
            self.scene_engine.process_event(event, run_time, context)  # NEW
```

#### **Step 3.3: Test Integration (2 hours)**
```bash
# Test that your refactored code works
agloviz render --algo bfs --scenario demo.yaml --mode fast
```

## 🧪 **Testing Your Changes**

### **Validation Commands**
```bash
# 1. Check for remaining pollution
grep -r "place_start\|place_goal" src/ || echo "✅ Director cleaned!"

# 2. Check widget contracts
grep -r "def update.*event" src/agloviz/widgets/ || echo "✅ Widgets cleaned!"

# 3. Test CLI still works  
agloviz config-validate
agloviz list-algorithms

# 4. Test render (may need scene config integration)
agloviz render --algo bfs --scenario demo.yaml --mode draft
```

## 🎯 **Success Criteria**

After 2-3 days, you should have:
- ✅ **Director with only 4 generic actions**
- ✅ **SceneEngine handling event routing** 
- ✅ **Widgets with pure visual operations only**
- ✅ **BFS scene configuration working**
- ✅ **CLI commands still functional**

## 🚀 **After Cleanup: You're Ready for Phase 2!**

Once you complete this cleanup, you'll have:
- **Clean v2.0 architecture foundation**
- **Working BFS implementation** using proper architecture
- **Ready to add new algorithms** without touching core code
- **Plugin-ready system** for extensions

## 🆘 **If You Get Stuck**

1. **Focus on one file at a time** - Don't try to change everything at once
2. **Keep your current tests running** - Make sure CLI commands still work
3. **Reference the v2.0 docs** - Use `planning/v2/` documents as your guide
4. **Start with Director cleanup** - This is the most important change

## 📚 **Key Reference Documents**
- `planning/v2/ALGOViz_Design_Director_v2.md` - Pure orchestrator pattern
- `planning/v2/ALGOViz_Design_Widgets_Registry_v2.md` - Widget contracts and hierarchy
- `planning/rewrite_plan/output/final_analysis.md` - What needs to be cleaned up

---

**🎯 You've got this! The architecture is solid, you just need to clean up the implementation to match it.**
