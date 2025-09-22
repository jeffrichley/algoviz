# Full Hydra-zen Implementation Plan - Option B

## 🎯 **Mission: Complete Hydra-zen Scene Management**

Transform our CLI from 80% hydra-zen to 100% hydra-zen by making scene configurations fully manageable through hydra-zen, enabling complete CLI control over widget configurations and scene experiments.

## 📊 **Current State Analysis**

### **✅ What's Already Working (4/5 Config Groups)**
```yaml
== Current Configuration Groups ==
renderer: draft, medium, hd          # ✅ Fully hydra-zen managed
scenario: maze_small, maze_large     # ✅ Fully hydra-zen managed  
theme: default, dark                 # ✅ Fully hydra-zen managed
timing: normal, fast                 # ✅ Fully hydra-zen managed
scene: MISSING                       # ❌ Manual business logic
```

### **❌ Current Scene Config Problem**
**File**: `src/agloviz/cli/render_pure_zen.py` - Lines 48-56
```python
# CURRENT MANUAL APPROACH (PROBLEM!)
scene_config = {
    "name": f"{algorithm}_pathfinding",
    "algorithm": algorithm,
    "widgets": {
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
    }
}
```

**Issues**:
- ❌ Hardcoded in function (not configurable)
- ❌ No CLI override capability
- ❌ No scene experiments possible
- ❌ Inconsistent with hydra-zen architecture

### **🎯 Target Full Hydra-zen State**
```yaml
== Target Configuration Groups ==
renderer: draft, medium, hd          # ✅ Already working
scenario: maze_small, maze_large     # ✅ Already working
theme: default, dark                 # ✅ Already working
timing: normal, fast                 # ✅ Already working
scene: bfs_basic, bfs_advanced, dfs_basic, dijkstra  # 🚀 NEW!
```

**Target CLI Capabilities**:
```bash
# Scene selection
uv run render-zen scene=bfs_advanced

# Widget-level overrides (THE GOAL!)
uv run render-zen scene.widgets.grid.width=15
uv run render-zen scene.widgets.queue.max_size=50

# Scene experiments  
uv run render-zen --multirun scene=bfs_basic,bfs_advanced,dijkstra
uv run render-zen --multirun scene.widgets.grid.width=10,15,20
```

---

## 🏗️ **PHASE 1: Scene Config Infrastructure**

### **PHASE 1.1: Create Scene Config Models**

#### **STEP 1.1.1: Enhance Scene Config Model**
**File**: `src/agloviz/config/models.py`
**Action**: Add proper scene configuration model

**Current Code** (Lines 1-62):
```python
# Current models.py has ScenarioConfig, ThemeConfig, TimingConfig
# Missing: Enhanced SceneConfig for hydra-zen
```

**Required Changes**:
```python
# ADD TO src/agloviz/config/models.py

@dataclass
class WidgetConfigSpec:
    """Widget configuration specification for hydra-zen."""
    _target_: str
    # Widget-specific parameters will be added dynamically
    
    class Config:
        extra = "allow"  # Allow widget-specific parameters


class SceneConfig(BaseModel):
    """Complete scene configuration for algorithm visualization.
    
    Fully hydra-zen compatible scene configuration that defines:
    - Algorithm-specific widget layouts
    - Widget parameters and customizations
    - Event binding configurations
    """
    name: str = Field(..., description="Scene configuration name")
    algorithm: str = Field(..., description="Target algorithm (bfs, dfs, dijkstra)")
    widgets: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Widget configurations with _target_ and parameters"
    )
    event_bindings: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Event to widget action bindings"
    )
    
    class Config:
        extra = "forbid"
        validate_assignment = True
```

**Validation**:
```bash
# Test that new model works
uv run python -c "
from agloviz.config.models import SceneConfig
scene = SceneConfig(
    name='test_scene',
    algorithm='bfs',
    widgets={'grid': {'_target_': 'agloviz.widgets.grid.GridWidget', 'width': 10}}
)
print(f'✅ SceneConfig: {scene.name} for {scene.algorithm}')
"
```

#### **STEP 1.1.2: Create Widget Configuration Builders**
**File**: `src/agloviz/config/hydra_zen.py`
**Action**: Add widget configuration builders

**Current Code** (Lines 95-123):
```python
# Current hydra_zen.py has renderer, scenario, theme, timing configs
# Missing: Widget configuration builders
```

**Required Changes**:
```python
# ADD TO src/agloviz/config/hydra_zen.py

# =====================================================================
# WIDGET CONFIGURATION BUILDERS
# =====================================================================

# Grid widget configurations
BasicGridWidget = builds(
    dict,
    _target_="agloviz.widgets.grid.GridWidget"
)

AdvancedGridWidget = builds(
    dict,
    _target_="agloviz.widgets.grid.GridWidget",
    show_coordinates=True,
    cell_size=1.2,
    border_width=2
)

ResearchGridWidget = builds(
    dict,
    _target_="agloviz.widgets.grid.GridWidget", 
    show_coordinates=True,
    show_distances=True,
    cell_size=1.5,
    highlight_mode="enhanced"
)

# Queue widget configurations  
BasicQueueWidget = builds(
    dict,
    _target_="agloviz.widgets.queue.QueueWidget"
)

AdvancedQueueWidget = builds(
    dict,
    _target_="agloviz.widgets.queue.QueueWidget",
    max_visible_items=12,
    show_size=True,
    orientation="vertical"
)

PriorityQueueWidget = builds(
    dict,
    _target_="agloviz.widgets.queue.QueueWidget",
    priority_mode=True,
    show_priorities=True,
    max_visible_items=15
)

# =====================================================================
# SCENE CONFIGURATION BUILDERS  
# =====================================================================

# BFS Scene Configurations
BFSBasicSceneConfig = builds(
    SceneConfig,
    name="bfs_basic",
    algorithm="bfs",
    widgets={
        "grid": BasicGridWidget,
        "queue": BasicQueueWidget
    },
    event_bindings={
        "enqueue": [
            {"widget": "queue", "action": "add_element", "order": 1},
            {"widget": "grid", "action": "highlight_cell", "params": {"color": "blue"}, "order": 2}
        ],
        "dequeue": [
            {"widget": "queue", "action": "remove_element", "order": 1}
        ]
    }
)

BFSAdvancedSceneConfig = builds(
    SceneConfig,
    name="bfs_advanced", 
    algorithm="bfs",
    widgets={
        "grid": AdvancedGridWidget,
        "queue": AdvancedQueueWidget,
        "legend": builds(dict, _target_="agloviz.widgets.legend.LegendWidget")
    },
    event_bindings={
        "enqueue": [
            {"widget": "queue", "action": "add_element", "order": 1},
            {"widget": "grid", "action": "highlight_cell", "params": {"color": "blue"}, "order": 2},
            {"widget": "legend", "action": "update_stats", "order": 3}
        ]
    }
)

# DFS Scene Configurations
DFSBasicSceneConfig = builds(
    SceneConfig,
    name="dfs_basic",
    algorithm="dfs", 
    widgets={
        "grid": BasicGridWidget,
        "queue": BasicQueueWidget  # Stack visualization using queue widget
    }
)

# Dijkstra Scene Configurations
DijkstraSceneConfig = builds(
    SceneConfig,
    name="dijkstra",
    algorithm="dijkstra",
    widgets={
        "grid": ResearchGridWidget,  # Show distances and weights
        "queue": BasicQueueWidget,
        "priority_queue": PriorityQueueWidget
    }
)
```

#### **STEP 1.1.3: Register Scene Configurations in Store**
**File**: `src/agloviz/config/store.py`
**Action**: Add scene config registration

**Current Code** (Lines 40-52):
```python
# Current store.py registers renderer, scenario, theme, timing
# Missing: Scene configuration registration
```

**Required Changes**:
```python
# MODIFY src/agloviz/config/store.py

# ADD import
from .hydra_zen import (
    # Existing imports...
    # NEW: Scene configs
    BFSBasicSceneConfig, BFSAdvancedSceneConfig, 
    DFSBasicSceneConfig, DijkstraSceneConfig
)

# MODIFY register_all_configs() function
def register_all_configs():
    """Register all hydra-zen configurations - simple and clean."""
    
    # Existing registrations...
    
    # NEW: Scene configurations
    scene_store = store(group="scene")
    scene_store(BFSBasicSceneConfig, name="bfs_basic")
    scene_store(BFSAdvancedSceneConfig, name="bfs_advanced")
    scene_store(DFSBasicSceneConfig, name="dfs_basic") 
    scene_store(DijkstraSceneConfig, name="dijkstra")
```

**Validation**:
```bash
# Test scene config registration
uv run python -c "
from agloviz.config.store import setup_store
from hydra.core.config_store import ConfigStore

setup_store()
cs = ConfigStore.instance()
print('Available scene configs:', list(cs.repo['scene'].keys()))
"
```

---

## 🏗️ **PHASE 2: SceneEngine Hydra-zen Integration**

### **PHASE 2.1: Refactor SceneEngine Widget Initialization**

#### **STEP 2.1.1: Update SceneEngine Constructor**
**File**: `src/agloviz/core/scene.py`
**Action**: Handle both SceneConfig objects and dict configs

**Current Code** (Lines 167-189):
```python
def __init__(self, scene_config: DictConfig | SceneConfig, timing_config=None):
    # Current logic handles DictConfig and SceneConfig
    # Needs enhancement for hydra-zen instantiated SceneConfig objects
```

**Required Changes**:
```python
# MODIFY src/agloviz/core/scene.py - SceneEngine.__init__()

def __init__(self, scene_config: DictConfig | SceneConfig | dict, timing_config=None):
    self.timing_config = timing_config
    self.widgets: Dict[str, Any] = {}
    self.event_bindings: Dict[str, list] = {}
    
    # Setup parameter resolvers
    self._setup_resolvers()
    
    # Handle multiple scene config types
    if isinstance(scene_config, SceneConfig):
        # NEW: Direct SceneConfig object from hydra-zen
        self.scene_config = OmegaConf.structured(scene_config)
        self.scene_data = scene_config
    elif isinstance(scene_config, DictConfig):
        # Existing: DictConfig from Hydra
        self.scene_config = scene_config
        if hasattr(scene_config, '_target_'):
            self.scene_data = instantiate(scene_config)
        else:
            self.scene_data = scene_config
    elif isinstance(scene_config, dict):
        # NEW: Plain dict (for backward compatibility)
        self.scene_config = OmegaConf.create(scene_config)
        self.scene_data = scene_config
    else:
        raise ValueError(f"Unsupported scene_config type: {type(scene_config)}")
    
    # Initialize scene
    self._initialize_scene()
```

#### **STEP 2.1.2: Enhance Widget Initialization Logic**
**File**: `src/agloviz/core/scene.py`
**Action**: Handle hydra-zen instantiated widgets

**Current Code** (Lines 228-251):
```python
def _initialize_widgets(self, widget_specs: Dict[str, Any]):
    # Current logic handles config dicts and some instantiated widgets
    # Needs enhancement for full hydra-zen widget handling
```

**Required Changes**:
```python
# MODIFY src/agloviz/core/scene.py - SceneEngine._initialize_widgets()

def _initialize_widgets(self, widget_specs: Dict[str, Any]):
    """Initialize widgets with full hydra-zen support.
    
    Handles three cases:
    1. Already instantiated widgets (from hydra-zen scene config instantiation)
    2. Widget config dictionaries with _target_ (traditional approach)
    3. Hydra-zen widget build objects that need instantiation
    """
    for widget_name, widget_spec in widget_specs.items():
        try:
            # CASE 1: Already instantiated widget (from hydra-zen)
            if hasattr(widget_spec, 'show') and hasattr(widget_spec, 'hide'):
                # Widget instance - use directly
                widget_instance = widget_spec
                print(f"DEBUG: Using instantiated widget {widget_name}: {type(widget_instance)}")
                
            # CASE 2: Config dictionary with _target_ (traditional)
            elif isinstance(widget_spec, dict) and '_target_' in widget_spec:
                # Dict config - instantiate it
                widget_instance = instantiate(widget_spec)
                print(f"DEBUG: Instantiated widget {widget_name} from dict config")
                
            # CASE 3: Hydra-zen build object (from builds())
            elif hasattr(widget_spec, '_target_'):
                # Structured config - instantiate it
                widget_instance = instantiate(widget_spec)
                print(f"DEBUG: Instantiated widget {widget_name} from builds config")
                
            # CASE 4: Invalid widget spec
            else:
                raise ValueError(
                    f"Widget spec for '{widget_name}' is invalid. "
                    f"Expected: instantiated widget, dict with _target_, or builds() config. "
                    f"Got: {type(widget_spec)} - {widget_spec}"
                )
            
            # Store the widget instance
            self.widgets[widget_name] = widget_instance
            
        except Exception as e:
            raise ValueError(f"Failed to initialize widget '{widget_name}': {e}") from e
```

#### **STEP 2.1.3: Add Scene Config Access Methods**
**File**: `src/agloviz/core/scene.py`
**Action**: Add methods to access scene config properties

**Required Changes**:
```python
# ADD TO src/agloviz/core/scene.py - SceneEngine class

def get_scene_name(self) -> str:
    """Get scene configuration name."""
    if hasattr(self.scene_data, 'name'):
        return self.scene_data.name
    elif isinstance(self.scene_data, dict) and 'name' in self.scene_data:
        return self.scene_data['name']
    else:
        return "unknown_scene"

def get_scene_algorithm(self) -> str:
    """Get scene target algorithm."""
    if hasattr(self.scene_data, 'algorithm'):
        return self.scene_data.algorithm
    elif isinstance(self.scene_data, dict) and 'algorithm' in self.scene_data:
        return self.scene_data['algorithm']
    else:
        return "unknown_algorithm"

def get_widget_count(self) -> int:
    """Get number of widgets in scene."""
    return len(self.widgets)

def list_widget_names(self) -> List[str]:
    """Get list of widget names in scene."""
    return list(self.widgets.keys())
```

**Validation**:
```bash
# Test SceneEngine with different config types
uv run python -c "
from agloviz.core.scene import SceneEngine
from agloviz.config.models import SceneConfig

# Test with SceneConfig object
scene_config = SceneConfig(
    name='test_scene',
    algorithm='bfs',
    widgets={'grid': {'_target_': 'agloviz.widgets.grid.GridWidget'}}
)

engine = SceneEngine(scene_config)
print(f'✅ SceneEngine with SceneConfig: {engine.get_scene_name()}')
"
```

---

## 🏗️ **PHASE 2: Scene Configuration Definitions**

### **PHASE 2.1: Create Comprehensive Scene Configurations**

#### **STEP 2.1.1: Define Widget Configuration Variants**
**File**: `src/agloviz/config/hydra_zen.py`
**Action**: Create widget configuration builders

**Current Code** (Lines 95-123):
```python
# Current hydra_zen.py has timing configs at the end
# Missing: Widget and scene configuration builders
```

**Required Changes**:
```python
# ADD TO src/agloviz/config/hydra_zen.py (after timing configs)

# =====================================================================
# WIDGET CONFIGURATION BUILDERS
# =====================================================================

# Grid Widget Variants
BasicGridConfig = builds(
    dict,
    _target_="agloviz.widgets.grid.GridWidget"
    # Uses widget defaults: no additional parameters
)

StandardGridConfig = builds(
    dict,
    _target_="agloviz.widgets.grid.GridWidget",
    width=10,
    height=10,
    cell_size=1.0
)

LargeGridConfig = builds(
    dict,
    _target_="agloviz.widgets.grid.GridWidget", 
    width=20,
    height=20,
    cell_size=0.8
)

CoordinateGridConfig = builds(
    dict,
    _target_="agloviz.widgets.grid.GridWidget",
    show_coordinates=True,
    coordinate_font_size=8
)

ResearchGridConfig = builds(
    dict,
    _target_="agloviz.widgets.grid.GridWidget",
    show_coordinates=True,
    show_distances=True,
    cell_size=1.5,
    border_width=3,
    highlight_mode="enhanced"
)

# Queue Widget Variants
BasicQueueConfig = builds(
    dict,
    _target_="agloviz.widgets.queue.QueueWidget"
    # Uses widget defaults
)

VerticalQueueConfig = builds(
    dict,
    _target_="agloviz.widgets.queue.QueueWidget",
    orientation="vertical",
    max_visible_items=10
)

LargeQueueConfig = builds(
    dict,
    _target_="agloviz.widgets.queue.QueueWidget",
    max_visible_items=20,
    show_size=True,
    item_width=1.2
)

PriorityQueueConfig = builds(
    dict,
    _target_="agloviz.widgets.queue.QueueWidget",
    priority_mode=True,
    show_priorities=True,
    max_visible_items=15,
    sort_visual=True
)

# Legend Widget Variants
BasicLegendConfig = builds(
    dict,
    _target_="agloviz.widgets.legend.LegendWidget"
)

# HUD Widget Variants  
StatsHUDConfig = builds(
    dict,
    _target_="agloviz.widgets.hud.HUDWidget",
    show_step_count=True,
    show_queue_size=True,
    show_visited_count=True
)
```

#### **STEP 2.1.2: Define Algorithm Scene Configurations**
**File**: `src/agloviz/config/hydra_zen.py`
**Action**: Create complete scene configurations for each algorithm

**Required Changes**:
```python
# ADD TO src/agloviz/config/hydra_zen.py (after widget configs)

# =====================================================================
# ALGORITHM SCENE CONFIGURATIONS
# =====================================================================

# BFS Scene Variants
BFSBasicSceneConfig = builds(
    SceneConfig,
    name="bfs_basic",
    algorithm="bfs",
    widgets={
        "grid": BasicGridConfig,
        "queue": BasicQueueConfig
    },
    event_bindings={
        "enqueue": [
            {"widget": "queue", "action": "add_element", "order": 1},
            {"widget": "grid", "action": "highlight_cell", "params": {"color": "blue"}, "order": 2}
        ],
        "dequeue": [
            {"widget": "queue", "action": "remove_element", "order": 1},
            {"widget": "grid", "action": "mark_visited", "params": {"color": "green"}, "order": 2}
        ],
        "goal_found": [
            {"widget": "grid", "action": "highlight_path", "params": {"color": "gold"}, "order": 1}
        ]
    }
)

BFSAdvancedSceneConfig = builds(
    SceneConfig,
    name="bfs_advanced",
    algorithm="bfs",
    widgets={
        "grid": CoordinateGridConfig,
        "queue": VerticalQueueConfig,
        "legend": BasicLegendConfig,
        "hud": StatsHUDConfig
    },
    event_bindings={
        "enqueue": [
            {"widget": "queue", "action": "add_element", "order": 1},
            {"widget": "grid", "action": "highlight_cell", "params": {"color": "blue"}, "order": 2},
            {"widget": "legend", "action": "update_frontier", "order": 3},
            {"widget": "hud", "action": "increment_queue_size", "order": 4}
        ]
    }
)

BFSResearchSceneConfig = builds(
    SceneConfig,
    name="bfs_research",
    algorithm="bfs",
    widgets={
        "grid": ResearchGridConfig,
        "queue": LargeQueueConfig,
        "legend": BasicLegendConfig,
        "hud": StatsHUDConfig
    }
)

# DFS Scene Variants
DFSBasicSceneConfig = builds(
    SceneConfig,
    name="dfs_basic",
    algorithm="dfs",
    widgets={
        "grid": BasicGridConfig,
        "stack": BasicQueueConfig  # Use queue widget as stack
    },
    event_bindings={
        "push": [
            {"widget": "stack", "action": "add_element", "order": 1},
            {"widget": "grid", "action": "highlight_cell", "params": {"color": "purple"}, "order": 2}
        ],
        "pop": [
            {"widget": "stack", "action": "remove_element", "params": {"index": -1}, "order": 1}
        ]
    }
)

DFSAdvancedSceneConfig = builds(
    SceneConfig,
    name="dfs_advanced",
    algorithm="dfs",
    widgets={
        "grid": CoordinateGridConfig,
        "stack": VerticalQueueConfig,
        "legend": BasicLegendConfig
    }
)

# Dijkstra Scene Variants
DijkstraBasicSceneConfig = builds(
    SceneConfig,
    name="dijkstra_basic",
    algorithm="dijkstra",
    widgets={
        "grid": ResearchGridConfig,  # Need distances for Dijkstra
        "queue": BasicQueueConfig,
        "priority_queue": PriorityQueueConfig
    }
)

DijkstraAdvancedSceneConfig = builds(
    SceneConfig,
    name="dijkstra_advanced", 
    algorithm="dijkstra",
    widgets={
        "grid": ResearchGridConfig,
        "queue": BasicQueueConfig,
        "priority_queue": PriorityQueueConfig,
        "legend": BasicLegendConfig,
        "hud": StatsHUDConfig
    }
)
```

#### **STEP 2.1.3: Register All Scene Configurations**
**File**: `src/agloviz/config/store.py`
**Action**: Register all scene variants

**Required Changes**:
```python
# MODIFY src/agloviz/config/store.py - register_all_configs()

# UPDATE scene registration section
scene_store = store(group="scene")

# BFS scenes
scene_store(BFSBasicSceneConfig, name="bfs_basic")
scene_store(BFSAdvancedSceneConfig, name="bfs_advanced") 
scene_store(BFSResearchSceneConfig, name="bfs_research")

# DFS scenes
scene_store(DFSBasicSceneConfig, name="dfs_basic")
scene_store(DFSAdvancedSceneConfig, name="dfs_advanced")

# Dijkstra scenes
scene_store(DijkstraBasicSceneConfig, name="dijkstra_basic")
scene_store(DijkstraAdvancedSceneConfig, name="dijkstra_advanced")
```

**Validation**:
```bash
# Test all scene configs can be instantiated
uv run python -c "
from agloviz.config.store import setup_store
from hydra_zen import instantiate
from hydra.core.config_store import ConfigStore

setup_store()
cs = ConfigStore.instance()

scenes = ['bfs_basic', 'bfs_advanced', 'dfs_basic', 'dijkstra_basic']
for scene_name in scenes:
    try:
        config = cs.repo['scene'][f'{scene_name}.yaml'].node
        scene = instantiate(config)
        print(f'✅ {scene_name}: {scene.name} with {len(scene.widgets)} widgets')
    except Exception as e:
        print(f'❌ {scene_name} failed: {e}')
"
```

---

## 🏗️ **PHASE 3: CLI Integration**

### **PHASE 3.1: Update Pure Hydra-zen CLI**

#### **STEP 3.1.1: Add Scene Parameter to Main Function**
**File**: `src/agloviz/cli/render_pure_zen.py`
**Action**: Add scene parameter and remove manual scene creation

**Current Code** (Lines 24-33):
```python
def render_algorithm_video(
    algorithm: str,
    renderer: SimpleRenderer,
    scenario: ScenarioConfig,
    theme: ThemeConfig,
    timing: TimingConfig,
    output_path: str = "output.mp4"
) -> Dict[str, Any]:
```

**Required Changes**:
```python
# MODIFY src/agloviz/cli/render_pure_zen.py - render_algorithm_video()

def render_algorithm_video(
    algorithm: str,
    renderer: SimpleRenderer,
    scenario: ScenarioConfig,
    theme: ThemeConfig,
    timing: TimingConfig,
    scene: SceneConfig,              # NEW: Hydra-zen managed scene config
    output_path: str = "output.mp4"
) -> Dict[str, Any]:
    """Main render function - ALL objects instantiated by hydra-zen.
    
    Now includes scene configuration management through hydra-zen,
    enabling complete CLI control over widget configurations.
    """
    console.print(Panel(f"🎬 Rendering [bold cyan]{algorithm}[/] with Full Hydra-zen", title="ALGOViz"))
    
    console.print("✨ ALL objects automatically instantiated by hydra-zen!")
    quality = renderer.config.quality.value if hasattr(renderer.config.quality, 'value') else renderer.config.quality
    console.print(f"📊 Renderer: {quality} @ {renderer.config.resolution}")
    console.print(f"🗺️  Scenario: {scenario.name} ({scenario.grid_size})")
    console.print(f"🎨 Theme: {theme.name}")
    mode = timing.mode.value if hasattr(timing.mode, 'value') else timing.mode
    console.print(f"⏱️  Timing: {mode}")
    console.print(f"🎬 Scene: {scene.name} with {len(scene.widgets)} widgets")  # NEW!
    console.print(f"   Widgets: {list(scene.widgets.keys())}")                    # NEW!
    console.print(f"🚀 Output: [bold green]{output_path}[/]")
    
    # Scene is already a fully configured SceneConfig object from hydra-zen!
    result = renderer.render_algorithm_video(
        algorithm=algorithm,
        scenario_config=scenario,
        scene_config=scene,          # Pass the hydra-zen SceneConfig object
        theme_config=theme,
        timing_config=timing,
        output_path=output_path
    )
    
    console.print(Panel(
        f"✅ Video rendered successfully!\n"
        f"📁 Output: {output_path}\n"
        f"⏱️  Duration: {result.get('duration', 'N/A')}s\n"
        f"📊 Resolution: {result.get('resolution', 'N/A')}\n"
        f"🎯 Algorithm: {algorithm}\n"
        f"🎬 Scene: {scene.name}",                            # NEW!
        title="[green]Render Complete[/]"
    ))
    
    return result
```

#### **STEP 3.1.2: Remove Manual Scene Config Creation**
**File**: `src/agloviz/cli/render_pure_zen.py`
**Action**: Remove the manual scene config creation code

**Current Code** (Lines 48-56):
```python
# REMOVE THIS ENTIRE SECTION
scene_config = {
    "name": f"{algorithm}_pathfinding",
    "algorithm": algorithm,
    "widgets": {
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
    }
}
```

**Action**: **DELETE** these lines completely - hydra-zen will handle scene config instantiation.

#### **STEP 3.1.3: Update Scene Configuration Registration**
**File**: `src/agloviz/cli/render_pure_zen.py`
**Action**: Remove local scene configs and import from hydra_zen.py

**Current Code** (Lines 140-170):
```python
# REMOVE local scene config definitions
BFSSceneConfig = builds(dict, ...)
DFSSceneConfig = builds(dict, ...)
# etc.
```

**Required Changes**:
```python
# MODIFY src/agloviz/cli/render_pure_zen.py

# REMOVE local scene config definitions

# ADD import for scene configs
from ..config.hydra_zen import (
    # Existing imports...
    # NEW: Scene configs
    BFSBasicSceneConfig, BFSAdvancedSceneConfig, BFSResearchSceneConfig,
    DFSBasicSceneConfig, DFSAdvancedSceneConfig,
    DijkstraBasicSceneConfig, DijkstraAdvancedSceneConfig
)

# UPDATE scene store registration
scene_store = store(group="scene")
scene_store(BFSBasicSceneConfig, name="bfs_basic")
scene_store(BFSAdvancedSceneConfig, name="bfs_advanced")
scene_store(BFSResearchSceneConfig, name="bfs_research")
scene_store(DFSBasicSceneConfig, name="dfs_basic")
scene_store(DFSAdvancedSceneConfig, name="dfs_advanced")
scene_store(DijkstraBasicSceneConfig, name="dijkstra_basic")
scene_store(DijkstraAdvancedSceneConfig, name="dijkstra_advanced")
```

#### **STEP 3.1.4: Update Default Configuration**
**File**: `src/agloviz/cli/render_pure_zen.py`
**Action**: Add scene to hydra_defaults

**Current Code** (Lines 200-205):
```python
hydra_defaults=[
    "_self_",
    {"renderer": "medium"},
    {"scenario": "maze_small"},
    {"theme": "default"},
    {"timing": "normal"}
],
```

**Required Changes**:
```python
# MODIFY src/agloviz/cli/render_pure_zen.py - store() call

hydra_defaults=[
    "_self_",
    {"renderer": "medium"},
    {"scenario": "maze_small"},
    {"theme": "default"},
    {"timing": "normal"},
    {"scene": "bfs_basic"}        # NEW: Default scene configuration
],
```

---

## 🏗️ **PHASE 4: Testing & Validation**

### **PHASE 4.1: Unit Tests for Scene Config System**

#### **STEP 4.1.1: Create Scene Config Model Tests**
**File**: `tests/unit/test_scene_config_models.py` (NEW)
**Action**: Test new SceneConfig model

**Required Code**:
```python
"""Tests for enhanced SceneConfig model."""

import pytest
from agloviz.config.models import SceneConfig

class TestSceneConfigModel:
    """Test SceneConfig Pydantic model."""
    
    def test_scene_config_creation(self):
        """Test basic SceneConfig creation."""
        scene = SceneConfig(
            name="test_scene",
            algorithm="bfs",
            widgets={
                "grid": {"_target_": "agloviz.widgets.grid.GridWidget", "width": 10},
                "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
            }
        )
        
        assert scene.name == "test_scene"
        assert scene.algorithm == "bfs"
        assert len(scene.widgets) == 2
        assert "grid" in scene.widgets
        assert scene.widgets["grid"]["_target_"] == "agloviz.widgets.grid.GridWidget"
    
    def test_scene_config_validation(self):
        """Test SceneConfig validation."""
        # Should require name and algorithm
        with pytest.raises(ValueError):
            SceneConfig(widgets={})
    
    def test_scene_config_with_event_bindings(self):
        """Test SceneConfig with event bindings."""
        scene = SceneConfig(
            name="test_scene",
            algorithm="bfs",
            widgets={"grid": {"_target_": "agloviz.widgets.grid.GridWidget"}},
            event_bindings={
                "enqueue": [
                    {"widget": "grid", "action": "highlight_cell", "order": 1}
                ]
            }
        )
        
        assert "enqueue" in scene.event_bindings
        assert len(scene.event_bindings["enqueue"]) == 1
```

#### **STEP 4.1.2: Create Scene Config Builder Tests**
**File**: `tests/unit/test_scene_config_builders.py` (NEW)
**Action**: Test hydra-zen scene config builders

**Required Code**:
```python
"""Tests for hydra-zen scene configuration builders."""

import pytest
from hydra_zen import instantiate

from agloviz.config.hydra_zen import (
    BFSBasicSceneConfig, BFSAdvancedSceneConfig, BFSResearchSceneConfig,
    DFSBasicSceneConfig, DFSAdvancedSceneConfig,
    DijkstraBasicSceneConfig, DijkstraAdvancedSceneConfig
)
from agloviz.config.models import SceneConfig

class TestSceneConfigBuilders:
    """Test scene configuration builders."""
    
    def test_bfs_basic_scene_instantiation(self):
        """Test BFS basic scene config instantiation."""
        scene = instantiate(BFSBasicSceneConfig)
        assert isinstance(scene, SceneConfig)
        assert scene.name == "bfs_basic"
        assert scene.algorithm == "bfs"
        assert "grid" in scene.widgets
        assert "queue" in scene.widgets
    
    def test_bfs_advanced_scene_instantiation(self):
        """Test BFS advanced scene config instantiation."""
        scene = instantiate(BFSAdvancedSceneConfig)
        assert isinstance(scene, SceneConfig)
        assert scene.name == "bfs_advanced"
        assert len(scene.widgets) >= 3  # grid, queue, legend
        assert "legend" in scene.widgets
    
    def test_dijkstra_scene_instantiation(self):
        """Test Dijkstra scene config instantiation."""
        scene = instantiate(DijkstraBasicSceneConfig)
        assert isinstance(scene, SceneConfig)
        assert scene.algorithm == "dijkstra"
        assert "priority_queue" in scene.widgets
    
    def test_all_scene_configs_have_required_fields(self):
        """Test that all scene configs have required fields."""
        configs = [
            BFSBasicSceneConfig, BFSAdvancedSceneConfig, BFSResearchSceneConfig,
            DFSBasicSceneConfig, DFSAdvancedSceneConfig,
            DijkstraBasicSceneConfig, DijkstraAdvancedSceneConfig
        ]
        
        for config in configs:
            scene = instantiate(config)
            assert hasattr(scene, 'name')
            assert hasattr(scene, 'algorithm')
            assert hasattr(scene, 'widgets')
            assert len(scene.widgets) > 0
```

#### **STEP 4.1.3: Create SceneEngine Integration Tests**
**File**: `tests/unit/test_scene_engine_hydra_zen.py` (NEW)
**Action**: Test SceneEngine with hydra-zen scene configs

**Required Code**:
```python
"""Tests for SceneEngine integration with hydra-zen scene configs."""

import pytest
from hydra_zen import instantiate

from agloviz.core.scene import SceneEngine
from agloviz.config.hydra_zen import BFSBasicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode

class TestSceneEngineHydraZenIntegration:
    """Test SceneEngine with hydra-zen scene configs."""
    
    def test_scene_engine_with_scene_config_object(self):
        """Test SceneEngine with hydra-zen instantiated SceneConfig."""
        # Instantiate scene config with hydra-zen
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        
        # Create SceneEngine with SceneConfig object
        engine = SceneEngine(scene_config, timing_config)
        
        assert engine.get_scene_name() == "bfs_basic"
        assert engine.get_scene_algorithm() == "bfs" 
        assert engine.get_widget_count() == 2  # grid + queue
        assert "grid" in engine.list_widget_names()
        assert "queue" in engine.list_widget_names()
    
    def test_scene_engine_widget_initialization_with_hydra_zen(self):
        """Test that SceneEngine properly initializes hydra-zen widgets."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)
        
        # Check that widgets are properly initialized
        assert len(engine.widgets) == 2
        
        grid_widget = engine.widgets["grid"]
        queue_widget = engine.widgets["queue"]
        
        # Widgets should have the Widget protocol methods
        assert hasattr(grid_widget, 'show')
        assert hasattr(grid_widget, 'hide')
        assert hasattr(queue_widget, 'show')
        assert hasattr(queue_widget, 'hide')
```

### **PHASE 4.2: CLI Integration Tests**

#### **STEP 4.2.1: Create Full CLI Tests**
**File**: `tests/unit/test_full_hydra_zen_cli.py` (NEW)
**Action**: Test complete hydra-zen CLI functionality

**Required Code**:
```python
"""Tests for full hydra-zen CLI implementation."""

import subprocess
import sys
import pytest

class TestFullHydraZenCLI:
    """Test complete hydra-zen CLI functionality."""
    
    def test_cli_shows_all_config_groups(self):
        """Test that CLI shows all 5 config groups including scene."""
        result = subprocess.run([
            "uv", "run", "render-zen", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "renderer:" in result.stdout
        assert "scenario:" in result.stdout
        assert "theme:" in result.stdout
        assert "timing:" in result.stdout
        assert "scene:" in result.stdout  # NEW!
    
    def test_scene_config_selection(self):
        """Test scene configuration selection."""
        result = subprocess.run([
            "uv", "run", "render-zen", "scene=bfs_advanced", "output_path=test_scene.mp4"
        ], capture_output=True, text=True, timeout=60)
        
        assert result.returncode == 0
        assert "bfs_advanced" in result.stdout
        assert "Video rendered successfully!" in result.stdout
    
    def test_widget_parameter_overrides(self):
        """Test widget parameter overrides through scene config."""
        result = subprocess.run([
            "uv", "run", "render-zen", 
            "scene.widgets.grid.width=15",
            "scene.widgets.queue.max_size=25",
            "output_path=test_widget_override.mp4"
        ], capture_output=True, text=True, timeout=60)
        
        # Should work without errors
        assert result.returncode == 0
        assert "Video rendered successfully!" in result.stdout
    
    def test_scene_multirun_experiments(self):
        """Test multi-run experiments on scene configurations.""" 
        result = subprocess.run([
            "uv", "run", "render-zen",
            "--multirun", 
            "scene=bfs_basic,bfs_advanced",
            "output_path=multirun_test.mp4"
        ], capture_output=True, text=True, timeout=120)
        
        # Should run multiple experiments
        assert result.returncode == 0
        # Would create multiple output directories with different configs
```

---

## 🏗️ **PHASE 5: Advanced Features**

### **PHASE 5.1: Widget Configuration Experiments**

#### **STEP 5.1.1: Create Widget Variant Configs**
**File**: `src/agloviz/config/hydra_zen.py`
**Action**: Add experimental widget configurations

**Required Changes**:
```python
# ADD TO src/agloviz/config/hydra_zen.py

# =====================================================================
# EXPERIMENTAL WIDGET CONFIGURATIONS
# =====================================================================

# Grid size experiments
SmallGridConfig = builds(dict, _target_="agloviz.widgets.grid.GridWidget", width=5, height=5)
MediumGridConfig = builds(dict, _target_="agloviz.widgets.grid.GridWidget", width=10, height=10)
LargeGridConfig = builds(dict, _target_="agloviz.widgets.grid.GridWidget", width=20, height=20)

# Grid visual experiments
MinimalGridConfig = builds(dict, _target_="agloviz.widgets.grid.GridWidget", border_width=1, cell_size=0.8)
BoldGridConfig = builds(dict, _target_="agloviz.widgets.grid.GridWidget", border_width=4, cell_size=1.5)

# Queue experiments
HorizontalQueueConfig = builds(dict, _target_="agloviz.widgets.queue.QueueWidget", orientation="horizontal")
VerticalQueueConfig = builds(dict, _target_="agloviz.widgets.queue.QueueWidget", orientation="vertical")
CompactQueueConfig = builds(dict, _target_="agloviz.widgets.queue.QueueWidget", item_width=0.8, max_visible_items=6)

# =====================================================================
# EXPERIMENTAL SCENE CONFIGURATIONS
# =====================================================================

# Grid size experiment scenes
BFSSmallGridSceneConfig = builds(
    SceneConfig,
    name="bfs_small_grid",
    algorithm="bfs",
    widgets={"grid": SmallGridConfig, "queue": BasicQueueConfig}
)

BFSLargeGridSceneConfig = builds(
    SceneConfig,
    name="bfs_large_grid", 
    algorithm="bfs",
    widgets={"grid": LargeGridConfig, "queue": BasicQueueConfig}
)

# Visual style experiment scenes
BFSMinimalSceneConfig = builds(
    SceneConfig,
    name="bfs_minimal",
    algorithm="bfs",
    widgets={"grid": MinimalGridConfig, "queue": CompactQueueConfig}
)

BFSBoldSceneConfig = builds(
    SceneConfig,
    name="bfs_bold",
    algorithm="bfs", 
    widgets={"grid": BoldGridConfig, "queue": VerticalQueueConfig}
)
```

#### **STEP 5.1.2: Register Experimental Configurations**
**File**: `src/agloviz/config/store.py`
**Action**: Register experimental scene configs

**Required Changes**:
```python
# ADD TO src/agloviz/config/store.py - register_all_configs()

# Experimental scene configurations
scene_store(BFSSmallGridSceneConfig, name="bfs_small_grid")
scene_store(BFSLargeGridSceneConfig, name="bfs_large_grid")
scene_store(BFSMinimalSceneConfig, name="bfs_minimal")
scene_store(BFSBoldSceneConfig, name="bfs_bold")
```

### **PHASE 5.2: Advanced CLI Features**

#### **STEP 5.2.1: Test Advanced Override Capabilities**
**Validation Commands**:
```bash
# Test all new capabilities

# 1. Scene selection
uv run render-zen scene=bfs_advanced                    # Select advanced scene
uv run render-zen scene=dijkstra_basic                  # Select Dijkstra scene

# 2. Widget parameter overrides
uv run render-zen scene.widgets.grid.width=15           # Override grid width
uv run render-zen scene.widgets.queue.max_size=25       # Override queue size
uv run render-zen scene.widgets.grid.show_coordinates=true  # Enable coordinates

# 3. Deep nested overrides
uv run render-zen scene.widgets.grid.cell_size=1.5 scene.widgets.queue.orientation=vertical

# 4. Multi-run scene experiments
uv run render-zen --multirun scene=bfs_basic,bfs_advanced,bfs_research
uv run render-zen --multirun scene.widgets.grid.width=10,15,20
uv run render-zen --multirun algorithm=bfs,dfs scene=basic,advanced

# 5. Combined experiments
uv run render-zen --multirun renderer=medium,hd scene=bfs_basic,bfs_advanced scenario=maze_small,maze_large

# 6. Research experiments
uv run render-zen --multirun scene.widgets.grid.cell_size=0.5,1.0,1.5,2.0 algorithm=bfs,dfs
```

---

## 🎯 **PHASE 6: Final Integration**

### **PHASE 6.1: Update Entry Points**

#### **STEP 6.1.1: Update pyproject.toml**
**File**: `pyproject.toml`
**Action**: Make render-zen the primary CLI

**Current Code** (Lines 58-60):
```toml
[project.scripts]
agloviz = "agloviz.cli:app"
render = "agloviz.cli.render_app:app"
render-zen = "agloviz.cli.render_pure_zen:main"
```

**Required Changes**:
```toml
# MODIFY pyproject.toml

[project.scripts]
agloviz = "agloviz.cli:app"                          # Legacy CLI
render-legacy = "agloviz.cli.render_app:app"         # Rename old CLI
render = "agloviz.cli.render_pure_zen:main"          # NEW: Full hydra-zen CLI as primary
render-zen = "agloviz.cli.render_pure_zen:main"      # Alias for clarity
```

#### **STEP 6.1.2: Create Migration Documentation**
**File**: `MIGRATION_TO_FULL_HYDRA_ZEN.md` (NEW)
**Action**: Document migration path for users

**Required Content**:
```markdown
# Migration to Full Hydra-zen CLI

## New CLI Capabilities

### Scene Configuration Control
# Old way (not possible)
# Had to modify code to change widget setups

# New way (full control)
uv run render scene=bfs_advanced                     # Select scene variant
uv run render scene.widgets.grid.width=15            # Override widget parameters
uv run render --multirun scene=basic,advanced        # Scene experiments

### Available Scene Configurations
- `bfs_basic`: Basic BFS with grid + queue
- `bfs_advanced`: BFS with coordinates, legend, HUD
- `bfs_research`: BFS with enhanced grid for research
- `dfs_basic`: Basic DFS with grid + stack
- `dfs_advanced`: DFS with enhanced visualization
- `dijkstra_basic`: Dijkstra with priority queue
- `dijkstra_advanced`: Dijkstra with full research setup

### Migration Commands
# Old CLI still available as:
uv run render-legacy video bfs --quality hd

# New CLI (recommended):
uv run render algorithm=bfs renderer=hd scene=bfs_advanced
```

---

## 📊 **Implementation Timeline**

### **Week 1: Core Infrastructure**
- **Day 1**: PHASE 1 - Scene config models and builders
- **Day 2**: PHASE 2.1 - SceneEngine refactor
- **Day 3**: PHASE 2.2 - Scene config definitions
- **Day 4**: PHASE 3 - CLI integration
- **Day 5**: Testing and validation

### **Week 2: Advanced Features**
- **Day 1**: PHASE 4 - Comprehensive testing
- **Day 2**: PHASE 5 - Experimental configurations
- **Day 3**: PHASE 6 - Final integration
- **Day 4**: Documentation and migration guides
- **Day 5**: User acceptance testing

---

## ✅ **Success Criteria**

### **Functional Requirements**
1. **✅ 5 Config Groups**: renderer, scenario, theme, timing, scene all hydra-zen managed
2. **✅ Widget Overrides**: `scene.widgets.grid.width=15` works from CLI
3. **✅ Scene Experiments**: `--multirun scene=basic,advanced` works
4. **✅ Deep Overrides**: `scene.widgets.grid.cell_size=1.5` works
5. **✅ Algorithm Variants**: Multiple scene configs per algorithm
6. **✅ Backward Compatibility**: Existing render functionality unchanged

### **Technical Requirements**
1. **✅ SceneEngine Compatibility**: Works with both config dicts and SceneConfig objects
2. **✅ Widget Instantiation**: Handles both hydra-zen instantiated and config widgets
3. **✅ Type Safety**: All scene configs validated through builds()
4. **✅ Error Handling**: Clear error messages for invalid configurations

### **User Experience Requirements**
1. **✅ CLI Consistency**: All config groups follow same override patterns
2. **✅ Rich Help**: Scene configs show available options and current values
3. **✅ Experiment Support**: Multi-run works across all config dimensions
4. **✅ Research Features**: Fine-grained widget control for research use cases

---

## 🚨 **Risk Mitigation**

### **Potential Issues & Solutions**

1. **Widget Instantiation Conflicts**:
   - **Risk**: Widgets instantiated twice (hydra-zen + SceneEngine)
   - **Solution**: Enhanced type checking in `_initialize_widgets()`

2. **Scene Config Complexity**:
   - **Risk**: Too many scene config variants to maintain
   - **Solution**: Start with basic variants, add more based on user needs

3. **Breaking Changes**:
   - **Risk**: Existing scene functionality breaks
   - **Solution**: Maintain backward compatibility in SceneEngine

4. **Performance Impact**:
   - **Risk**: Additional config instantiation slows down rendering
   - **Solution**: Profile and optimize if needed

---

**This plan provides complete hydra-zen scene management with full CLI control over widget configurations, enabling advanced research experiments while maintaining architectural consistency.**
