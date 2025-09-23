# ALGOViz Design Doc — Storyboard DSL v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0 - Hydra-zen First)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Complete rewrite for Widget Architecture v2.0 - hydra-zen first storyboard system)
**Supersedes:** planning/v1/ALGOViz_Design_Storyboard_DSL.md

---

## 1. Purpose (Updated for Hydra-zen First)

Define a **declarative DSL** for describing algorithm visualizations using **hydra-zen first storyboard configurations** as *Acts → Shots → Beats*. The DSL removes imperative scene sprawl, enables reuse across algorithm types, and serves as the bridge between **data (VizEvents)** and **presentation (multi-level widgets)** through hydra-zen structured config event binding and ConfigStore-based template composition.

## 2. Non‑Goals
- Rendering specifics of Manim objects (left to Director & Widgets)
- Voice synthesis specifics (Voiceover doc)
- Algorithm semantics (Adapters & VizEvents doc)
- Widget-specific event handling (Scene Configuration handles this)

## 3. Requirements (Enhanced for Hydra-zen)
- **Hydra-zen First**: All storyboard components use structured configs and ConfigStore
- **Template System**: Reusable storyboard templates via ConfigStore groups
- Human‑readable YAML/JSON with hydra-zen composition syntax
- Minimal surface area: each **Beat** is one *action* + *args*
- Optional **narration** and **bookmarks** per Beat
- **Generic actions only** in core DSL - algorithm-specific actions via hydra-zen scene configurations
- **Configuration Composition**: Support for storyboard template inheritance and overrides

## 4. Core Concepts & Schema (Hydra-zen First)

### 4.1 Types (Python with Complete Hydra-zen Integration)
```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from hydra_zen import builds, make_config, instantiate
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig

@dataclass
class Beat:
    action: str
    args: dict[str, Any] = field(default_factory=dict)

    # Voiceover
    narration: str | None = None
    bookmarks: dict[str, str] = field(default_factory=dict)  # literal_word -> action_name

    # Timing overrides (optional)
    min_duration: float | None = None
    max_duration: float | None = None

@dataclass
class Shot:
    beats: list[Beat]

@dataclass
class Act:
    title: str
    shots: list[Shot]

@dataclass
class Storyboard:
    acts: list[Act]

# Enhanced hydra-zen structured configs for storyboard components
BeatConfigZen = builds(
    Beat,
    action="${beat.action}",
    args="${beat.args:{}}",
    narration="${beat.narration:null}",
    bookmarks="${beat.bookmarks:{}}",
    min_duration="${beat.min_duration:null}",
    max_duration="${beat.max_duration:null}",
    zen_partial=True,
    populate_full_signature=True
)

ShotConfigZen = builds(
    Shot,
    beats="${shot.beats:[]}",
    zen_partial=True,
    populate_full_signature=True
)

ActConfigZen = builds(
    Act,
    title="${act.title}",
    shots="${act.shots:[]}",
    zen_partial=True,
    populate_full_signature=True
)

StoryboardConfigZen = builds(
    Storyboard,
    acts="${storyboard.acts:[]}",
    zen_partial=True,
    populate_full_signature=True
)

# Storyboard template configurations using make_config
IntroActConfigZen = make_config(
    title="Introduction",
    shots=[
        builds(Shot,
              beats=[
                  builds(Beat, action="show_title", args={"text": "${title}", "subtitle": "${subtitle}"}, narration="${intro.narration}"),
                  builds(Beat, action="show_widgets", args={"${widget_names}"}, narration="Here is our visualization setup.")
              ])
    ],
    hydra_defaults=["_self_"]
)

SetupActConfigZen = make_config(
    title="Setup", 
    shots=[
        builds(Shot,
              beats=[
                  builds(Beat, action="place_start", args={"pos": "${scenario.start}"}, narration="We start from ${start_description}."),
                  builds(Beat, action="place_goal", args={"pos": "${scenario.goal}"}, narration="Our goal is ${goal_description}.")
              ])
    ],
    hydra_defaults=["_self_"]
)

AlgorithmActConfigZen = make_config(
    title="Algorithm Execution",
    shots=[
        builds(Shot,
              beats=[
                  builds(Beat, 
                        action="play_events", 
                        args={"algorithm": "${algorithm}", "scene": "${scene_config}"}, 
                        narration="${algorithm_description}",
                        bookmarks="${algorithm_bookmarks:{}}")
              ])
    ],
    hydra_defaults=["_self_"]
)

ResultsActConfigZen = make_config(
    title="Results",
    shots=[
        builds(Shot,
              beats=[
                  builds(Beat, action="trace_path", narration="Here is the ${result_type} we discovered."),
                  builds(Beat, action="outro", args={"text": "${outro_text:Thank you for watching}"})
              ])
    ],
    hydra_defaults=["_self_"]
)
```

### 4.2 ConfigStore Registration for Storyboard Templates
```python
def register_storyboard_configs():
    """Register all storyboard structured configs with ConfigStore."""
    cs = ConfigStore.instance()
    
    # Register base storyboard components
    cs.store(name="beat_base", node=BeatConfigZen)
    cs.store(name="shot_base", node=ShotConfigZen)
    cs.store(name="act_base", node=ActConfigZen)
    cs.store(name="storyboard_base", node=StoryboardConfigZen)
    
    # Register act templates
    cs.store(group="act", name="intro", node=IntroActConfigZen)
    cs.store(group="act", name="setup", node=SetupActConfigZen)
    cs.store(group="act", name="algorithm", node=AlgorithmActConfigZen)
    cs.store(group="act", name="results", node=ResultsActConfigZen)
    
    # Register complete storyboard templates
    cs.store(group="storyboard", name="pathfinding_template", node=make_config(
        acts=[
            IntroActConfigZen,
            SetupActConfigZen, 
            AlgorithmActConfigZen,
            ResultsActConfigZen
        ],
        defaults={
            "title": "Pathfinding Algorithm",
            "subtitle": "Graph Traversal Visualization",
            "algorithm": "bfs",
            "scene_config": "bfs_pathfinding",
            "widget_names": {"grid": True, "queue": True, "legend": True},
            "start_description": "the top-left corner",
            "goal_description": "the bottom-right corner", 
            "algorithm_description": "We explore nodes level by level until we reach the goal.",
            "result_type": "shortest path"
        },
        hydra_defaults=["_self_"]
    ))
    
    cs.store(group="storyboard", name="sorting_template", node=make_config(
        acts=[
            IntroActConfigZen,
            builds(Act, title="Setup", shots=[
                builds(Shot, beats=[
                    builds(Beat, action="setup_array", args={"size": "${array.size:10}", "values": "${array.values:random}"})
                ])
            ]),
            AlgorithmActConfigZen,
            ResultsActConfigZen
        ],
        defaults={
            "title": "Sorting Algorithm",
            "subtitle": "Array Sorting Visualization", 
            "algorithm": "quicksort",
            "scene_config": "quicksort",
            "widget_names": {"array": True, "call_stack": True},
            "algorithm_description": "We partition and sort the array recursively.",
            "result_type": "sorted array"
        },
        hydra_defaults=["_self_"]
    ))
    
    # Register beat templates for common actions
    cs.store(group="beat", name="show_title", node=builds(
        Beat,
        action="show_title",
        args={"text": "${title}", "subtitle": "${subtitle}"},
        narration="${title_narration}",
        zen_partial=True
    ))
    
    cs.store(group="beat", name="show_widgets", node=builds(
        Beat,
        action="show_widgets", 
        args="${widget_config}",
        narration="Here is our visualization setup.",
        zen_partial=True
    ))
    
    cs.store(group="beat", name="play_events", node=builds(
        Beat,
        action="play_events",
        args={"algorithm": "${algorithm}", "scene": "${scene_config}"},
        narration="${algorithm_narration}",
        bookmarks="${algorithm_bookmarks:{}}",
        zen_partial=True
    ))
```

### 4.3 Hydra Configuration Files for Storyboards
```yaml
# config/storyboard/bfs_demo.yaml
# @package _global_
defaults:
  - storyboard: pathfinding_template
  - _self_

# Override template defaults
title: "Breadth-First Search"
subtitle: "Graph Traversal Algorithm"
algorithm: "bfs"
scene_config: "bfs_pathfinding"
intro:
            narration: "This video explains Breadth-First Search."
widget_names:
  grid: true
  queue: true
  legend: true
start_description: "the top-left corner"
goal_description: "the bottom-right corner"
algorithm_description: "We explore nodes level by level until we reach the goal."
algorithm_bookmarks:
  enqueue: "queue.add_element"
  dequeue: "queue.remove_element" 
  goal: "grid.mark_goal"
result_type: "shortest path"
outro_text: "BFS guarantees the shortest path!"
```

```yaml
# config/storyboard/quicksort_demo.yaml
# @package _global_
defaults:
  - storyboard: sorting_template
  - _self_

# Override template defaults
title: "QuickSort Algorithm"
subtitle: "Divide and Conquer Sorting"
algorithm: "quicksort"
scene_config: "quicksort"
widget_names:
  array: true
  call_stack: true
array:
  size: 12
  values: "random"
algorithm_description: "We partition around a pivot and sort recursively."
algorithm_bookmarks:
  compare: "array.compare_highlight"
  swap: "array.swap_elements"
  partition: "array.partition_marker"
result_type: "sorted array"
outro_text: "QuickSort is efficient on average!"
```

## 5. Core Actions (Updated - Generic Only)

### 5.1 Generic Orchestration Actions
| Action | Description | Expected Args |
|---|---|---|
| `show_title` | Show title card | `text: str`, `subtitle: str` |
| `show_widgets` | Show widgets from scene config | widget names: `queue: true`, `grid: true` |
| `play_events` | Stream adapter events via scene routing | `algorithm: str`, `scene: str` |
| `outro` | Fade out/credits | `text: str` (optional) |

### 5.2 Removed Algorithm-Specific Actions
**No longer in core actions (moved to scene configurations):**
- ❌ `place_start` - Now in PathfindingSceneConfig via hydra-zen
- ❌ `place_goal` - Now in PathfindingSceneConfig via hydra-zen
- ❌ `setup_array` - Now in SortingSceneConfig via hydra-zen
- ❌ `trace_path` - Now resolved via scene configuration templates

These actions are now **resolved through scene configurations** using hydra-zen instantiation, making the core DSL truly generic while maintaining algorithm-specific functionality.

## 5.3 Architectural Separation: Storyboards vs Scene Configs

### **Key Architectural Principle: Generic Storyboards + Algorithm-Specific Scene Configs**

The Storyboard DSL v2.0 establishes a clear separation of concerns between storyboard orchestration and algorithm-specific behavior:

**Storyboard Responsibilities (Generic Orchestration):**
- ✅ **Narrative Structure**: Acts, shots, and beats for story flow
- ✅ **Generic Actions**: show_title, show_widgets, play_events, outro
- ✅ **Timing Control**: Duration, narration, bookmarks
- ✅ **Template Composition**: Reusable storyboard templates via ConfigStore

**Scene Configuration Responsibilities (Algorithm-Specific Behavior):**
- ✅ **Widget Configuration**: Which widgets exist and their properties
- ✅ **Event Bindings**: How algorithm events map to widget actions
- ✅ **Parameter Resolution**: Dynamic parameter resolution using OmegaConf resolvers
- ✅ **Algorithm-Specific Actions**: Custom actions for specific algorithms

**The Flow:**
1. **Storyboard**: Defines narrative structure with generic actions
2. **play_events Action**: Routes to SceneEngine with algorithm and scene config
3. **SceneEngine**: Handles algorithm-specific event processing and parameter resolution
4. **Widget Actions**: Called with resolved parameters from event data

**Benefits:**
- ✅ **Generic Storyboards**: Reusable across different algorithm types
- ✅ **Algorithm-Specific Scene Configs**: Tailored behavior for each algorithm
- ✅ **Clear Separation**: Orchestration vs algorithm-specific behavior
- ✅ **Hydra-zen First**: Both storyboards and scene configs use structured configs
- ✅ **Maintainability**: Single responsibility for each component

**Example:**
```yaml
# Storyboard (Generic)
- action: play_events
  args:
    algorithm: "bfs"
    scene: "bfs_pathfinding"
  narration: "Let's explore the maze with BFS"

# Scene Config (Algorithm-Specific)
event_bindings:
  enqueue:
    - widget: "queue"
      action: "add_element"
      params:
        element: "${event.node}"
```

## 6. Storyboard Loading and Instantiation (Hydra-zen Native)

### 6.1 Hydra-zen Storyboard Loader
```python
from hydra_zen import instantiate
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf
import hydra

class StoryboardLoader:
    """Loads storyboards using hydra-zen configuration system."""
    
    def __init__(self):
        self.cs = ConfigStore.instance()
        # Register all storyboard configs
        register_storyboard_configs()
    
    @hydra.main(version_base=None, config_path="config/storyboard", config_name="bfs_demo")
    def load_with_hydra(self, cfg: DictConfig) -> Storyboard:
        """Load storyboard using Hydra's composition system."""
        # Instantiate storyboard from structured config
        storyboard = instantiate(cfg)
        
        # Validate and return
        if not isinstance(storyboard, Storyboard):
            storyboard = Storyboard(**OmegaConf.to_container(cfg, resolve=True))
        
        return storyboard
    
    def load_from_template(self, template_name: str, **overrides) -> Storyboard:
        """Load storyboard from ConfigStore template with overrides."""
        config_key = f"storyboard/{template_name}"
        
        repo = self.cs.get_repo()
        if config_key not in repo:
            raise ValueError(f"Storyboard template '{template_name}' not found")
        
        storyboard_config = repo[config_key].node
        
        # Apply overrides if provided
        if overrides:
            override_config = OmegaConf.create(overrides)
            storyboard_config = OmegaConf.merge(storyboard_config, override_config)
        
        # Instantiate using hydra-zen
        return instantiate(storyboard_config)
    
    def create_custom_storyboard(self, acts_config: List[DictConfig]) -> Storyboard:
        """Create custom storyboard from act configurations."""
        acts = []
        for act_config in acts_config:
            act = instantiate(act_config)
            acts.append(act)
        
        return Storyboard(acts=acts)
    
    def get_available_templates(self) -> Dict[str, str]:
        """Get all available storyboard templates from ConfigStore."""
        repo = self.cs.get_repo()
        templates = {}
        
        for config_name in repo:
            if config_name.startswith("storyboard/"):
                template_name = config_name[11:]  # Remove "storyboard/" prefix
                templates[template_name] = config_name
        
        return templates
```

### 6.2 Enhanced YAML Loading with Composition
```python
def load_storyboard_yaml(yaml_path: str, config_overrides: Dict = None) -> Storyboard:
    """Load storyboard YAML with hydra-zen composition support."""
    # Load base configuration
    cfg = OmegaConf.load(yaml_path)
    
    # Apply overrides if provided
    if config_overrides:
        override_cfg = OmegaConf.create(config_overrides)
        cfg = OmegaConf.merge(cfg, override_cfg)
    
    # Resolve any interpolations
    cfg = OmegaConf.to_container(cfg, resolve=True)
    
    # Create storyboard using structured configs
    loader = StoryboardLoader()
    
    # If it references a template, use that
    if 'storyboard_template' in cfg:
        template_name = cfg['storyboard_template']
        return loader.load_from_template(template_name, **cfg)
    else:
        # Create from direct configuration
        storyboard_cfg = OmegaConf.create(cfg)
        return instantiate(StoryboardConfigZen, **storyboard_cfg)

# Usage examples
def load_bfs_storyboard():
    """Load BFS storyboard using template."""
    loader = StoryboardLoader()
    return loader.load_from_template("pathfinding_template", 
                                   algorithm="bfs",
                                   scene_config="bfs_pathfinding",
                                   title="Breadth-First Search")

def load_custom_storyboard():
    """Load custom storyboard with specific acts."""
    loader = StoryboardLoader()
    
    custom_acts = [
        instantiate(IntroActConfigZen, title="Custom Algorithm", subtitle="My Visualization"),
        instantiate(AlgorithmActConfigZen, algorithm="custom", scene_config="custom_scene"),
        instantiate(ResultsActConfigZen, result_type="custom result")
    ]
    
    return loader.create_custom_storyboard(custom_acts)
```

## 7. Action Resolution (Updated for Hydra-zen Scene Integration)

### 7.1 Enhanced Action Resolution with Scene Configurations
```python
class ActionResolver:
    """Resolves actions through core registry and hydra-zen scene configurations."""
    
    def __init__(self, scene_engine):
        self.scene_engine = scene_engine
        self.core_actions = {
            "show_title": self._action_show_title,
            "show_widgets": self._action_show_widgets,
            "play_events": self._action_play_events,
            "outro": self._action_outro
        }
    
    def resolve_action(self, beat: Beat, context: Dict) -> callable:
        """Resolve action through core registry or scene configuration."""
        
        # 1. Check core actions first
        if beat.action in self.core_actions:
            return self.core_actions[beat.action]
        
        # 2. Check scene configuration actions (SceneEngine handles algorithm-specific actions)
        if self.scene_engine.has_action(beat.action):
            return lambda scene, args, run_time, ctx: \
                self.scene_engine.execute_action(beat.action, args, run_time, ctx)
        
        # 3. Check if it's a configurable action template
        if self._is_template_action(beat.action):
            return self._resolve_template_action(beat.action, beat.args, context)
        
        raise ValueError(f"Unknown action '{beat.action}'. Available actions: {self._get_available_actions()}")
    
    def _is_template_action(self, action_name: str) -> bool:
        """Check if action is available as a template in ConfigStore."""
        cs = ConfigStore.instance()
        repo = cs.get_repo()
        return f"beat/{action_name}" in repo
    
    def _resolve_template_action(self, action_name: str, args: Dict, context: Dict) -> callable:
        """Resolve action from ConfigStore template."""
        cs = ConfigStore.instance()
        beat_config = cs.get_repo()[f"beat/{action_name}"].node
        
        # Merge args with template
        resolved_config = OmegaConf.merge(beat_config, OmegaConf.create({"args": args}))
        
        # Instantiate beat and return action resolver
        beat = instantiate(resolved_config, **context)
        return self.resolve_action(beat, context)
```

## 8. Validation & Loading (Enhanced for Hydra-zen)

### 8.1 Hydra-zen Aware Validation
```python
class StoryboardValidator:
    """Validates storyboards with hydra-zen scene configuration integration."""
    
    def __init__(self, scene_config: DictConfig):
        self.scene_config = scene_config
        self.cs = ConfigStore.instance()
    
    def validate_storyboard(self, storyboard: Storyboard) -> List[str]:
        """Validate storyboard against scene configuration and ConfigStore."""
        errors = []
        
        for act_idx, act in enumerate(storyboard.acts):
            for shot_idx, shot in enumerate(act.shots):
                for beat_idx, beat in enumerate(shot.beats):
                    try:
                        self.validate_beat(beat)
                    except ValueError as e:
                        location = f"Act {act_idx}/Shot {shot_idx}/Beat {beat_idx}"
                        errors.append(f"{location}: {e}")
        
        return errors
    
    def validate_beat(self, beat: Beat):
        """Validate beat action against available actions and templates."""
        core_actions = ["show_title", "show_widgets", "play_events", "outro"]
        
        # Check core actions (storyboard handles generic actions only)
        if beat.action in core_actions:
            return
        
        # Check scene configuration actions (SceneEngine handles algorithm-specific actions)
        if hasattr(self.scene_config, 'event_bindings'):
            scene_actions = list(self.scene_config.event_bindings.keys())
            if beat.action in scene_actions:
                return
        
        # Check ConfigStore beat templates
        repo = self.cs.get_repo()
        if f"beat/{beat.action}" in repo:
            return
        
        # Action not found
        available_actions = core_actions + self._get_scene_actions() + self._get_template_actions()
        raise ValueError(f"Unknown action '{beat.action}'. Available: {available_actions}")
    
    def _get_scene_actions(self) -> List[str]:
        """Get actions available from scene configuration."""
        if hasattr(self.scene_config, 'event_bindings'):
            return list(self.scene_config.event_bindings.keys())
        return []
    
    def _get_template_actions(self) -> List[str]:
        """Get actions available from ConfigStore templates."""
        repo = self.cs.get_repo()
        template_actions = []
        
        for config_name in repo:
            if config_name.startswith("beat/"):
                action_name = config_name[5:]  # Remove "beat/" prefix
                template_actions.append(action_name)
        
        return template_actions
    
    def validate_template_compatibility(self, template_name: str, overrides: Dict) -> List[str]:
        """Validate that template overrides are compatible."""
        errors = []
        
        config_key = f"storyboard/{template_name}"
        repo = self.cs.get_repo()
        
        if config_key not in repo:
            errors.append(f"Template '{template_name}' not found in ConfigStore")
            return errors
        
        template_config = repo[config_key].node
        
        # Validate override keys exist in template
        for override_key in overrides.keys():
            if not self._key_exists_in_config(override_key, template_config):
                errors.append(f"Override key '{override_key}' not found in template '{template_name}'")
        
        return errors
    
    def _key_exists_in_config(self, key: str, config) -> bool:
        """Check if key exists in structured config (supports nested keys)."""
        try:
            keys = key.split('.')
            current = config
            for k in keys:
                if hasattr(current, k):
                    current = getattr(current, k)
                else:
                    return False
            return True
        except:
            return False
```

## 9. Examples (Enhanced for Hydra-zen)

### 9.1 Template-Based Storyboard Creation
```python
# Using ConfigStore templates
def create_algorithm_storyboard(algorithm: str, scene_config: str, **customizations):
    """Create storyboard from template with customizations."""
    loader = StoryboardLoader()
    
    if algorithm in ["bfs", "dfs", "dijkstra", "astar"]:
        template = "pathfinding_template"
    elif algorithm in ["quicksort", "mergesort", "heapsort"]:
        template = "sorting_template"
    else:
        template = "generic_template"
    
    return loader.load_from_template(
        template,
        algorithm=algorithm,
        scene_config=scene_config,
        **customizations
    )

# Usage examples
bfs_storyboard = create_algorithm_storyboard(
    "bfs", 
    "bfs_pathfinding",
    title="BFS Visualization",
    algorithm_description="We explore nodes level by level."
)

quicksort_storyboard = create_algorithm_storyboard(
    "quicksort",
    "quicksort", 
    title="QuickSort Demo",
    array={"size": 15, "values": "ascending"}
)
```

### 9.2 Dynamic Storyboard Composition
```python
def create_comparison_storyboard(algorithms: List[str], scene_configs: List[str]):
    """Create storyboard comparing multiple algorithms."""
    loader = StoryboardLoader()
    
    acts = [
        instantiate(IntroActConfigZen, 
                   title="Algorithm Comparison",
                   subtitle="Side-by-side Analysis")
    ]
    
    for i, (algorithm, scene_config) in enumerate(zip(algorithms, scene_configs)):
        acts.append(
            instantiate(ActConfigZen,
                       title=f"Algorithm {i+1}: {algorithm.upper()}",
                       shots=[
                           instantiate(ShotConfigZen,
                                     beats=[
                                         instantiate(BeatConfigZen,
                                                   action="play_events",
                                                   args={"algorithm": algorithm, "scene": scene_config},
                                                   narration=f"Now let's see how {algorithm} performs.")
                                     ])
                       ])
        )
    
    acts.append(
        instantiate(ResultsActConfigZen,
                   title="Comparison Results", 
                   result_type="performance comparison")
    )
    
    return loader.create_custom_storyboard(acts)
```

## 9.5 The `play_events` Action: Bridge Between Storyboards and Scene Configs

### **How Generic Storyboards Connect to Algorithm-Specific Behavior**

The `play_events` action is the key bridge that connects generic storyboards to algorithm-specific scene configurations:

**Storyboard Side (Generic):**
```yaml
- action: play_events
  args:
    algorithm: "bfs"           # Which algorithm to run
    scene: "bfs_pathfinding"   # Which scene config to use
  narration: "Let's explore the maze with BFS"
```

**Scene Config Side (Algorithm-Specific):**
```yaml
# bfs_pathfinding.yaml
event_bindings:
  enqueue:
    - widget: "queue"
      action: "add_element"
      params:
        element: "${event.node}"  # Dynamic parameter from algorithm
  node_visited:
    - widget: "grid"
      action: "highlight_cell"
      params:
        position: "${event.position}"
        style: "visited"
```

**The Flow:**
1. **Storyboard**: Defines `play_events` action with algorithm and scene config
2. **Director**: Receives the action and gets the algorithm adapter
3. **Algorithm Adapter**: Generates VizEvents with dynamic data
4. **SceneEngine**: Uses scene config to route events to widgets with parameter resolution
5. **Widgets**: Receive resolved parameters and execute actions

**Benefits:**
- ✅ **Generic Storyboards**: Same storyboard structure works for any algorithm
- ✅ **Algorithm-Specific Behavior**: Scene configs handle algorithm-specific event processing
- ✅ **Dynamic Parameters**: Event data resolved at runtime with full context
- ✅ **Clear Separation**: Orchestration vs algorithm-specific behavior
- ✅ **Reusability**: Storyboard templates work across different algorithms

**Example: Same Storyboard, Different Algorithms**
```yaml
# Generic storyboard template
- action: play_events
  args:
    algorithm: "${algorithm}"      # Resolved at runtime
    scene: "${scene_config}"       # Resolved at runtime
  narration: "${algorithm_description}"

# Used for BFS
algorithm: "bfs"
scene_config: "bfs_pathfinding"
algorithm_description: "We explore nodes level by level"

# Used for DFS  
algorithm: "dfs"
scene_config: "dfs_pathfinding"
algorithm_description: "We explore as deep as possible first"
```

## 10. CLI Integration (Hydra-zen Native)

### 10.1 Storyboard CLI Commands
```bash
# List available storyboard templates
agloviz storyboard list-templates

# Create storyboard from template
agloviz storyboard create --template pathfinding_template --algorithm bfs --output bfs_demo.yaml

# Validate storyboard configuration
agloviz storyboard validate bfs_demo.yaml --scene bfs_pathfinding

# Run storyboard with overrides
agloviz render --storyboard pathfinding_template --algorithm dfs --scene dfs_pathfinding
```

### 10.2 CLI Implementation
```python
import click
from hydra_zen import instantiate

@click.group()
def storyboard():
    """Storyboard management commands."""
    pass

@storyboard.command()
def list_templates():
    """List available storyboard templates."""
    loader = StoryboardLoader()
    templates = loader.get_available_templates()
    
    click.echo("Available storyboard templates:")
    for template_name, config_path in templates.items():
        click.echo(f"  - {template_name} ({config_path})")

@storyboard.command()
@click.option('--template', required=True, help='Template name')
@click.option('--algorithm', required=True, help='Algorithm name')
@click.option('--output', required=True, help='Output YAML file')
@click.option('--scene', help='Scene configuration name')
def create(template, algorithm, output, scene):
    """Create storyboard from template."""
    loader = StoryboardLoader()
    
    overrides = {"algorithm": algorithm}
    if scene:
        overrides["scene_config"] = scene
    
    try:
        storyboard = loader.load_from_template(template, **overrides)
        
        # Convert to YAML and save
        storyboard_dict = OmegaConf.structured(storyboard)
        with open(output, 'w') as f:
            OmegaConf.save(storyboard_dict, f)
        
        click.echo(f"Created storyboard: {output}")
        
    except Exception as e:
        click.echo(f"Error creating storyboard: {e}", err=True)

@storyboard.command()
@click.argument('storyboard_file')
@click.option('--scene', help='Scene configuration for validation')
def validate(storyboard_file, scene):
    """Validate storyboard configuration."""
    try:
        # Load storyboard
        storyboard = load_storyboard_yaml(storyboard_file)
        
        # Load scene config if provided
        scene_config = None
        if scene:
            from agloviz.core.scene import create_scene_from_config_store
            scene_engine = create_scene_from_config_store(scene)
            scene_config = scene_engine.get_scene_config()
        
        # Validate
        if scene_config:
            validator = StoryboardValidator(scene_config)
            errors = validator.validate_storyboard(storyboard)
            
            if errors:
                click.echo("Validation errors found:")
                for error in errors:
                    click.echo(f"  - {error}")
            else:
                click.echo("Storyboard validation passed!")
        else:
            click.echo("Basic storyboard structure validation passed!")
            
    except Exception as e:
        click.echo(f"Validation failed: {e}", err=True)
```

## 11. Testing (Enhanced for Hydra-zen)

### 11.1 Template and ConfigStore Testing
```python
def test_storyboard_template_instantiation():
    """Test that storyboard templates instantiate correctly."""
    register_storyboard_configs()
    cs = ConfigStore.instance()
    
    # Test pathfinding template
    pathfinding_config = cs.get_repo()["storyboard/pathfinding_template"].node
    storyboard = instantiate(pathfinding_config)
    
    assert isinstance(storyboard, Storyboard)
    assert len(storyboard.acts) >= 3  # Intro, setup, algorithm, results
    assert storyboard.acts[0].title == "Introduction"

def test_storyboard_template_overrides():
    """Test template overrides work correctly."""
    loader = StoryboardLoader()
    
    storyboard = loader.load_from_template(
        "pathfinding_template",
        algorithm="dfs",
        title="DFS Custom Title",
        scene_config="dfs_pathfinding"
    )
    
    # Check overrides were applied
    play_events_beat = None
        for act in storyboard.acts:
            for shot in act.shots:
                for beat in shot.beats:
                if beat.action == "play_events":
                    play_events_beat = beat
                    break
    
    assert play_events_beat is not None
    assert play_events_beat.args["algorithm"] == "dfs"
    assert play_events_beat.args["scene"] == "dfs_pathfinding"

def test_configstore_template_discovery():
    """Test ConfigStore template discovery works."""
    loader = StoryboardLoader()
    templates = loader.get_available_templates()
    
    assert "pathfinding_template" in templates
    assert "sorting_template" in templates
    assert len(templates) >= 2

def test_hydra_composition_loading():
    """Test loading storyboard via Hydra composition."""
    # This would test actual Hydra config file loading
    # with defaults and overrides
    pass
```

## 12. Migration Strategy

### 12.1 Phase 1: Template System Implementation
**Goal**: Implement ConfigStore-based storyboard template system

**Tasks**:
1. Create structured configs for all storyboard components
2. Register templates with ConfigStore using appropriate groups
3. Implement StoryboardLoader with template support
4. Add CLI commands for template management

### 12.2 Phase 2: YAML Composition Enhancement
**Goal**: Update YAML loading to use hydra-zen composition

**Tasks**:
1. Update YAML files to use Hydra composition syntax
2. Add template references and overrides to existing storyboards
3. Implement parameter interpolation in storyboard configs
4. Test template inheritance and customization

### 12.3 Phase 3: Integration Testing
**Goal**: Validate complete hydra-zen storyboard system

**Tasks**:
1. Test template instantiation and customization
2. Validate scene configuration integration
3. Test CLI template management commands
4. Performance testing of hydra-zen composition

## 13. Success Criteria

### 13.1 Hydra-zen Integration Success
- ✅ All storyboard components use structured configs with `builds()` patterns
- ✅ ConfigStore registration works for storyboard templates and components
- ✅ Template system supports inheritance and customization
- ✅ YAML loading uses hydra-zen composition syntax
- ✅ CLI integration supports template management and validation

### 13.2 Template System Quality
- ✅ Reusable templates for common storyboard patterns
- ✅ Easy customization through parameter overrides
- ✅ Template discovery and validation
- ✅ Integration with scene configuration system
- ✅ Performance maintained with structured config instantiation

---

## Summary

This Storyboard DSL v2.0 document defines a complete hydra-zen first storyboard system that seamlessly integrates with the Configuration System, DI Strategy, and Widget Architecture. The storyboard system features:

1. **Hydra-zen Native Configuration**: All storyboard components use `builds()` and structured configs
2. **ConfigStore Template System**: Reusable storyboard templates with inheritance and customization
3. **Enhanced YAML Composition**: Hydra-zen composition syntax with parameter interpolation
4. **Generic Storyboard Actions**: Core DSL uses generic actions only (show_title, show_widgets, play_events, outro)
5. **Scene Configuration Integration**: Algorithm-specific behavior handled by scene configs, not storyboards
6. **CLI Template Management**: Complete CLI support for template discovery, creation, and validation

**Key Architectural Principle**: Storyboards handle generic orchestration while scene configurations handle algorithm-specific behavior. The `play_events` action serves as the bridge between generic storyboards and algorithm-specific scene configs.

The implementation provides a world-class, extensible storyboard system that supports any algorithm type while maintaining the high engineering standards established in the ALGOViz project vision.
