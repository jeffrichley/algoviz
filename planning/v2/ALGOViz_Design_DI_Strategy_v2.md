# ALGOViz Design Doc — Dependency Injection (DI) Strategy v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0 - Hydra-zen First)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Updated for Hydra-zen First Philosophy & Widget Architecture v2.0)
**Supersedes:** planning/v1/ALGOViz_Design_DI_Strategy.md

---

> This document specifies **how ALGOViz constructs and wires objects** (adapters, director, widgets, voiceover engines, pipelines) using **hydra-zen first dependency injection** built on **Hydra + hydra‑zen + OmegaConf**. It follows the **hydra-zen first philosophy** established in the Configuration System and provides comprehensive patterns for structured config-driven object construction.

---

## 1. Problem Statement & Goals

**Problem.** ALGOViz is highly modular (Storyboard DSL, Director, Adapters, Widgets, Voiceover, Rendering). Without a disciplined construction pattern, we risk:
- Hard-coded dependencies (tight coupling)
- Brittle test setups
- Unclear swap points (e.g., voiceover backend, renderer engine)
- Configuration sprawl and inconsistent overrides

**Goal.** Provide a **hydra-zen first DI approach** that:
1. **Instantiates** objects from structured configs via `builds()` and `instantiate()`.
2. **Wires** nested dependencies using hydra-zen composition patterns.
3. **Swaps** implementations via ConfigStore groups and CLI overrides.
4. **Scopes** object lifetimes (singleton vs per-run vs per-act/per-shot).
5. **Validates** structured configs → objects with clear errors.
6. **Works with plugins** and matches our testing + CI needs.

**Non-Goals.**
- Full enterprise DI container with AOP, interceptors, or reflection-based injection.
- Runtime mutation of the graph beyond documented scopes.

---

## 2. Technology Choices (Hydra-zen First)

- **hydra‑zen**: **PRIMARY** - ergonomic structured configs using `builds()`, `make_config()`, and `instantiate()` for type-safe object construction.
- **Hydra**: config composition, CLI overrides, and **instantiation** (`hydra.utils.instantiate` via hydra-zen).
- **ConfigStore**: centralized registration of structured config templates with groups and inheritance.
- **OmegaConf**: hierarchical config resolution, deep merge from multiple YAMLs + CLI overrides.
- **Pydantic** (v1 or v2): **final validation** of instantiated objects (schema + cross-field checks).

> **Design stance**: **Create structured configs with hydra-zen → Register with ConfigStore → Compose with Hydra → Instantiate with hydra-zen → Validate with Pydantic**

---

## 3. Object Graph Overview (Hydra-zen Flow)

The "canonical" graph (top-level run) showing hydra-zen instantiation flow:

```
ConfigStore Templates
├─ VideoConfigZen (main config template)
├─ DirectorConfigZen (per-run template)
├─ VoiceoverConfigZen (engine templates)
├─ RegistryConfigZen (singleton template)
└─ SceneConfigZen (scene templates)
           ↓ hydra-zen instantiate()
VideoRun (ephemeral)
└─ Director (per-run, instantiated from DirectorConfigZen)
   ├─ Storyboard (immutable; instantiated from StoryboardConfigZen)
   ├─ TimingConfig (immutable; validated Pydantic model)
   ├─ VoiceoverEngine (optional; instantiated from VoiceoverConfigZen)
   ├─ ComponentRegistry (singleton; instantiated from RegistryConfigZen)
   ├─ AlgorithmAdapter (per-run, instantiated from AdapterConfigZen)
   ├─ RenderPipeline (per-run, instantiated from RenderConfigZen)
   │  ├─ FrameRenderer (per-run, builds() template)
   │  ├─ Encoder (per-run, builds() template)
   │  ├─ SubtitleExporter (per-run, builds() template)
   │  └─ MetadataExporter (per-run, builds() template)
   ├─ ScenarioRuntime (per-run; instantiated from ScenarioConfigZen)
   └─ SceneEngine (per-run; manages widget instantiation)
      └─ Widgets (per-shot; instantiated from widget structured configs)
```

**Scopes.**
- **Singleton** (process): `ComponentRegistry` registrations, PluginManager, ConfigStore templates.
- **Per‑run**: Director, Adapter, VoiceoverEngine, RenderPipeline, SceneEngine.
- **Per‑shot**: transient widget instances, temporary scene contexts.

---

## 4. Hydra-zen Structured Config Patterns

### 4.1 Core Component Structured Configs

```python
# di/core_configs.py
from hydra_zen import builds, make_config
from hydra.core.config_store import ConfigStore
from agloviz.core.director import Director
from agloviz.voice.coqui import CoquiTTS
from agloviz.core.registry import ComponentRegistry
from agloviz.adapters.bfs import BFSAdapter

# Create structured configs using builds()
DirectorConfigZen = builds(
    Director,
    storyboard="${storyboard}",
    timing="${timing}",
    registry="${registry}",
    voiceover="${voiceover}",
    mode="${timing.mode}",
    with_voice="${voiceover.enabled:false}",
    zen_partial=True,
    populate_full_signature=True
)

VoiceoverConfigZen = builds(
    CoquiTTS,
    enabled="${voiceover.enabled:false}",
    lang="${voiceover.lang:en}",
    voice="${voiceover.voice:en_US}",
    speed="${voiceover.speed:1.0}",
    zen_partial=True,
    populate_full_signature=True
)

RegistryConfigZen = builds(
    ComponentRegistry,
    plugins="${plugins}",
    widget_factories="${widget_factories:[]}",
    zen_partial=True,
    populate_full_signature=True
)

BFSAdapterConfigZen = builds(
    BFSAdapter,
    scenario="${scenario}",
    grid_data="${grid_data}",
    start_pos="${scenario.start}",
    goal_pos="${scenario.goal}",
    zen_partial=True,
    populate_full_signature=True
)

# Main run configuration using composition
RunConfigZen = make_config(
    director=DirectorConfigZen,
    storyboard="${storyboard}",
    timing="${timing}",
    voiceover=VoiceoverConfigZen,
    registry=RegistryConfigZen,
    adapter=BFSAdapterConfigZen,
    hydra_defaults=["_self_"]
)
```

### 4.2 ConfigStore Registration

```python
def register_di_configs():
    """Register all DI structured configs with ConfigStore"""
    cs = ConfigStore.instance()
    
    # Core component configs
    cs.store(name="director_base", node=DirectorConfigZen)
    cs.store(name="registry_base", node=RegistryConfigZen)
    cs.store(name="run_base", node=RunConfigZen)
    
    # Voiceover engine configs by group
    cs.store(group="voiceover", name="coqui", node=builds(
        CoquiTTS,
        enabled=True,
        lang="en",
        voice="en_US",
        speed=1.0,
        zen_partial=True
    ))
    
    cs.store(group="voiceover", name="disabled", node=builds(
        CoquiTTS,
        enabled=False,
        zen_partial=True
    ))
    
    # Adapter configs by algorithm
    cs.store(group="adapter", name="bfs", node=BFSAdapterConfigZen)
    cs.store(group="adapter", name="dfs", node=builds(
        "agloviz.adapters.dfs.DFSAdapter",
        scenario="${scenario}",
        zen_partial=True
    ))
    
    # Render pipeline configs
    cs.store(group="render", name="standard", node=builds(
        "agloviz.core.render.RenderPipeline",
        config="${render}",
        zen_partial=True
    ))
```

### 4.3 Hydra Configuration Files

```yaml
# config/run.yaml
# @package _global_
defaults:
  - scenario: maze_small
  - timing: normal
  - voiceover: disabled
  - adapter: bfs
  - render: standard
  - _self_

# Main run config uses structured config template
_target_: agloviz.di.core_configs.RunConfigZen

# Override specific parameters
director:
  mode: "${timing.mode}"
  
voiceover:
  enabled: false

timing:
  mode: "normal"
```

### 4.4 CLI Overrides (Hydra-zen Native)

```bash
# Switch voiceover engine and parameters
agloviz render scenario=maze_large voiceover=coqui voiceover.voice=en_US_male_1 voiceover.speed=0.95

# Change adapter algorithm
agloviz render scenario=maze_small adapter=dfs timing=fast

# Override nested parameters
agloviz render scenario.start=[1,1] timing.ui=1.5 render.quality=high
```

---

## 5. Widget System DI Integration (Enhanced)

### 5.1 Widget Structured Configs

```python
# widgets/configs.py
from hydra_zen import builds, make_config
from agloviz.widgets.grid import GridWidget
from agloviz.widgets.queue import QueueWidget
from agloviz.widgets.legend import LegendWidget

# Widget structured configs using builds()
GridWidgetConfigZen = builds(
    GridWidget,
    width="${grid.width:20}",
    height="${grid.height:15}",
    cell_size="${grid.cell_size:0.5}",
    show_coordinates="${grid.show_coordinates:true}",
    theme="${theme}",
    zen_partial=True,
    populate_full_signature=True
)

QueueWidgetConfigZen = builds(
    QueueWidget,
    max_visible="${queue.max_visible:10}",
    orientation="${queue.orientation:horizontal}",
    show_indices="${queue.show_indices:true}",
    theme="${theme}",
    zen_partial=True,
    populate_full_signature=True
)

LegendWidgetConfigZen = builds(
    LegendWidget,
    position="${legend.position:top_right}",
    items="${legend.items:[]}",
    theme="${theme}",
    zen_partial=True,
    populate_full_signature=True
)

# Scene configuration using widget composition
BFSSceneConfigZen = make_config(
    name="bfs_pathfinding",
    algorithm="bfs",
    widgets={
        "grid": GridWidgetConfigZen,
        "queue": QueueWidgetConfigZen,
        "legend": LegendWidgetConfigZen
    },
    event_bindings={
        "enqueue": [
            builds("agloviz.core.events.EventBinding", 
                  widget="queue", 
                  action="add_element", 
                  params={"element": "${event.node}"},
                  order=1),
            builds("agloviz.core.events.EventBinding",
                  widget="grid",
                  action="highlight_cell",
                  params={"pos": "${event.pos}", "style": "frontier"},
                  order=2)
        ],
        "dequeue": [
            builds("agloviz.core.events.EventBinding",
                  widget="queue",
                  action="remove_element",
                  params={"index": 0},
                  order=1),
            builds("agloviz.core.events.EventBinding",
                  widget="grid", 
                  action="highlight_cell",
                  params={"pos": "${event.pos}", "style": "current"},
                  order=2)
        ]
    },
    hydra_defaults=["_self_"]
)
```

### 5.2 Widget Registry with Hydra-zen

```python
# core/registry.py
from hydra_zen import instantiate
from hydra.core.config_store import ConfigStore

class ComponentRegistry:
    def __init__(self, plugins=None, widget_factories=None):
        self.widget_factories = {}
        self.scene_configs = {}
        self._setup_core_widgets()
        if plugins:
            self._register_plugin_widgets(plugins)
    
    def _setup_core_widgets(self):
        """Register core widget structured configs"""
        cs = ConfigStore.instance()
        
        # Register widget configs in ConfigStore
        cs.store(group="widget", name="grid", node=GridWidgetConfigZen)
        cs.store(group="widget", name="queue", node=QueueWidgetConfigZen)
        cs.store(group="widget", name="legend", node=LegendWidgetConfigZen)
        
        # Register scene configs
        cs.store(group="scene", name="bfs_pathfinding", node=BFSSceneConfigZen)
        cs.store(group="scene", name="dfs_pathfinding", node=builds(
            BFSSceneConfigZen,  # Inherit from BFS scene
            name="dfs_pathfinding",
            algorithm="dfs",
            zen_partial=True
        ))
    
    def create_widget(self, widget_name: str, widget_config) -> Any:
        """Create widget instance using hydra-zen instantiation"""
        if hasattr(widget_config, '_target_'):
            # Structured config - use instantiate()
            return instantiate(widget_config)
        else:
            # Legacy factory pattern (for backward compatibility)
            factory = self.widget_factories.get(widget_name)
            if factory:
                return factory(widget_config)
            raise ValueError(f"No widget factory for {widget_name}")
    
    def get_scene_config(self, scene_name: str):
        """Retrieve scene configuration from ConfigStore"""
        cs = ConfigStore.instance()
        repo = cs.get_repo()
        scene_key = f"scene/{scene_name}"
        if scene_key in repo:
            return repo[scene_key].node
        raise ValueError(f"No scene config for {scene_name}")
```

### 5.3 Scene Engine with Hydra-zen Integration

```python
# core/scene_engine.py
from hydra_zen import instantiate
from omegaconf import OmegaConf, DictConfig
from typing import Dict, Any

class SceneEngine:
    def __init__(self, scene_config: DictConfig, registry: ComponentRegistry, timing_config):
        self.scene_config = scene_config
        self.registry = registry
        self.timing_config = timing_config
        self.widgets: Dict[str, Any] = {}
        self.event_bindings: Dict[str, list] = {}
    
    def initialize_scene(self) -> None:
        """Initialize scene using hydra-zen instantiation"""
        # Instantiate scene configuration if needed
        if hasattr(self.scene_config, '_target_'):
            scene_data = instantiate(self.scene_config)
        else:
            scene_data = self.scene_config
        
        # Initialize widgets using structured configs
        self._initialize_widgets(scene_data.widgets)
        
        # Setup event bindings with parameter resolution
        self._setup_event_bindings(scene_data.event_bindings)
    
    def _initialize_widgets(self, widget_specs: Dict[str, Any]) -> None:
        """Initialize widgets from structured configs"""
        for widget_name, widget_spec in widget_specs.items():
            try:
                # Use registry to create widget (handles both structured configs and factories)
                widget_instance = self.registry.create_widget(widget_name, widget_spec)
                self.widgets[widget_name] = widget_instance
            except Exception as e:
                raise ValueError(f"Failed to initialize widget '{widget_name}': {e}") from e
    
    def _setup_event_bindings(self, binding_specs: Dict[str, list]) -> None:
        """Setup event bindings with parameter template resolution"""
        for event_name, bindings in binding_specs.items():
            resolved_bindings = []
            for binding_spec in bindings:
                if hasattr(binding_spec, '_target_'):
                    # Structured config - instantiate
                    binding = instantiate(binding_spec)
                else:
                    # Direct binding data
                    binding = binding_spec
                resolved_bindings.append(binding)
            self.event_bindings[event_name] = resolved_bindings
```

---

## 6. Parameter Template Resolution (Hydra-zen Integration)

### 6.1 OmegaConf Resolver Integration

```python
# core/resolvers.py
from omegaconf import OmegaConf
from typing import Any, Dict

def register_custom_resolvers():
    """Register custom OmegaConf resolvers for parameter templates"""
    
    # Event data resolver
    OmegaConf.register_new_resolver(
        "event_data", 
        lambda path, context=None: _resolve_event_path(path, context)
    )
    
    # Configuration resolver
    OmegaConf.register_new_resolver(
        "config_value",
        lambda path, default=None: _resolve_config_path(path, default)
    )
    
    # Timing resolver
    OmegaConf.register_new_resolver(
        "timing_value",
        lambda timing_key, mode="normal": _resolve_timing_value(timing_key, mode)
    )
    
    # Widget state resolver
    OmegaConf.register_new_resolver(
        "widget_state",
        lambda widget_name, state_key: _resolve_widget_state(widget_name, state_key)
    )

def _resolve_event_path(path: str, context: Dict[str, Any]) -> Any:
    """Resolve event data path like 'event.node' or 'event.pos'"""
    if not context or 'event' not in context:
        return None
    
    event_data = context['event']
    keys = path.split('.')
    result = event_data
    
    for key in keys[1:]:  # Skip 'event' prefix
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return None
    
    return result

def _resolve_config_path(path: str, default: Any = None) -> Any:
    """Resolve configuration path like 'config.highlight_style'"""
    # Implementation would access current config context
    # This is a placeholder for the actual implementation
    return default

def _resolve_timing_value(timing_key: str, mode: str = "normal") -> float:
    """Resolve timing values based on current timing mode"""
    timing_multipliers = {
        "draft": 0.5,
        "normal": 1.0, 
        "fast": 0.25
    }
    
    base_timings = {
        "ui": 1.0,
        "events": 0.8,
        "effects": 0.5,
        "waits": 0.5
    }
    
    base_time = base_timings.get(timing_key, 1.0)
    multiplier = timing_multipliers.get(mode, 1.0)
    return base_time * multiplier
```

### 6.2 Enhanced Event Binding with Templates

```yaml
# scene/bfs_pathfinding.yaml
# @package scene
_target_: agloviz.widgets.configs.BFSSceneConfigZen

widgets:
  grid:
    _target_: agloviz.widgets.grid.GridWidget
    width: 20
    height: 15
    cell_size: 0.5
    
  queue:
    _target_: agloviz.widgets.queue.QueueWidget
    max_visible: 10
    orientation: "horizontal"

event_bindings:
  enqueue:
    - _target_: agloviz.core.events.EventBinding
      widget: "queue"
      action: "add_element"
      params:
        element: "${event_data:event.node}"
        style: "${config_value:queue.element_style,default}"
        duration: "${timing_value:events}"
      order: 1
      
    - _target_: agloviz.core.events.EventBinding
      widget: "grid"
      action: "highlight_cell"
      params:
        pos: "${event_data:event.pos}"
        style: "frontier"
        duration: "${timing_value:effects}"
      order: 2
      
  dequeue:
    - _target_: agloviz.core.events.EventBinding
      widget: "queue"
      action: "remove_element"
      params:
        index: 0
        animation_duration: "${timing_value:ui}"
      order: 1
```

### 6.3 Runtime Parameter Resolution

```python
# core/event_processor.py
from hydra_zen import instantiate
from omegaconf import OmegaConf
from typing import Dict, Any

class EventProcessor:
    def __init__(self, scene_engine: SceneEngine):
        self.scene_engine = scene_engine
        self.context = {}
        
        # Register resolvers with access to current context
        self._setup_context_resolvers()
    
    def process_event(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """Process event with parameter template resolution"""
        # Update context with current event data
        self.context.update({
            'event': event_data,
            'config': self.scene_engine.scene_config,
            'timing': self.scene_engine.timing_config,
            'widgets': {name: widget for name, widget in self.scene_engine.widgets.items()}
        })
        
        # Get event bindings
        bindings = self.scene_engine.event_bindings.get(event_name, [])
        
        for binding in bindings:
            # Resolve parameters using current context
            resolved_params = self._resolve_binding_parameters(binding, self.context)
            
            # Execute binding with resolved parameters
            self._execute_binding(binding, resolved_params)
    
    def _resolve_binding_parameters(self, binding, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter templates in binding using context"""
        if not hasattr(binding, 'params'):
            return {}
        
        # Create OmegaConf config with context for resolution
        params_config = OmegaConf.create(binding.params)
        
        # Set resolver context
        OmegaConf.set_resolver("current_context", lambda: context)
        
        # Resolve all interpolations
        resolved_config = OmegaConf.to_container(params_config, resolve=True)
        
        return resolved_config
    
    def _execute_binding(self, binding, resolved_params: Dict[str, Any]) -> None:
        """Execute event binding with resolved parameters"""
        widget = self.scene_engine.widgets.get(binding.widget)
        if widget and hasattr(widget, binding.action):
            action_method = getattr(widget, binding.action)
            action_method(**resolved_params)
        else:
            raise ValueError(f"Widget '{binding.widget}' does not have action '{binding.action}'")
```

---

## 7. Validation Pipeline (Enhanced)

We separate concerns with hydra-zen integration:
1. **ConfigStore + hydra‑zen**: structured config templates and composition.
2. **Hydra + OmegaConf**: load + merge YAML + CLI → `cfg` tree with resolution.
3. **hydra‑zen**: instantiate **objects** per structured configs and `_target_`.
4. **Pydantic**: validate **domain models** after instantiation.

```python
from hydra_zen import instantiate
from pydantic import BaseModel, ValidationError

class ScenarioModel(BaseModel):
    grid_file: str
    start: tuple[int,int]
    goal: tuple[int,int]

def create_scenario_runtime(scenario_config) -> "ScenarioRuntime":
    """Create ScenarioRuntime with validation pipeline"""
    try:
        # Step 1: Instantiate from structured config
        if hasattr(scenario_config, '_target_'):
            scenario_data = instantiate(scenario_config)
        else:
            scenario_data = scenario_config
        
        # Step 2: Validate with Pydantic
        if not isinstance(scenario_data, ScenarioModel):
            model = ScenarioModel(**scenario_data)
        else:
            model = scenario_data
        
        # Step 3: Create runtime object
    return ScenarioRuntime.from_model(model)
        
    except ValidationError as e:
        raise ValueError(f"Scenario validation failed: {e}") from e
    except Exception as e:
        raise ValueError(f"Scenario instantiation failed: {e}") from e
```

---

## 8. Error Handling & Diagnostics (Enhanced)

**Classification & Guidance with Hydra-zen**
- **Structured config error**: Invalid `builds()` configuration or missing parameters.  
  - Message: `Failed to build VoiceoverConfigZen: missing required parameter 'lang'`  
  - Action: check structured config definition and parameter defaults.

- **Instantiation error**: `_target_` import path missing or constructor error.  
  - Message: `Failed to instantiate VoiceoverEngine (agloviz.voice.coqui.CoquiTTS): No module named 'coqui_tts'`  
  - Action: verify dependency, plugin, or import path.

- **ConfigStore error**: Missing config group or template.  
  - Message: `Config 'voiceover/advanced_tts' not found in ConfigStore. Available: ['voiceover/coqui', 'voiceover/disabled']`  
  - Action: check config group name and available templates.

- **Parameter resolution error**: Template interpolation failure.  
  - Message: `Failed to resolve parameter template '${event.invalid_field}' in event binding`  
  - Action: check event data structure and template syntax.

**Enhanced Traceability**
- Include **ConfigStore group/name** context when errors occur.
- Emit **structured config lineage** showing template inheritance.
- Provide **parameter resolution trace** for complex interpolations.

---

## 9. Testing the DI Graph (Enhanced)

### 9.1 Structured Config Testing

```python
# tests/test_di_configs.py
import pytest
from hydra_zen import instantiate
from hydra.core.config_store import ConfigStore
from agloviz.di.core_configs import register_di_configs

def test_director_config_instantiation():
    """Test that DirectorConfigZen instantiates correctly"""
    register_di_configs()
    cs = ConfigStore.instance()
    
    director_config = cs.get_repo()["director_base"].node
    
    # Mock dependencies for testing
    test_config = instantiate(director_config,
                             storyboard=MockStoryboard(),
                             timing=MockTimingConfig(),
                             registry=MockRegistry(),
                             voiceover=None)
    
    assert test_config is not None
    assert hasattr(test_config, 'run')

def test_widget_config_composition():
    """Test that widget configs compose correctly in scenes"""
    scene_config = BFSSceneConfigZen
    
    # Test instantiation with mock parameters
    scene_instance = instantiate(scene_config,
                                grid={"width": 10, "height": 10},
                                queue={"max_visible": 5},
                                theme=MockTheme())
    
    assert "grid" in scene_instance.widgets
    assert "queue" in scene_instance.widgets
    assert len(scene_instance.event_bindings) > 0

def test_parameter_template_resolution():
    """Test that parameter templates resolve correctly"""
    from agloviz.core.resolvers import register_custom_resolvers
    
    register_custom_resolvers()
    
    # Test event data resolution
    context = {"event": {"node": "A", "pos": [1, 2]}}
    
    # This would be tested with actual OmegaConf resolution
    # Placeholder for actual test implementation
    assert True  # Replace with actual assertions
```

### 9.2 Integration Testing

```python
# tests/test_di_integration.py
def test_full_di_pipeline():
    """Test complete DI pipeline from config to object instantiation"""
    from hydra_zen import instantiate
    from omegaconf import OmegaConf
    
    # Load test configuration
    cfg = OmegaConf.create({
        "director": {
            "_target_": "agloviz.core.director.Director",
            "storyboard": {"_target_": "MockStoryboard"},
            "timing": {"_target_": "MockTimingConfig"},
            "registry": {"_target_": "MockRegistry"}
        }
    })
    
    # Test instantiation
    director = instantiate(cfg.director)
    
    assert director is not None
    assert hasattr(director, 'run')
    assert director.timing is not None
    assert director.registry is not None

def test_widget_instantiation_pipeline():
    """Test widget instantiation through scene engine"""
    scene_config = OmegaConf.create({
        "widgets": {
            "grid": {
                "_target_": "agloviz.widgets.grid.GridWidget",
                "width": 10,
                "height": 10
            }
        }
    })
    
    registry = MockRegistry()
    scene_engine = SceneEngine(scene_config, registry, MockTimingConfig())
    
    scene_engine.initialize_scene()
    
    assert "grid" in scene_engine.widgets
    assert scene_engine.widgets["grid"] is not None
```

---

## 10. Widget Registry via DI Factories (Updated for Hydra-zen)

```python
# core/registry.py  
from hydra_zen import instantiate, builds
from hydra.core.config_store import ConfigStore

def build_component_registry(plugins=None, widget_configs=None) -> "ComponentRegistry":
    """Build component registry with hydra-zen structured configs"""
    reg = ComponentRegistry()
    cs = ConfigStore.instance()
    
    # Register core widget structured configs
    cs.store(group="widget", name="grid", node=builds(
        "agloviz.widgets.grid.GridWidget",
        zen_partial=True,
        populate_full_signature=True
    ))
    
    cs.store(group="widget", name="queue", node=builds(
        "agloviz.widgets.queue.QueueWidget", 
        zen_partial=True,
        populate_full_signature=True
    ))
    
    cs.store(group="widget", name="stack", node=builds(
        "agloviz.widgets.stack.StackWidget",
        zen_partial=True,
        populate_full_signature=True
    ))
    
    # Register domain-specific widget configs
    cs.store(group="widget", name="pathfinding_grid", node=builds(
        "agloviz.widgets.pathfinding.PathfindingGrid",
        zen_partial=True,
        populate_full_signature=True
    ))
    
    cs.store(group="widget", name="sorting_array", node=builds(
        "agloviz.widgets.sorting.SortingArray",
        zen_partial=True,
        populate_full_signature=True
    ))
    
    # Register plugin widgets
    if plugins:
        for widget_name, widget_config in plugins.get_widget_configs():
            cs.store(group="widget", name=f"plugin_{widget_name}", node=widget_config)
    
    return reg
```

---

## 11. Example: Two Swappable Voiceover Engines (Hydra-zen)

### 11.1 Structured Config Definitions

```python
# voice/configs.py
from hydra_zen import builds

CoquiTTSConfig = builds(
    "agloviz.voice.coqui.CoquiTTS",
    enabled=True,
    lang="en",
    voice="en_US",
    speed=1.0,
    zen_partial=True,
    populate_full_signature=True
)

RecorderServiceConfig = builds(
    "agloviz.voice.recorder.RecorderService",
    enabled=True,
    input_wav="tracks/teacher.wav",
    playback_speed=1.0,
    zen_partial=True,
    populate_full_signature=True
)

# Register with ConfigStore
def register_voiceover_configs():
    cs = ConfigStore.instance()
    cs.store(group="voiceover", name="coqui", node=CoquiTTSConfig)
    cs.store(group="voiceover", name="recorder", node=RecorderServiceConfig)
    cs.store(group="voiceover", name="disabled", node=builds(
        "agloviz.voice.null.NullVoiceoverEngine",
        enabled=False,
        zen_partial=True
    ))
```

### 11.2 Configuration Files

```yaml
# config/voiceover/coqui.yaml
# @package voiceover
_target_: agloviz.voice.coqui.CoquiTTS
enabled: true
lang: "en"
voice: "en_US"
speed: 1.0

# config/voiceover/recorder.yaml  
# @package voiceover
_target_: agloviz.voice.recorder.RecorderService
enabled: true
input_wav: "tracks/teacher.wav"
playback_speed: 1.0
```

### 11.3 CLI Usage

```bash
# Use Coqui TTS
agloviz render scenario=maze_small voiceover=coqui

# Use recorder service
agloviz render scenario=maze_small voiceover=recorder

# Override parameters
agloviz render scenario=maze_small voiceover=coqui voiceover.voice=en_US_male voiceover.speed=0.9
```

---

## 12. Migration Plan (Updated for Hydra-zen First)

**Phase 0 (Structured Config Foundation)**
- Create structured configs using `builds()` for all core components.
- Register configs with ConfigStore using appropriate groups.
- Update main configuration to use hydra-zen composition.

**Phase 1 (Core Component Migration)**
- Migrate Director, VoiceoverEngine, Registry to use structured configs.
- Update instantiation to use `instantiate()` instead of direct construction.
- Add parameter template resolution with OmegaConf resolvers.

**Phase 2 (Widget System Migration)**
- Convert widget factories to structured configs.
- Update SceneEngine to use hydra-zen widget instantiation.
- Migrate event bindings to use parameter templates.

**Phase 3 (Advanced Features)**
- Add plugin support with structured configs.
- Implement advanced parameter resolution patterns.
- Add comprehensive testing for DI pipeline.

---

## 13. Reference Code Skeleton (Updated)

```python
# main.py
from hydra_zen import instantiate
from hydra.core.config_store import ConfigStore
from agloviz.di.core_configs import register_di_configs
import hydra

@hydra.main(version_base=None, config_path="configs", config_name="run")
def main(cfg):
    # Register all structured configs
    register_di_configs()
    
    # Instantiate complete object graph
    director = instantiate(cfg.director)
    return director.run()

if __name__ == "__main__":
    main()
```

```python
# core/director.py (Updated for DI)
class Director:
    def __init__(self, storyboard, timing, registry, voiceover=None, mode="normal", with_voice=False):
        self.storyboard = storyboard
        self.timing = timing
        self.registry = registry
        self.voiceover = voiceover if with_voice else None
        self.mode = mode
        
        # All dependencies injected via hydra-zen
        self.scene_engine = None  # Will be injected or created as needed
    
    @classmethod
    def from_config(cls, cfg):
        """Alternative constructor from configuration"""
        return instantiate(cfg)
```

---

## 14. Open Questions (Updated)

1. **Advanced DI Scopes**: Do we want explicit per‑act scopes with structured config inheritance?  
2. **ConfigStore Organization**: How should we organize config groups for complex plugin ecosystems?  
3. **Parameter Template Performance**: Should we cache resolved templates for repeated event processing?  
4. **Migration Strategy**: Phased migration vs. big-bang approach for existing codebase?

---

# ✅ Summary

This enhanced DI Strategy provides ALGOViz with a **hydra-zen first, config-driven, testable, and swappable** construction plan. It leverages **structured configs, ConfigStore organization, and parameter template resolution** to create a robust dependency injection system that supports complex widget hierarchies, plugin ecosystems, and runtime parameter resolution while maintaining type safety and clear error handling.

The system enables **zero-code component swapping**, **comprehensive testing strategies**, and **plugin-friendly architecture** through consistent use of hydra-zen patterns throughout the entire application stack.
