# Hydra-zen Scene Config Analysis

## 🔍 **Current State: What We Have Working**

### **Current Working Pure Hydra-zen CLI**

**File**: `src/agloviz/cli/render_pure_zen.py`

**What Works Perfectly**:
```python
def render_algorithm_video(
    algorithm: str,
    renderer: SimpleRenderer,        # ✅ Hydra-zen instantiated
    scenario: ScenarioConfig,        # ✅ Hydra-zen instantiated  
    theme: ThemeConfig,              # ✅ Hydra-zen instantiated
    timing: TimingConfig,            # ✅ Hydra-zen instantiated
    output_path: str = "output.mp4"
):
    # ❓ Scene config - this is where the question is
    scene_config = {
        "name": f"{algorithm}_pathfinding",
        "algorithm": algorithm,
        "widgets": {
            "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
            "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
        }
    }
    
    # All other objects already instantiated by hydra-zen!
    return renderer.render_algorithm_video(...)
```

**CLI Usage Examples (Working)**:
```bash
# Basic usage - all automatic
uv run render-zen                                    # ✅ Works perfectly

# Simple overrides - all automatic  
uv run render-zen algorithm=dfs                      # ✅ Works perfectly
uv run render-zen renderer=hd                        # ✅ Works perfectly
uv run render-zen scenario=maze_large                # ✅ Works perfectly
uv run render-zen theme=dark                         # ✅ Works perfectly

# Deep overrides - all automatic
uv run render-zen renderer.render_config.resolution=[1920,1080]  # ✅ Works perfectly
uv run render-zen scenario.start=[2,2]               # ✅ Works perfectly
uv run render-zen theme.colors.visited="#FF0000"     # ✅ Works perfectly

# Multi-run experiments - all automatic
uv run render-zen --multirun renderer=draft,medium,hd            # ✅ Would work
uv run render-zen --multirun algorithm=bfs,dfs scenario=maze_small,maze_large  # ✅ Would work
```

**Configuration Groups Available**:
```yaml
# From --help output
== Configuration groups ==
renderer: draft, medium, hd
scenario: maze_small, maze_large  
theme: default, dark
timing: normal, fast
```

---

## 🎯 **The Scene Config Question**

### **Current Approach: Manual Scene Config**
```python
# In render_algorithm_video() function
scene_config = {
    "name": f"{algorithm}_pathfinding",
    "algorithm": algorithm,
    "widgets": {
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
    }
}
```

**What This Means**:
- Scene config is **not** hydra-zen managed
- Scene config is created as simple business logic
- Users **cannot** override scene widgets from CLI
- Scene setup is **hardcoded** in the function

---

## 🚀 **Option A: Keep Scene Config Simple (Current Working)**

### **Implementation**:
```python
def render_algorithm_video(
    algorithm: str,
    renderer: SimpleRenderer,        # ✅ Hydra-zen managed
    scenario: ScenarioConfig,        # ✅ Hydra-zen managed
    theme: ThemeConfig,              # ✅ Hydra-zen managed
    timing: TimingConfig,            # ✅ Hydra-zen managed
    output_path: str = "output.mp4"
):
    # Simple business logic - NOT hydra-zen managed
    scene_config = create_scene_for_algorithm(algorithm)
    
    return renderer.render_algorithm_video(
        scene_config=scene_config,  # Simple dict with _target_ configs
        # ... other hydra-zen instantiated objects
    )

def create_scene_for_algorithm(algorithm: str) -> dict:
    """Simple business logic to create scene config."""
    base_widgets = {
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
    }
    
    if algorithm == "dijkstra":
        base_widgets["priority_queue"] = {"_target_": "agloviz.widgets.queue.QueueWidget"}
    
    return {
        "name": f"{algorithm}_pathfinding",
        "algorithm": algorithm,
        "widgets": base_widgets
    }
```

### **CLI Usage Examples**:
```bash
# What works
uv run render-zen algorithm=bfs renderer=hd scenario=maze_large  # ✅ Works
uv run render-zen renderer.render_config.resolution=[1920,1080] # ✅ Works
uv run render-zen scenario.start=[2,2] theme.colors.visited="#FF0000"  # ✅ Works

# What doesn't work
uv run render-zen scene.widgets.grid.width=20                   # ❌ No scene config group
uv run render-zen --multirun scene=bfs_basic,bfs_advanced       # ❌ No scene variations
```

### **Pros**:
- ✅ **Works immediately** with existing SceneEngine
- ✅ **Simple and predictable** scene logic
- ✅ **80% hydra-zen benefits** with 20% complexity
- ✅ **No architectural changes** needed

### **Cons**:
- ❌ **No scene CLI control**: Can't override widget configs from CLI
- ❌ **No scene experiments**: Can't do multi-run on scene variations
- ❌ **Inconsistent architecture**: Some things hydra-zen, some not
- ❌ **Limited scene flexibility**: Scene setup is hardcoded

---

## 🎯 **Option B: Full Hydra-zen Scene Management**

### **Implementation**:
```python
# Scene config becomes a proper hydra-zen managed configuration
@dataclass
class SceneConfig:
    name: str
    algorithm: str  
    widgets: Dict[str, Any]  # Widget configurations

# Scene configs defined with builds()
BFSSceneConfig = builds(
    SceneConfig,
    name="bfs_pathfinding",
    algorithm="bfs",
    widgets={
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget", "width": 10, "height": 10},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget", "max_size": 20}
    }
)

BFSAdvancedSceneConfig = builds(
    SceneConfig,
    name="bfs_advanced",
    algorithm="bfs",
    widgets={
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget", "width": 15, "height": 15, "show_coordinates": True},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget", "max_size": 50, "show_size": True},
        "legend": {"_target_": "agloviz.widgets.legend.LegendWidget"}
    }
)

DijkstraSceneConfig = builds(
    SceneConfig,
    name="dijkstra_pathfinding",
    algorithm="dijkstra",
    widgets={
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget", "show_weights": True},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"},
        "priority_queue": {"_target_": "agloviz.widgets.queue.QueueWidget", "priority_mode": True}
    }
)

# Store scene configurations
scene_store = store(group="scene")
scene_store(BFSSceneConfig, name="bfs_basic")
scene_store(BFSAdvancedSceneConfig, name="bfs_advanced")  
scene_store(DijkstraSceneConfig, name="dijkstra")

def render_algorithm_video(
    algorithm: str,
    renderer: SimpleRenderer,        # ✅ Hydra-zen managed
    scenario: ScenarioConfig,        # ✅ Hydra-zen managed
    theme: ThemeConfig,              # ✅ Hydra-zen managed
    timing: TimingConfig,            # ✅ Hydra-zen managed
    scene: SceneConfig,              # ✅ Hydra-zen managed (NEW!)
    output_path: str = "output.mp4"
):
    # Everything is hydra-zen managed!
    return renderer.render_algorithm_video(
        scene_config=scene,  # SceneConfig object with widget configs
        # ... other objects
    )
```

### **Required SceneEngine Changes**:
```python
# In SceneEngine._initialize_widgets()
def _initialize_widgets(self, widget_specs: Dict[str, Any]):
    for widget_name, widget_spec in widget_specs.items():
        try:
            # NEW: Handle already instantiated widgets (from hydra-zen)
            if hasattr(widget_spec, 'show') and hasattr(widget_spec, 'hide'):
                # Already a widget instance from hydra-zen instantiation
                widget_instance = widget_spec
            # EXISTING: Handle config dictionaries  
            elif isinstance(widget_spec, dict) and '_target_' in widget_spec:
                # Dict config that needs instantiation
                widget_instance = instantiate(widget_spec)
            else:
                raise ValueError(f"Invalid widget spec: {widget_spec}")
            
            self.widgets[widget_name] = widget_instance
        except Exception as e:
            raise ValueError(f"Failed to initialize widget '{widget_name}': {e}") from e
```

### **CLI Usage Examples**:
```bash
# Basic scene selection
uv run render-zen scene=bfs_basic                    # Use basic BFS scene
uv run render-zen scene=bfs_advanced                 # Use advanced BFS scene with legend
uv run render-zen scene=dijkstra                     # Use Dijkstra scene with priority queue

# Scene widget overrides (NEW CAPABILITY!)
uv run render-zen scene.widgets.grid.width=15       # Override grid width
uv run render-zen scene.widgets.queue.max_size=50   # Override queue size
uv run render-zen scene.widgets.grid.show_coordinates=true  # Enable coordinates

# Scene experiments (NEW CAPABILITY!)
uv run render-zen --multirun scene=bfs_basic,bfs_advanced,dijkstra
uv run render-zen --multirun scene.widgets.grid.width=10,15,20
uv run render-zen --multirun algorithm=bfs,dfs scene=basic,advanced

# Combined overrides (MAXIMUM POWER!)
uv run render-zen algorithm=bfs renderer=hd scenario=maze_large theme=dark scene=bfs_advanced scene.widgets.grid.width=20
```

### **Configuration Groups Available**:
```yaml
== Configuration groups ==
renderer: draft, medium, hd
scenario: maze_small, maze_large, weighted_graph
theme: default, dark, high_contrast  
timing: draft, normal, fast
scene: bfs_basic, bfs_advanced, dfs_basic, dijkstra  # NEW!
```

### **Pros**:
- ✅ **Complete CLI control** over every aspect including widgets
- ✅ **Scene experiments**: Multi-run on different scene configurations
- ✅ **Widget customization**: Override any widget parameter from CLI
- ✅ **Algorithm variations**: Different scene setups for same algorithm (basic vs advanced)
- ✅ **Research flexibility**: Researchers can experiment with widget layouts
- ✅ **Architectural consistency**: Everything follows hydra-zen patterns
- ✅ **Type safety**: Scene configs validated through builds()
- ✅ **Reproducible scenes**: Every scene configuration automatically saved

### **Cons**:
- ❌ **SceneEngine refactor required**: Need to handle both instantiated and config widgets
- ❌ **More complex scene definitions**: Need builds() for every scene variation
- ❌ **Potential widget instantiation issues**: Need to ensure widgets work with both approaches

---

## 🎯 **Option C: Hybrid with Scene Templates**

### **Implementation**:
```python
def render_algorithm_video(
    algorithm: str,
    renderer: SimpleRenderer,        # ✅ Hydra-zen managed
    scenario: ScenarioConfig,        # ✅ Hydra-zen managed
    theme: ThemeConfig,              # ✅ Hydra-zen managed
    timing: TimingConfig,            # ✅ Hydra-zen managed
    scene_template: str = "basic",   # ✅ Hydra-zen managed (simple string)
    output_path: str = "output.mp4"
):
    # Generate scene config from template + algorithm (business logic)
    scene_config = create_scene_from_template(algorithm, scene_template, scenario)
    
    return renderer.render_algorithm_video(scene_config=scene_config, ...)

def create_scene_from_template(algorithm: str, template: str, scenario: ScenarioConfig) -> dict:
    """Generate scene config from template."""
    if template == "basic":
        widgets = {
            "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
            "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
        }
    elif template == "advanced":
        widgets = {
            "grid": {"_target_": "agloviz.widgets.grid.GridWidget", "show_coordinates": True},
            "queue": {"_target_": "agloviz.widgets.queue.QueueWidget", "show_size": True},
            "legend": {"_target_": "agloviz.widgets.legend.LegendWidget"}
        }
    elif template == "research":
        widgets = {
            "grid": {"_target_": "agloviz.widgets.grid.GridWidget", "cell_size": 1.5},
            "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"},
            "hud": {"_target_": "agloviz.widgets.hud.HUDWidget"},
            "stats": {"_target_": "agloviz.widgets.stats.StatsWidget"}
        }
    
    if algorithm == "dijkstra":
        widgets["priority_queue"] = {"_target_": "agloviz.widgets.queue.QueueWidget", "priority_mode": True}
    
    return {
        "name": f"{algorithm}_{template}",
        "algorithm": algorithm,
        "widgets": widgets
    }

# Scene templates stored in hydra-zen
scene_template_store = store(group="scene_template")
scene_template_store("basic", name="basic")
scene_template_store("advanced", name="advanced") 
scene_template_store("research", name="research")
```

### **CLI Usage Examples**:
```bash
# Template selection
uv run render-zen scene_template=basic               # Basic widget set
uv run render-zen scene_template=advanced            # Advanced widget set with legend
uv run render-zen scene_template=research            # Research widget set with HUD/stats

# Template experiments
uv run render-zen --multirun scene_template=basic,advanced,research
uv run render-zen --multirun algorithm=bfs,dfs scene_template=basic,advanced

# Still no widget-level overrides
uv run render-zen scene.widgets.grid.width=20       # ❌ Doesn't work
```

### **Pros**:
- ✅ **Scene variations**: Different templates for different use cases
- ✅ **Algorithm-aware**: Templates can adapt based on algorithm
- ✅ **Simple implementation**: No SceneEngine changes needed
- ✅ **Template experiments**: Multi-run on different templates

### **Cons**:
- ❌ **No widget-level control**: Can't override individual widget parameters
- ❌ **Limited flexibility**: Predefined templates only
- ❌ **Still hybrid architecture**: Not fully hydra-zen

---

## 📊 **Detailed Comparison**

### **User Experience Comparison**

#### **Research Scientist Use Case**:
```bash
# "I want to experiment with different grid cell sizes for my paper"

# Option A (Current): ❌ Not possible
# Can't override widget parameters

# Option B (Full Hydra-zen): ✅ Perfect
uv run render-zen scene.widgets.grid.cell_size=0.5
uv run render-zen --multirun scene.widgets.grid.cell_size=0.5,1.0,1.5,2.0
uv run render-zen scene.widgets.grid.show_coordinates=true scene.widgets.queue.orientation=vertical

# Option C (Templates): ⚠️ Limited
uv run render-zen scene_template=research  # Only if we predefined this template
```

#### **Student Use Case**:
```bash
# "I just want to render BFS with good quality"

# Option A (Current): ✅ Perfect
uv run render-zen algorithm=bfs renderer=hd scenario=maze_large

# Option B (Full Hydra-zen): ✅ Perfect (same + more power)
uv run render-zen algorithm=bfs renderer=hd scenario=maze_large scene=bfs_basic

# Option C (Templates): ✅ Good
uv run render-zen algorithm=bfs renderer=hd scenario=maze_large scene_template=basic
```

#### **Algorithm Developer Use Case**:
```bash
# "I'm implementing a new algorithm and need custom widget setup"

# Option A (Current): ❌ Need to modify code
# Have to edit render_algorithm_video() function to add new algorithm case

# Option B (Full Hydra-zen): ✅ Perfect
# Just create new scene config:
NewAlgorithmSceneConfig = builds(SceneConfig, 
    algorithm="my_algorithm",
    widgets={"custom_widget": builds(MyCustomWidget)}
)
scene_store(NewAlgorithmSceneConfig, name="my_algorithm")

# Option C (Templates): ⚠️ Need new template
# Have to add new template to create_scene_from_template() function
```

### **Code Complexity Comparison**

#### **Option A (Current)**:
```python
# Pros: Simple, works immediately
# Cons: Hardcoded scene logic

def render_algorithm_video(...):
    if algorithm == "bfs":
        widgets = {"grid": ..., "queue": ...}
    elif algorithm == "dfs": 
        widgets = {"grid": ..., "queue": ...}
    elif algorithm == "dijkstra":
        widgets = {"grid": ..., "queue": ..., "priority_queue": ...}
    # Need to add new cases for new algorithms
```

#### **Option B (Full Hydra-zen)**:
```python
# Pros: Fully configurable, extensible
# Cons: Requires SceneEngine refactor

# Scene configs defined declaratively
BFSSceneConfig = builds(SceneConfig, widgets={...})
DFSSceneConfig = builds(SceneConfig, widgets={...})
DijkstraSceneConfig = builds(SceneConfig, widgets={...})

# Function is pure - no algorithm-specific logic
def render_algorithm_video(algorithm, renderer, scenario, theme, timing, scene, output_path):
    return renderer.render_algorithm_video(scene_config=scene, ...)

# SceneEngine needs update:
def _initialize_widgets(self, widget_specs):
    for name, spec in widget_specs.items():
        if hasattr(spec, 'show'):  # Already instantiated by hydra-zen
            self.widgets[name] = spec
        else:  # Config dict
            self.widgets[name] = instantiate(spec)
```

#### **Option C (Templates)**:
```python
# Pros: Some flexibility, no SceneEngine changes
# Cons: Still has hardcoded logic, just moved

def create_scene_from_template(algorithm, template, scenario):
    if template == "basic":
        widgets = {...}
    elif template == "advanced":
        widgets = {...}
    elif template == "research":
        widgets = {...}
    
    if algorithm == "dijkstra":
        widgets["priority_queue"] = ...
    
    # Still hardcoded, just organized differently
```

---

## 🎯 **My Analysis & Recommendation**

### **The Core Question**:
**Are scene configurations "data" (like RenderConfig) or "code" (like business logic)?**

**If scene configs are DATA**:
- Different algorithms need different widget setups
- Researchers want to experiment with widget parameters
- Scene variations should be configurable from CLI
- **→ Go with Option B (Full Hydra-zen)**

**If scene configs are CODE**:  
- Scene setup is algorithm implementation detail
- Widget arrangement is business logic
- Users don't need to customize widget parameters
- **→ Stay with Option A (Current)**

### **Looking at Real Use Cases**:

1. **Research Papers**: "Effect of grid cell size on algorithm visualization comprehension"
   - **Needs**: `scene.widgets.grid.cell_size=0.5,1.0,1.5`
   - **Verdict**: Scene configs are DATA

2. **Educational Content**: "Comparing BFS basic vs advanced visualization"
   - **Needs**: `scene=bfs_basic vs scene=bfs_advanced`
   - **Verdict**: Scene configs are DATA

3. **Algorithm Development**: "My new algorithm needs a custom widget layout"
   - **Needs**: Ability to define new scene configs without code changes
   - **Verdict**: Scene configs are DATA

## 🚀 **Final Recommendation: Option B (Full Hydra-zen)**

**Why Full Hydra-zen is Right**:
- Scene configurations **are data**, not code
- Research and educational use cases need widget-level control
- Architectural consistency is important
- The SceneEngine refactor is actually minimal

**The benefits of full CLI control over scene configurations outweigh the small implementation complexity.**

**Ready to implement Option B with the SceneEngine refactor?** 🚀
