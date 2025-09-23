# ALGOViz v2.0 Architecture Cleanup: AI Coder Instructions

## 🎯 **MISSION OVERVIEW**
You are tasked with cleaning up BFS-specific pollution in the ALGOViz codebase and implementing the Widget Architecture v2.0. The goal is to transform the current BFS-polluted implementation into a clean, generic architecture that can support any algorithm type.

## 📋 **CURRENT STATE ANALYSIS**
- **33 Python files** with working CLI, config system, timing, storyboard DSL
- **BFS-specific pollution identified** in `src/agloviz/cli/app.py` 
- **Widget system exists** but needs v2.0 architecture compliance
- **Director exists** but needs purification to only generic actions

---

## 🚀 **PHASE 1: DIRECTOR PURIFICATION (Day 1)**

### **STEP 1.1: Audit Current BFS Pollution (30 minutes)**

**TASK:** Run audit commands and document findings

```bash
# Run these commands and save output
grep -r "place_start\|place_goal\|place_obstacles\|celebrate_goal\|show_complexity" src/
grep -r "highlight_enqueue\|mark_frontier\|flash_goal\|show_success" src/
grep -r "update.*event\|handle_event" src/agloviz/widgets/
```

**EXPECTED FINDINGS:**
- `src/agloviz/cli/app.py` contains BFS-specific actions: `"place_start", "place_goal", "place_obstacles", "show_complexity", "celebrate_goal"`
- Widgets may have `update()` methods that violate v2.0 architecture

### **STEP 1.2: Clean CLI Actions Registry (1 hour)**

**FILE:** `src/agloviz/cli/app.py`

**CURRENT CODE (around line with BFS actions):**
```python
"show_title", "show_grid", "place_start", "place_goal",
"place_obstacles", "show_widgets", "play_events", "trace_path", 
"show_complexity", "celebrate_goal", "outro"
```

**REPLACE WITH:**
```python
"show_title", "show_widgets", "play_events", "outro"
```

**RATIONALE:** Only 4 generic orchestration actions allowed in v2.0 architecture.

### **STEP 1.3: Update Director Core Actions (2 hours)**

**FILE:** `src/agloviz/core/director.py`

**TASK:** Find the action registration section and clean it up.

**SEARCH FOR:** Look for action registration code, likely in `__init__` or a `_register_actions` method.

**REPLACE ANY BFS-SPECIFIC ACTIONS WITH:**
```python
def _register_core_actions(self):
    """Register only generic orchestration actions (v2.0 compliance)."""
    self.core_actions = {
        "show_title": self._action_show_title,
        "show_widgets": self._action_show_widgets,
        "play_events": self._action_play_events,
        "outro": self._action_outro
    }
```

**REMOVE THESE METHODS** if they exist:
- `_action_place_start`
- `_action_place_goal`
- `_action_place_obstacles`
- `_action_celebrate_goal`
- `_action_show_complexity`

### **STEP 1.4: Remove BFS Routing Map (30 minutes)**

**FILE:** `src/agloviz/core/routing.py`

**CURRENT CODE:**
```python
BFS_ROUTING: RoutingMap = {
    "enqueue": ["queue.highlight_enqueue", "grid.mark_frontier"],
    "dequeue": ["queue.highlight_dequeue"],
    "goal_found": ["grid.flash_goal", "hud.show_success"]
}
```

**REPLACE WITH:**
```python
# BFS_ROUTING removed - routing now handled by scene configurations
# Legacy routing maps are deprecated in v2.0 architecture
```

**UPDATE IMPORTS:** Remove `BFS_ROUTING` from `src/agloviz/core/__init__.py`

---

## 🚀 **PHASE 2: SCENE ENGINE IMPLEMENTATION (Day 2)**

### **STEP 2.1: Create SceneEngine Module (3 hours)**

**CREATE FILE:** `src/agloviz/core/scene_engine.py`

**CONTENT:**
```python
"""Scene Engine for Widget Architecture v2.0.

This module provides the SceneEngine that manages widget lifecycle and 
event routing through declarative scene configurations.
"""

from typing import Any, Dict, List
from dataclasses import dataclass, field
from agloviz.core.events import VizEvent
from agloviz.core.errors import RegistryError
import re


@dataclass
class EventBinding:
    """Binds algorithm events to widget actions."""
    widget: str = field(metadata={"description": "Target widget name"})
    action: str = field(metadata={"description": "Widget method to call"})
    params: Dict[str, Any] = field(default_factory=dict)
    order: int = field(default=1, metadata={"description": "Execution order"})
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WidgetSpec:
    """Configuration for widget instantiation."""
    name: str = field(metadata={"description": "Unique widget name"})
    _target_: str = field(metadata={"description": "Widget class path"})
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class SceneConfig:
    """Complete scene configuration for algorithm visualization."""
    widgets: Dict[str, WidgetSpec] = field(default_factory=dict)
    event_bindings: Dict[str, List[EventBinding]] = field(default_factory=dict)
    layout_config: Dict[str, Any] = field(default_factory=dict)


class SceneEngine:
    """Manages widget lifecycle and event routing for v2.0 architecture."""
    
    def __init__(self, scene_config: SceneConfig):
        self.scene_config = scene_config
        self.widgets: Dict[str, Any] = {}
        self._parameter_template_cache: Dict[str, Any] = {}
    
    def initialize_widgets(self) -> None:
        """Instantiate widgets from scene configuration."""
        from agloviz.widgets import component_registry
        
        for widget_name, widget_spec in self.scene_config.widgets.items():
            # For now, use simple class instantiation
            # TODO: Implement hydra-zen instantiation in future
            widget_class_path = widget_spec._target_
            module_path, class_name = widget_class_path.rsplit('.', 1)
            
            # Simple factory-based instantiation
            if widget_name in ["grid", "queue"]:
                widget_instance = component_registry.get_widget(widget_name)
                self.widgets[widget_name] = widget_instance
            else:
                raise RegistryError(
                    category="SceneEngine",
                    context=f"Widget '{widget_name}'",
                    issue="not supported yet",
                    remedy="Use 'grid' or 'queue' for now"
                )
    
    def process_event(self, event: VizEvent, run_time: float, context: dict) -> None:
        """Route event through scene configuration to widgets."""
        bindings = self.scene_config.event_bindings.get(event.type, [])
        
        # Sort by execution order
        bindings.sort(key=lambda b: b.order)
        
        for binding in bindings:
            if binding.widget not in self.widgets:
                continue  # Skip missing widgets
                
            widget = self.widgets[binding.widget]
            resolved_params = self._resolve_parameters(binding.params, {
                "event": event,
                "context": context,
                "run_time": run_time
            })
            
            # Call widget method
            if hasattr(widget, binding.action):
                method = getattr(widget, binding.action)
                method(**resolved_params)
    
    def _resolve_parameters(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter templates using context data."""
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                template_path = value[2:-1]  # Remove ${ and }
                resolved[key] = self._resolve_template_path(template_path, context)
            else:
                resolved[key] = value
        
        return resolved
    
    def _resolve_template_path(self, template_path: str, context: Dict[str, Any]) -> Any:
        """Resolve a template path like 'event.node' to actual value."""
        parts = template_path.split('.')
        current = context
        
        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None  # Template resolution failed
        
        return current
    
    def cleanup_widgets_for_shot(self, shot) -> None:
        """Clean up widgets at end of shot."""
        # TODO: Implement widget cleanup
        pass
        
    def initialize_widgets_for_shot(self, shot) -> None:
        """Initialize widgets at start of shot."""
        # TODO: Implement shot-specific widget initialization
        pass
```

### **STEP 2.2: Update Director to Use SceneEngine (2 hours)**

**FILE:** `src/agloviz/core/director.py`

**ADD IMPORTS:**
```python
from agloviz.core.scene_engine import SceneEngine, SceneConfig
```

**MODIFY `__init__` METHOD:**
```python
def __init__(
    self,
    scene: Any,
    storyboard: Storyboard,
    timing: TimingConfig,
    scene_config: SceneConfig,  # NEW PARAMETER
    **kwargs
):
    self.scene = scene
    self.storyboard = storyboard
    self.timing = timing
    self.scene_engine = SceneEngine(scene_config)  # NEW
    
    # ... rest of existing code
    
    # Replace old action registration with clean v2.0 actions
    self._register_core_actions()
```

**MODIFY `_action_play_events` METHOD:**
```python
def _action_play_events(self, scene: Any, args: dict[str, Any], run_time: float, context: dict[str, Any]) -> None:
    """Play algorithm events through scene configuration routing."""
    # Get algorithm from context or args
    algorithm_name = args.get('algorithm', context.get('algorithm', 'bfs'))
    
    # Get adapter
    adapter = self.adapter_registry.get_algorithm(algorithm_name)
    scenario = context.get('scenario')
    
    if not scenario:
        console.print("[red]No scenario provided for event playback[/red]")
        return
    
    # Initialize widgets through scene engine
    self.scene_engine.initialize_widgets()
    
    # Route events through scene configuration
    for event in adapter.run(scenario):
        event_run_time = self.timing.events_for(mode=self.mode)
        self.scene_engine.process_event(event, event_run_time, context)
```

### **STEP 2.3: Widget Contract Cleanup (2 hours)**

**FILE:** `src/agloviz/widgets/protocol.py`

**REPLACE ENTIRE CONTENT:**
```python
"""Widget protocol for ALGOViz visualizations v2.0.

This module defines the Widget protocol that all visualization components must implement
following the Widget Architecture v2.0 specifications.
"""

from typing import Protocol, Any


class PrimitiveWidget(Protocol):
    """Protocol for Level 1 primitive widgets (v2.0)."""
    
    def show(self, scene: Any, **kwargs) -> None:
        """Initialize and render widget."""
        ...
        
    def hide(self, scene: Any) -> None:
        """Clean teardown and removal."""
        ...
    
    # NO update() method - no event handling in v2.0


class DataStructureWidget(Protocol):
    """Protocol for Level 2 data structure widgets (v2.0)."""
    
    def add_element(self, element: Any, **kwargs) -> None:
        """Add element to data structure."""
        ...
        
    def remove_element(self, identifier: Any = None, **kwargs) -> None:
        """Remove element from data structure."""
        ...
        
    def highlight_element(self, identifier: Any, style: str, **kwargs) -> None:
        """Highlight specific element."""
        ...
    
    def show(self, scene: Any, **kwargs) -> None:
        """Initialize and render widget."""
        ...
        
    def hide(self, scene: Any) -> None:
        """Clean teardown and removal."""
        ...
    
    # NO event handling - pure visual operations only


class DomainWidget(Protocol):
    """Protocol for Level 3 domain-specific widgets (v2.0)."""
    # Inherits from appropriate Level 2 protocol
    # Adds domain-specific semantic methods
    # Still NO event handling - pure visual operations only
    pass


# Legacy Widget protocol for backwards compatibility
# TODO: Remove after migration complete
Widget = DataStructureWidget
```

**FILES:** `src/agloviz/widgets/grid.py` and `src/agloviz/widgets/queue.py`

**TASK:** Remove any `update()` methods and replace with v2.0 compliant methods.

**IN `src/agloviz/widgets/grid.py`:**
- **REMOVE:** `def update(self, scene, event: VizEvent, run_time: float):`
- **ENSURE EXISTS:** `def highlight_element(self, identifier: Any, style: str, **kwargs):`

**IN `src/agloviz/widgets/queue.py`:**
- **REMOVE:** `def update(self, scene, event: VizEvent, run_time: float):`
- **ENSURE EXISTS:** `def add_element(self, element: Any, **kwargs):` (for enqueue)
- **ENSURE EXISTS:** `def remove_element(self, identifier: Any = None, **kwargs):` (for dequeue)

---

## 🚀 **PHASE 3: SCENE CONFIGURATION IMPLEMENTATION (Day 3)**

### **STEP 3.1: Create BFS Scene Configuration (2 hours)**

**CREATE FILE:** `src/agloviz/scenes/__init__.py`
```python
"""Scene configurations for algorithm visualizations."""
```

**CREATE FILE:** `src/agloviz/scenes/bfs_scene.py`

**CONTENT:**
```python
"""BFS algorithm scene configuration for v2.0 architecture."""

from agloviz.core.scene_engine import SceneConfig, EventBinding, WidgetSpec


class BFSSceneConfig:
    """Scene configuration for Breadth-First Search algorithm."""
    
    @staticmethod
    def create() -> SceneConfig:
        """Create BFS scene configuration with proper event bindings."""
        return SceneConfig(
            widgets={
                "grid": WidgetSpec(
                    name="grid",
                    _target_="agloviz.widgets.grid.GridWidget",
                    params={}
                ),
                "queue": WidgetSpec(
                    name="queue", 
                    _target_="agloviz.widgets.queue.QueueWidget",
                    params={}
                )
            },
            event_bindings={
                "enqueue": [
                    EventBinding(
                        widget="queue",
                        action="add_element", 
                        params={"element": "${event.node}"},
                        order=1
                    ),
                    EventBinding(
                        widget="grid",
                        action="highlight_element",
                        params={
                            "identifier": "${event.node}",
                            "style": "frontier"
                        },
                        order=2
                    )
                ],
                "dequeue": [
                    EventBinding(
                        widget="queue",
                        action="remove_element",
                        params={},
                        order=1
                    )
                ],
                "goal_found": [
                    EventBinding(
                        widget="grid",
                        action="highlight_element",
                        params={
                            "identifier": "${event.node}",
                            "style": "goal"
                        },
                        order=1
                    )
                ]
            },
            layout_config={
                "grid_position": "center",
                "queue_position": "bottom"
            }
        )


# Factory function for easy access
def create_bfs_scene_config() -> SceneConfig:
    """Factory function to create BFS scene configuration."""
    return BFSSceneConfig.create()
```

### **STEP 3.2: Update CLI to Use Scene Configuration (1.5 hours)**

**FILE:** `src/agloviz/cli/render.py`

**ADD IMPORTS:**
```python
from agloviz.scenes.bfs_scene import create_bfs_scene_config
```

**MODIFY `render_with_director` FUNCTION:**
```python
def render_with_director(
    algorithm: str,
    scenario_path: Path,
    storyboard_path: Path | None = None,
    timing_mode: str = "normal",
    with_voiceover: bool = False
) -> None:
    """Render algorithm visualization using Director with scene configuration."""
    
    # Create scene configuration based on algorithm
    if algorithm.lower() == "bfs":
        scene_config = create_bfs_scene_config()
    else:
        raise ValueError(f"Algorithm '{algorithm}' not supported yet")
    
    # ... rest of existing code ...
    
    # Create director with scene configuration
    director = Director(
        scene=None,  # Will be created by Director
        storyboard=storyboard,
        timing=timing_config,
        scene_config=scene_config,  # NEW PARAMETER
        mode=timing_mode,
        with_voice=with_voiceover
    )
```

### **STEP 3.3: Test Integration (1 hour)**

**CREATE TEST FILE:** `test_v2_integration.py`

**CONTENT:**
```python
"""Integration test for v2.0 architecture cleanup."""

from agloviz.core.scene_engine import SceneEngine
from agloviz.scenes.bfs_scene import create_bfs_scene_config
from agloviz.core.events import VizEvent


def test_scene_engine_basic():
    """Test basic scene engine functionality."""
    scene_config = create_bfs_scene_config()
    scene_engine = SceneEngine(scene_config)
    
    # Test widget initialization
    scene_engine.initialize_widgets()
    assert "grid" in scene_engine.widgets
    assert "queue" in scene_engine.widgets
    
    # Test event processing
    event = VizEvent(type="enqueue", payload={"node": (0, 0)}, step_index=1)
    scene_engine.process_event(event, 1.0, {})
    
    print("✅ Scene engine basic test passed")


def test_parameter_template_resolution():
    """Test parameter template resolution."""
    scene_config = create_bfs_scene_config()
    scene_engine = SceneEngine(scene_config)
    
    # Test template resolution
    params = {"identifier": "${event.node}", "style": "frontier"}
    event = VizEvent(type="enqueue", payload={"node": (2, 3)}, step_index=1)
    context = {"event": event}
    
    resolved = scene_engine._resolve_parameters(params, context)
    assert resolved["identifier"] == (2, 3)
    assert resolved["style"] == "frontier"
    
    print("✅ Parameter template resolution test passed")


if __name__ == "__main__":
    test_scene_engine_basic()
    test_parameter_template_resolution()
    print("🎉 All v2.0 integration tests passed!")
```

**RUN TEST:**
```bash
python test_v2_integration.py
```

---

## 🧪 **PHASE 4: VALIDATION & TESTING (Day 3 - Final Hours)**

### **STEP 4.1: Pollution Audit (30 minutes)**

**RUN VALIDATION COMMANDS:**
```bash
# 1. Check for remaining algorithm-specific pollution
echo "=== Checking for algorithm-specific actions ==="
grep -r "place_start\|place_goal\|place_obstacles\|celebrate_goal\|show_complexity" src/ || echo "✅ No algorithm pollution found!"

# 2. Check for widget event handling violations  
echo "=== Checking for widget event handling violations ==="
grep -r "def update.*event\|handle_event\|process_event" src/agloviz/widgets/ || echo "✅ No widget violations found!"

# 3. Check for BFS-specific widget methods
echo "=== Checking for BFS-specific widget methods ==="
grep -r "highlight_enqueue\|mark_frontier\|flash_goal\|show_success" src/ || echo "✅ No BFS-specific methods found!"

# 4. Verify Director only has 4 core actions
echo "=== Checking Director core actions ==="
grep -A 10 "core_actions.*{" src/agloviz/core/director.py
```

### **STEP 4.2: CLI Functionality Test (30 minutes)**

**TEST COMMANDS:**
```bash
# Test basic CLI commands still work
agloviz --help
agloviz config-validate
agloviz list-algorithms

# Test render command (may fail but should not crash)
agloviz render --algo bfs --scenario demo.yaml --mode draft || echo "Render test completed (expected to fail until full implementation)"
```

### **STEP 4.3: Architecture Compliance Check (30 minutes)**

**CREATE VALIDATION SCRIPT:** `validate_v2_architecture.py`

**CONTENT:**
```python
"""Validate v2.0 architecture compliance."""

import ast
import os
from pathlib import Path


def check_director_purity():
    """Check that Director only has 4 generic actions."""
    director_file = Path("src/agloviz/core/director.py")
    if not director_file.exists():
        print("❌ Director file not found")
        return False
    
    content = director_file.read_text()
    
    # Check for forbidden actions
    forbidden_actions = ["place_start", "place_goal", "place_obstacles", "celebrate_goal", "show_complexity"]
    for action in forbidden_actions:
        if action in content:
            print(f"❌ Found forbidden action '{action}' in Director")
            return False
    
    print("✅ Director purity check passed")
    return True


def check_widget_contracts():
    """Check that widgets don't have update() methods."""
    widgets_dir = Path("src/agloviz/widgets")
    if not widgets_dir.exists():
        print("❌ Widgets directory not found")
        return False
    
    for widget_file in widgets_dir.glob("*.py"):
        if widget_file.name in ["__init__.py", "protocol.py"]:
            continue
            
        content = widget_file.read_text()
        if "def update(" in content and "event" in content:
            print(f"❌ Found update() method in {widget_file}")
            return False
    
    print("✅ Widget contract check passed")
    return True


def check_scene_engine_exists():
    """Check that SceneEngine is implemented."""
    scene_engine_file = Path("src/agloviz/core/scene_engine.py")
    if not scene_engine_file.exists():
        print("❌ SceneEngine not implemented")
        return False
    
    content = scene_engine_file.read_text()
    required_classes = ["SceneEngine", "SceneConfig", "EventBinding"]
    for cls in required_classes:
        if f"class {cls}" not in content:
            print(f"❌ Missing class {cls} in SceneEngine")
            return False
    
    print("✅ SceneEngine implementation check passed")
    return True


def main():
    """Run all architecture compliance checks."""
    print("🔍 Running v2.0 Architecture Compliance Validation...")
    print("=" * 50)
    
    checks = [
        check_director_purity,
        check_widget_contracts, 
        check_scene_engine_exists
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 ALL ARCHITECTURE COMPLIANCE CHECKS PASSED!")
        print("✅ Ready for Phase 2 implementation")
    else:
        print("❌ Some checks failed - review and fix issues")
    
    return all_passed


if __name__ == "__main__":
    main()
```

**RUN VALIDATION:**
```bash
python validate_v2_architecture.py
```

---

## 🎯 **SUCCESS CRITERIA CHECKLIST**

After completing all phases, verify these criteria:

### **✅ Director Purification**
- [ ] Only 4 core actions: `show_title`, `show_widgets`, `play_events`, `outro`
- [ ] No algorithm-specific actions in Director
- [ ] SceneEngine integration implemented
- [ ] `_action_play_events` routes through SceneEngine

### **✅ Widget Architecture v2.0 Compliance**
- [ ] No `update()` methods in widget classes
- [ ] Widgets have pure visual operations only
- [ ] `highlight_element`, `add_element`, `remove_element` methods exist
- [ ] Widget protocol updated for v2.0

### **✅ Scene Configuration System**
- [ ] SceneEngine class implemented
- [ ] EventBinding and SceneConfig classes created
- [ ] Parameter template resolution working
- [ ] BFS scene configuration created

### **✅ Integration & Testing**
- [ ] CLI commands still functional
- [ ] No algorithm-specific pollution found in audit
- [ ] Architecture compliance validation passes
- [ ] Basic integration test passes

---

## 🚀 **POST-CLEANUP STATUS**

After completing this cleanup, you will have:

1. **Clean v2.0 Architecture Foundation** - No algorithm pollution
2. **Working BFS Implementation** - Using proper scene configuration
3. **Extensible Framework** - Ready for new algorithms without core changes
4. **Plugin-Ready System** - Scene configurations as extension points

## 📚 **REFERENCE DOCUMENTS**

- `planning/v2/ALGOViz_Design_Director_v2.md` - Director v2.0 specification
- `planning/v2/ALGOViz_Design_Widgets_Registry_v2.md` - Widget Architecture v2.0
- `planning/v2/ALGOViz_Design_Storyboard_DSL_v2.md` - Generic storyboard actions
- `planning/rewrite_plan/output/final_analysis.md` - Architecture validation report

---

**🎯 EXECUTION NOTE:** Follow this plan step-by-step. Each phase builds on the previous one. Test frequently and ensure CLI commands remain functional throughout the process.
