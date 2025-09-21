# ALGOViz Design Doc — Storyboard DSL v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Complete rewrite for Widget Architecture v2.0 - generic actions with scene configuration)
**Supersedes:** planning/v1/ALGOViz_Design_Storyboard_DSL.md

---

## 1. Purpose (Updated for v2.0)

Define a **declarative DSL** for describing algorithm visualizations using scene configurations as *Acts → Shots → Beats*. The DSL removes imperative scene sprawl, enables reuse across algorithm types, and serves as the bridge between **data (VizEvents)** and **presentation (multi-level widgets)** through configuration-driven event binding.

## 2. Non‑Goals
- Rendering specifics of Manim objects (left to Director & Widgets)
- Voice synthesis specifics (Voiceover doc)
- Algorithm semantics (Adapters & VizEvents doc)
- Widget-specific event handling (Scene Configuration handles this)

## 3. Requirements
- Human‑readable YAML/JSON with strict validation
- Minimal surface area: each **Beat** is one *action* + *args*
- Optional **narration** and **bookmarks** per Beat
- **Generic actions only** in core DSL - algorithm-specific actions via scene configurations
- Forward‑compatible for future actions

## 4. Core Concepts & Schema

### 4.1 Types (Python)
```python
from dataclasses import dataclass, field
from typing import Any

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
```

### 4.2 YAML Example (Updated for v2.0)
```yaml
acts:
  - title: "Intro"
    shots:
      - beats:
          - action: show_title
            args: {text: "Breadth-First Search", subtitle: "Graph Traversal Algorithm"}
            narration: "This video explains Breadth-First Search."
          - action: show_widgets
            args: {grid: true, queue: true, hud: true}
            narration: "Here is our visualization setup."
  - title: "Setup"
    shots:
      - beats:
          - action: place_start
            args: {pos: [0, 0]}
            narration: "We start from the top-left corner."
          - action: place_goal
            args: {pos: [9, 9]}
            narration: "Our goal is the bottom-right corner."
  - title: "Algorithm Execution"
    shots:
      - beats:
          - action: play_events
            args: {algorithm: "bfs", scene_config: "pathfinding.bfs"}
            narration: "We explore nodes level by level until we reach the goal."
            bookmarks:
              enqueue: "queue.highlight_frontier"
              dequeue: "queue.highlight_head"
              goal: "grid.flash_goal"
  - title: "Results"
    shots:
      - beats:
          - action: trace_path
            narration: "Here is the shortest path we discovered."
          - action: outro
```

## 5. Core Actions (Updated - Generic Only)

### 5.1 Generic Orchestration Actions
| Action | Description | Expected Args |
|---|---|---|
| `show_title` | Show title card | `text: str`, `subtitle: str` |
| `show_widgets` | Show widgets from scene config | widget names: `queue: true`, `grid: true` |
| `play_events` | Stream adapter events via scene routing | `routing_override: dict` (optional) |
| `outro` | Fade out/credits | `text: str` (optional) |

### 5.2 Removed Algorithm-Specific Actions
**No longer in core actions (moved to scene configurations):**
- ❌ `place_start` - Now in PathfindingSceneConfig
- ❌ `place_goal` - Now in PathfindingSceneConfig
- ❌ `place_obstacles` - Now in PathfindingSceneConfig
- ❌ `show_complexity` - Now in AlgorithmAnalysisSceneConfig
- ❌ `celebrate_goal` - Now in PathfindingSceneConfig

### 5.3 Action Resolution Process
1. Check if action is core generic action
2. If not, resolve through scene configuration
3. Scene configuration provides action implementation
4. Parameter templates resolve event data

```python
def resolve_action(action_name: str, scene_config: SceneConfig) -> Callable:
    """Resolve action through core registry or scene configuration."""
    
    # Core actions (generic orchestration)
    core_actions = ["show_title", "show_widgets", "play_events", "outro"]
    
    if action_name in core_actions:
        return get_core_action_handler(action_name)
    
    # Scene configuration actions (algorithm-specific)
    if action_name in scene_config.action_handlers:
        return scene_config.action_handlers[action_name]
    
    raise ValueError(f"Unknown action: {action_name}")
```

## 6. Scene Configuration Actions (New Section)

### 6.1 Algorithm-Specific Actions in Scene Configs
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
                    scene_engine.get_widget("grid").mark_goal(args["pos"]),
                "place_obstacles": lambda scene, args, run_time, context:
                    [scene_engine.get_widget("grid").mark_obstacle(pos) for pos in args["positions"]],
                "celebrate_goal": lambda scene, args, run_time, context:
                    scene_engine.get_widget("grid").highlight_element(args["pos"], "celebration")
            },
            event_bindings={
                "enqueue": [
                    EventBinding(widget="queue", action="enqueue", params={"element": "${event.node}"})
                ]
            }
        )

class SortingSceneConfig(BaseModel):
    @staticmethod
    def create() -> SceneConfig:
        return SceneConfig(
            action_handlers={
                "setup_array": lambda scene, args, run_time, context:
                    scene_engine.get_widget("array").initialize_elements(args["values"]),
                "show_comparison": lambda scene, args, run_time, context:
                    scene_engine.get_widget("array").compare_elements(args["i"], args["j"], args["result"])
            }
        )
```

### 6.2 Domain-Specific Action Examples
- **Pathfinding**: `place_start`, `place_goal`, `place_obstacles`, `celebrate_goal`
- **Sorting**: `setup_array`, `show_comparison`, `swap_elements`, `show_sorted`
- **Trees**: `highlight_node`, `show_path`, `traverse_subtree`

### 6.3 Event Binding Integration
Scene configurations also handle event binding for `play_events` action.

```python
# Event bindings in scene configuration
event_bindings = {
    "enqueue": [
        EventBinding(widget="queue", action="enqueue", params={"element": "${event.node}"}, order=1),
        EventBinding(widget="grid", action="highlight_element", params={"index": "${event.pos}", "style": "frontier"}, order=2)
    ],
    "dequeue": [
        EventBinding(widget="queue", action="dequeue", params={}, order=1)
    ]
}
```

## 7. Action Resolution (Updated for Scene Configuration)

### 7.1 Resolution Process
1. **Core Action Check**: Is action in Director's core actions?
2. **Scene Configuration Check**: Is action defined in scene configuration?
3. **Plugin Action Check**: Is action provided by loaded plugins?
4. **Error Handling**: Provide helpful error with available actions

```python
class ActionResolver:
    def __init__(self, director: Director, scene_engine: SceneEngine):
        self.director = director
        self.scene_engine = scene_engine
    
    def resolve(self, action_name: str) -> Callable:
        """Resolve action through hierarchy."""
        
        # 1. Core generic actions (highest priority)
        if action_name in self.director.core_actions:
            return self.director.core_actions[action_name]
        
        # 2. Scene configuration actions
        if self.scene_engine.has_action(action_name):
            return self.scene_engine.get_action_handler(action_name)
        
        # 3. Plugin-provided actions
        if self.director.registry.has_action(action_name):
            return self.director.registry.get_action(action_name)
        
        # 4. Error with helpful context
        available_actions = self.get_available_actions()
        raise ValueError(f"Unknown action '{action_name}'. Available: {available_actions}")
```

### 7.2 Priority Order
1. Core generic actions (highest priority)
2. Scene configuration actions
3. Plugin-provided actions
4. Error if not found

### 7.3 Parameter Resolution
- Static parameters passed directly
- Template parameters (`${event.pos}`) resolved at runtime
- Context parameters (act/shot/beat indices) available

```python
def resolve_beat_parameters(beat: Beat, context: dict) -> dict:
    """Resolve beat parameters including templates."""
    resolved_args = {}
    
    for key, value in beat.args.items():
        if isinstance(value, str) and value.startswith("${"):
            # Template parameter
            template_path = value[2:-1]  # Remove ${ and }
            resolved_args[key] = resolve_template_path(template_path, context)
        else:
            # Static parameter
            resolved_args[key] = value
    
    return resolved_args
```

## 8. Validation & Loading (Updated for v2.0)

- Pydantic models mirror the dataclasses (for runtime validation)
- Strict keys; unknown keys flag warnings (fail in CI)
- **Scene configuration validation**: Ensure referenced actions exist
- **Action availability check**: Verify all storyboard actions are resolvable
- Provide helpful error messages: include act/shot indexes for context

```python
class StoryboardValidator:
    def __init__(self, scene_config: SceneConfig):
        self.scene_config = scene_config
    
    def validate_storyboard(self, storyboard: Storyboard) -> list[str]:
        """Validate storyboard against scene configuration."""
        errors = []
        
        for act_idx, act in enumerate(storyboard.acts):
            for shot_idx, shot in enumerate(act.shots):
                for beat_idx, beat in enumerate(shot.beats):
                    try:
                        self.validate_beat_action(beat)
                    except ValueError as e:
                        location = f"Act {act_idx}/Shot {shot_idx}/Beat {beat_idx}"
                        errors.append(f"{location}: {e}")
        
        return errors
    
    def validate_beat_action(self, beat: Beat):
        """Validate that beat action is resolvable."""
        core_actions = ["show_title", "show_widgets", "play_events", "outro"]
        
        if beat.action not in core_actions:
            if beat.action not in self.scene_config.action_handlers:
                available = core_actions + list(self.scene_config.action_handlers.keys())
                raise ValueError(f"Unknown action '{beat.action}'. Available: {available}")
```

## 9. Examples (Updated for v2.0)

### 9.1 Generic Storyboard Examples
```yaml
# Generic storyboard structure (works with any algorithm)
acts:
  - title: "Introduction"
    shots:
      - beats:
          - action: show_title
            args: {text: "Algorithm Visualization"}
          - action: show_widgets
            args: {grid: true, queue: true}
  - title: "Execution"
    shots:
      - beats:
          - action: play_events
            args: {algorithm: "bfs", scene_config: "pathfinding.bfs"}
```

### 9.2 Scene Configuration Examples
```python
# Pathfinding scene configuration
PathfindingSceneConfig = SceneConfig(
    action_handlers={
        "place_start": pathfinding_place_start_handler,
        "place_goal": pathfinding_place_goal_handler,
        "celebrate_goal": pathfinding_celebrate_handler
    }
)

# Sorting scene configuration  
SortingSceneConfig = SceneConfig(
    action_handlers={
        "setup_array": sorting_setup_array_handler,
        "show_comparison": sorting_comparison_handler,
        "show_sorted": sorting_sorted_handler
    }
)
```

### 9.3 Multi-Algorithm Examples
```yaml
# Same storyboard structure works for different algorithms
acts:
  - title: "Setup"
    shots:
      - beats:
          - action: place_start    # Resolved via scene configuration
          - action: place_goal     # Resolved via scene configuration
  - title: "Algorithm"
    shots:
      - beats:
          - action: play_events
            args: 
              algorithm: "bfs"           # BFS with PathfindingSceneConfig
              scene_config: "pathfinding.bfs"
---
# Different algorithm, same storyboard structure
acts:
  - title: "Setup"
    shots:
      - beats:
          - action: setup_array    # Resolved via SortingSceneConfig
  - title: "Algorithm"  
    shots:
      - beats:
          - action: play_events
            args:
              algorithm: "quicksort"     # Quicksort with SortingSceneConfig
              scene_config: "sorting.quicksort"
```

## 10. Testing (Updated for v2.0)

- YAML schema tests (bad/missing/extra keys)
- Golden storyboards (snapshots) parsed ⇒ round-trip to dataclasses
- **Scene configuration integration tests**: Ensure action resolution works
- **Multi-algorithm tests**: Same storyboard structure with different scene configs
- Action contracts mocked; ensure Director calls with correct `run_time` and args
- Bookmarks: simulate "spoken words" and assert actions fire

```python
def test_storyboard_scene_configuration_integration():
    """Test storyboard works with scene configuration."""
    storyboard = load_storyboard("generic_pathfinding.yaml")
    scene_config = PathfindingSceneConfig.create()
    
    validator = StoryboardValidator(scene_config)
    errors = validator.validate_storyboard(storyboard)
    assert len(errors) == 0  # All actions should resolve

def test_multi_algorithm_storyboard():
    """Test same storyboard structure works with different algorithms."""
    base_storyboard = load_storyboard("generic_algorithm.yaml")
    
    # Test with pathfinding
    pathfinding_config = PathfindingSceneConfig.create()
    director_bfs = Director(scene, base_storyboard, timing, pathfinding_config)
    director_bfs.run()  # Should work
    
    # Test with sorting
    sorting_config = SortingSceneConfig.create()
    director_sort = Director(scene, base_storyboard, timing, sorting_config)
    director_sort.run()  # Should work with same storyboard
```

## 11. Performance

- Keep YAML small; prefer references to shared sequences if needed
- Pre-parse and memoize storyboards in CLI to avoid repeated parsing
- **Scene configuration caching**: Cache action resolution for performance
- **Template compilation**: Pre-compile parameter templates
- No heavy computation; this layer stays declarative

```python
class StoryboardOptimizer:
    def optimize_for_scene_config(self, storyboard: Storyboard, scene_config: SceneConfig):
        """Pre-optimize storyboard for scene configuration."""
        # Pre-resolve all action handlers
        for act in storyboard.acts:
            for shot in act.shots:
                for beat in shot.beats:
                    beat._resolved_handler = self.resolve_action(beat.action, scene_config)
```

## 12. Migration from v1.0

### 12.1 Removed Algorithm-Specific Actions
**Actions removed from core DSL (moved to scene configurations):**
- ❌ `place_start` - Now in PathfindingSceneConfig
- ❌ `place_goal` - Now in PathfindingSceneConfig
- ❌ `place_obstacles` - Now in PathfindingSceneConfig
- ❌ `show_complexity` - Now in AlgorithmAnalysisSceneConfig
- ❌ `celebrate_goal` - Now in PathfindingSceneConfig

### 12.2 New Scene Configuration Requirements
**Storyboards now require:**
- Scene configuration specification in `play_events` action
- Algorithm-specific actions provided by scene configurations
- Generic storyboard structure that works across algorithm types
- Parameter template support for dynamic arguments

### 12.3 Updated Action Resolution
**Action resolution hierarchy:**
1. Core generic actions (Director)
2. Scene configuration actions (SceneEngine)
3. Plugin actions (Registry)
4. Error with helpful context

```python
# Migration example: BFS storyboard action
# OLD v1.0 (algorithm-specific in core DSL):
- action: place_start
  args: {pos: [0, 0]}

# NEW v2.0 (generic storyboard + scene configuration):
- action: place_start        # Resolved via PathfindingSceneConfig
  args: {pos: [0, 0]}        # Same args, different resolution

# Scene configuration provides the implementation:
PathfindingSceneConfig.action_handlers["place_start"] = pathfinding_place_start_handler
```

---
