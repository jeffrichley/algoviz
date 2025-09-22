# ALGOViz Design Doc — Director v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Complete rewrite for Widget Architecture v2.0 - pure orchestrator with SceneEngine)
**Supersedes:** planning/v1/ALGOViz_Design_Director.md

---

## 1. Purpose

The **Director** is a **pure orchestrator** that executes storyboards using scene configurations, with no algorithm-specific knowledge. It delegates widget lifecycle and event routing to the SceneEngine while maintaining responsibility for timing, voiceover synchronization, and storyboard execution flow.

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

## 3. SceneEngine Integration (New Section)

### 3.1 Scene Configuration Loading (Hydra-zen First)
```python
from hydra_zen import instantiate
from omegaconf import DictConfig

class Director:
    def __init__(self, scene, storyboard, timing, scene_config: DictConfig, **kwargs):
        # Instantiate scene configuration using hydra-zen
        if hasattr(scene_config, '_target_'):
            self.scene_engine = SceneEngine(instantiate(scene_config), timing)
        else:
            self.scene_engine = SceneEngine(scene_config, timing)
        
        # Director delegates widget management to SceneEngine
        self.scene = scene
        self.storyboard = storyboard
        self.timing = timing
        self.mode = kwargs.get('mode', 'normal')
        self.with_voice = kwargs.get('with_voice', False)
        self.voiceover = kwargs.get('voiceover', None)
        
        # Only generic actions registered
        self._register_core_actions()
```

### 3.2 Widget Lifecycle Management
- SceneEngine instantiates widgets from scene configuration
- Director calls SceneEngine for widget show/hide
- No direct widget management in Director

```python
def _enter_shot(self, shot, act_index, shot_index):
    """Enter shot - delegate widget lifecycle to SceneEngine."""
    self.scene_engine.initialize_widgets_for_shot(shot)
    
def _exit_shot(self, shot, act_index, shot_index):
    """Exit shot - delegate widget cleanup to SceneEngine."""
    self.scene_engine.cleanup_widgets_for_shot(shot)
```

### 3.3 Event Routing Through SceneEngine
- Algorithm events routed through scene configuration
- Parameter template resolution in SceneEngine
- Conditional execution support

```python
def _play_events(self, beat, run_time, context):
    """Play algorithm events through scene configuration."""
    adapter = self.registry.get_algorithm(context.algorithm)
    
    for event in adapter.run(context.scenario):
        # Route through scene configuration, not direct widget calls
        self.scene_engine.process_event(event, run_time, context)
```

## 4. Class Sketch (Updated for v2.0)

```python
class Director:
    def __init__(self, scene, storyboard, timing, scene_config, **kwargs):
        self.scene = scene
        self.storyboard = storyboard
        self.timing = timing
        self.scene_engine = SceneEngine(scene_config)  # NEW
        self.mode = kwargs.get('mode', 'normal')
        self.with_voice = kwargs.get('with_voice', False)
        self.voiceover = kwargs.get('voiceover', None)
        
        # Only generic actions registered
        self._register_core_actions()  # show_title, show_widgets, play_events, outro

    def run(self):
        for i_act, act in enumerate(self.storyboard.acts):
            self._enter_act(act, i_act)
            for i_shot, shot in enumerate(act.shots):
                self._enter_shot(shot, i_act, i_shot)
                for i_beat, beat in enumerate(shot.beats):
                    self._run_beat(beat, i_act, i_shot, i_beat)
                self._exit_shot(shot, i_act, i_shot)
            self._exit_act(act, i_act)

    def _run_beat(self, beat, ai, si, bi):
        base = self.timing.base_for(beat.action, mode=self.mode)
        
        def invoke(run_time):
            # Resolve action through scene configuration if not core action
            if beat.action in self.core_actions:
                handler = self.core_actions[beat.action]
                handler(self.scene, beat.args, run_time, context={"ai": ai, "si": si, "bi": bi})
            else:
                # Delegate to scene configuration using hydra-zen patterns
                self.scene_engine.execute_action(beat.action, beat.args, run_time, 
                                               context={"ai": ai, "si": si, "bi": bi})

        # Hybrid timing with voiceover (unchanged)
        if self.with_voice and beat.narration and self.voiceover:
            with self.voiceover(text=beat.narration) as tracker:
                self._register_bookmarks(beat, tracker)
                run_time = max(base, tracker.duration)
                if beat.max_duration: run_time = min(run_time, beat.max_duration)
                if beat.min_duration: run_time = max(run_time, beat.min_duration)
                invoke(run_time)
        else:
            run_time = base
            if beat.min_duration: run_time = max(run_time, beat.min_duration)
            if beat.max_duration: run_time = min(run_time, beat.max_duration)
            invoke(run_time)
    
    def _register_core_actions(self):
        """Register only generic orchestration actions."""
        self.core_actions = {
            "show_title": self._action_show_title,
            "show_widgets": self._action_show_widgets,
            "play_events": self._action_play_events,
            "outro": self._action_outro
        }
```

## 5. Event Playback (Updated for Scene Configuration)

- Director obtains **AlgorithmAdapter** from registry
- Adapter yields **VizEvent**s
- Director passes events to **SceneEngine** for routing
- SceneEngine uses **scene configuration** to bind events to widget actions
- Parameter templates resolve event data to widget method parameters
- Multiple widgets can respond to same event in configured order

```python
def _action_play_events(self, scene, args, run_time, context):
    """Play algorithm events through hydra-zen scene configuration routing."""
    algorithm_name = args.get('algorithm', context.get('algorithm'))
    adapter = self.registry.get_algorithm(algorithm_name)
    
    # Get scene configuration for this algorithm (hydra-zen instantiated)
    scene_config = self.scene_engine.get_scene_config()
    
    for event in adapter.run(context.scenario):
        # Route through scene configuration using parameter templates
        event_run_time = self.timing.events_for(mode=self.mode)
        self.scene_engine.handle_event(event)  # Uses hydra-zen parameter resolution
```

## 6. Actions & Routing (Updated for v2.0)

### 6.1 Core Generic Actions Only
| Action | Description | Expected Args |
|---|---|---|
| `show_title` | Show title card | `text: str`, `subtitle: str` |
| `show_widgets` | Show widgets from scene config | widget names: `queue: true`, `grid: true` |
| `play_events` | Stream adapter events via scene routing | `routing_override: dict` (optional) |
| `outro` | Fade out/credits | `text: str` (optional) |

### 6.2 Scene Configuration Action Resolution
```python
def resolve_action(self, action_name: str, args: dict, run_time: float, context: dict):
    """Resolve action through core registry or scene configuration."""
    
    # 1. Check core actions first
    if action_name in self.core_actions:
        return self.core_actions[action_name]
    
    # 2. Check scene configuration actions
    if self.scene_engine.has_action(action_name):
        return lambda scene, args, run_time, context: \
            self.scene_engine.execute_action(action_name, args, run_time, context)
    
    # 3. Check plugin actions
    if self.registry.has_action(action_name):
        return self.registry.get_action(action_name)
    
    # 4. Error if not found
    raise ValueError(f"Unknown action '{action_name}' - available: {self.get_available_actions()}")
```

### 6.3 Algorithm-Specific Actions in Scene Configs
Algorithm-specific actions are now handled by scene configurations:

```python
# Example: BFS scene configuration provides algorithm-specific actions
class BFSSceneConfig(SceneConfig):
    @staticmethod
    def create() -> SceneConfig:
        return SceneConfig(
            action_handlers={
                "place_start": lambda scene, args, run_time, context: 
                    scene_engine.get_widget("grid").mark_start(args["pos"]),
                "place_goal": lambda scene, args, run_time, context:
                    scene_engine.get_widget("grid").mark_goal(args["pos"]),
                "celebrate_goal": lambda scene, args, run_time, context:
                    scene_engine.get_widget("grid").highlight_element(args["pos"], "celebration")
            }
        )
```

## 7. Timing (Unchanged)

- `TimingConfig` provides buckets: `ui`, `events`, `effects`, `waits`
- Mode multipliers: `draft`, `normal`, `fast`
- Hybrid rule ensures narration never gets clipped
- **Quality vs Timing Independence**: Render quality and timing mode are independent

## 8. Transitions (Unchanged)

- `_enter_act/_exit_act` and `_enter_shot/_exit_shot` perform fades or waits
- Uses `timing.waits` for transition durations
- Defaults conservative; overridable via storyboard beats

## 9. Error Handling (Updated for v2.0)

### 9.1 Scene Configuration Errors
- Unknown action in scene configuration → fail with available actions list
- Scene configuration loading failure → clear error with config path
- Widget instantiation failure → error with widget specification

### 9.2 Widget Resolution Errors
- Missing widget in scene configuration → error with available widgets
- Widget method not found → error with available methods
- Parameter template resolution failure → error with template and context

### 9.3 Event Binding Errors
- Event type not in scene configuration → log warning and skip
- Widget action failure → log error and continue with next binding
- Parameter resolution failure → error with template details

```python
def handle_scene_configuration_error(self, error: Exception, context: dict):
    """Handle scene configuration related errors."""
    logger.error(f"Scene configuration error at {context['location']}: {error}")
    
    if isinstance(error, WidgetNotFoundError):
        available_widgets = list(self.scene_engine.widgets.keys())
        logger.error(f"Available widgets: {available_widgets}")
    elif isinstance(error, ActionNotFoundError):
        available_actions = self.scene_engine.get_available_actions()
        logger.error(f"Available actions: {available_actions}")
```

## 10. Testing (Updated for v2.0)

### 10.1 Generic Director Testing
```python
def test_director_core_actions():
    """Test only generic orchestration actions."""
    director = Director(scene, storyboard, timing, scene_config)
    
    # Test core actions work
    assert "show_title" in director.core_actions
    assert "show_widgets" in director.core_actions
    assert "play_events" in director.core_actions
    assert "outro" in director.core_actions
    
    # Test no algorithm-specific actions
    assert "place_start" not in director.core_actions
    assert "celebrate_goal" not in director.core_actions
```

### 10.2 Scene Configuration Testing
```python
def test_scene_configuration_action_resolution():
    """Test action resolution through scene configuration."""
    scene_config = BFSSceneConfig.create()
    director = Director(scene, storyboard, timing, scene_config)
    
    # Algorithm-specific actions should resolve through scene config
    beat = Beat(action="place_start", args={"pos": (0, 0)})
    director._run_beat(beat, 0, 0, 0)  # Should not raise error
```

### 10.3 Multi-Algorithm Validation
```python
def test_director_algorithm_agnostic():
    """Test Director works with any algorithm via scene configuration."""
    
    # Test with BFS
    bfs_config = BFSSceneConfig.create()
    bfs_director = Director(scene, bfs_storyboard, timing, bfs_config)
    bfs_director.run()
    
    # Test with A* (different scene configuration)
    astar_config = AStarSceneConfig.create()
    astar_director = Director(scene, astar_storyboard, timing, astar_config)
    astar_director.run()
    
    # Director code unchanged between algorithms
```

## 11. Performance (Updated for v2.0)

- Avoid per-beat heavy computations
- Pre-resolve core actions once at initialization
- Scene configuration actions resolved by SceneEngine
- Widget instantiation handled by SceneEngine (cached per scene)
- Batch UI updates where possible through layout engines

```python
def optimize_scene_configuration(self, scene_config: SceneConfig):
    """Pre-optimize scene configuration for performance."""
    # Pre-resolve widget factories
    self.scene_engine.preload_widget_factories()
    
    # Pre-compile parameter templates
    self.scene_engine.compile_parameter_templates()
    
    # Cache event binding lookups
    self.scene_engine.build_event_binding_cache()
```

## 12. Migration from v1.0

### 12.1 Removed Algorithm-Specific Actions
**Actions removed from Director core registry:**
- ❌ `place_start` - Now in PathfindingSceneConfig
- ❌ `place_goal` - Now in PathfindingSceneConfig
- ❌ `place_obstacles` - Now in PathfindingSceneConfig
- ❌ `show_complexity` - Now in AlgorithmAnalysisSceneConfig
- ❌ `celebrate_goal` - Now in PathfindingSceneConfig

### 12.2 New Scene Configuration Requirements
**Scene configurations must provide:**
- Widget specifications for algorithm-specific widgets
- Event bindings for algorithm events
- Action handlers for algorithm-specific storyboard actions
- Parameter templates for runtime resolution

### 12.3 Updated Integration Points
**Director now integrates with:**
- **SceneEngine**: Widget lifecycle and event routing
- **Scene Configuration**: Algorithm-specific behavior
- **Generic Action Registry**: Only orchestration actions
- **Plugin System**: Scene configuration plugins

```python
# Migration example: BFS-specific action moved to scene configuration
class BFSSceneConfig(SceneConfig):
    @staticmethod
    def create() -> SceneConfig:
        return SceneConfig(
            action_handlers={
                "place_start": lambda scene, args, run_time, context: 
                    context['scene_engine'].get_widget("grid").mark_start(args["pos"])
            },
            event_bindings={
                "enqueue": [
                    EventBinding(widget="queue", action="enqueue", params={"element": "${event.node}"})
                ]
            }
        )
```

---

