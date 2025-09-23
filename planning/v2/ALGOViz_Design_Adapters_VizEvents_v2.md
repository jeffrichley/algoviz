# ALGOViz Design Doc — Adapters & VizEvents v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Updated for Widget Architecture v2.0 - scene configuration routing)
**Supersedes:** planning/v1/ALGOViz_Design_Adapters_VizEvents.md

---

## 1. Purpose
The **Adapter + VizEvent system** is the bridge between **algorithms** and the **visual layer**. Adapters translate pure algorithm logic into declarative `VizEvent`s. These events drive visual updates through the scene configuration system, enabling narration and testing.

## 2. Non‑Goals
- No drawing or animations (widgets handle that)
- No timing control (Director + TimingConfig handle that)
- No narration or voiceover specifics (Storyboard + Voiceover handle that)

## 3. Responsibilities
- Provide a clean interface for running algorithms step by step.
- Emit a standardized stream of `VizEvent`s.
- Maintain determinism: same input → same sequence of events.
- Remain agnostic of Manim and storyboard logic.

## 4. VizEvent Schema
```python
from dataclasses import dataclass
from typing import Any

@dataclass
class VizEvent:
    type: str                   # e.g., "enqueue", "visit", "relax"
    payload: dict[str, Any]     # structured metadata (node, pos, weight)
    step_index: int             # monotonically increasing
    metadata: dict[str, Any] = None  # optional (complexity, counters)
```

- **type**: canonical event name for routing (defined in registry).
- **payload**: algorithm data (e.g., node position, edge weight).
- **step_index**: sequential index, used for playback or testing.
- **metadata**: optional, e.g., complexity counter snapshot.

## 5. AlgorithmAdapter Interface
```python
class AlgorithmAdapter(Protocol):
    name: str
    def run(self, scenario: ScenarioConfig) -> Iterator[VizEvent]: ...
```

- Each algorithm ships with an Adapter.
- Adapters may wrap generators or incremental step functions.
- Example: BFSAdapter, DFSAdapter, DijkstraAdapter.
- Adapters rely on the Scenario Runtime Contract: `neighbors(node)`, `in_bounds(pos)`, `passable(pos)`, `cost(a,b)`

## 5.1 Standardized Payload Keys
To ensure consistency across algorithms, adapters should use these standardized payload keys:

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `node` | tuple[int,int] | Grid position or node identifier | `(3, 5)` |
| `pos` | tuple[int,int] | Alternative to node for position | `(0, 0)` |  
| `weight` | float | Edge weight or node cost | `2.5` |
| `parent` | tuple[int,int] | Parent node in search tree | `(2, 5)` |

## 6. Example — BFS Adapter
```python
class BFSAdapter:
    name = "bfs"

    def run(self, scenario: ScenarioConfig) -> Iterator[VizEvent]:
        queue = deque([scenario.start])
        visited = {scenario.start}

        yield VizEvent("enqueue", {"node": scenario.start}, step_index=0)

        i = 1
        while queue:
            node = queue.popleft()
            yield VizEvent("dequeue", {"node": node}, step_index=i); i += 1

            if node == scenario.goal:
                yield VizEvent("goal_found", {"node": node}, step_index=i); break

            for nbr in scenario.neighbors(node):
                if nbr not in visited:
                    visited.add(nbr)
                    queue.append(nbr)
                    yield VizEvent("enqueue", {"node": nbr}, step_index=i); i += 1
```

## 7. Event-Driven Architecture (Updated for v2.0)
Scene configuration routing with **static widget configs** and **dynamic event parameters**:

```python
# OLD v1.0 - Hard-coded BFS-specific methods
routing_map_bfs = {
    "enqueue": ["queue.highlight_enqueue", "grid.mark_frontier"],
    "dequeue": ["queue.highlight_dequeue"],
    "goal_found": ["grid.flash_goal", "hud.show_success"]
}

# NEW v2.0 - Static widget configs + dynamic event parameters
BFSSceneConfig.create().event_bindings = {
    "enqueue": [
        EventBinding(widget="queue", action="add_element", 
                    params={"element": "${event.node}", "style": "frontier"}, order=1),
        EventBinding(widget="grid", action="highlight_cell", 
                    params={"position": "${event.node.position}", "style": "frontier"}, order=2)
    ],
    "dequeue": [
        EventBinding(widget="queue", action="remove_element", params={}, order=1)
    ],
    "goal_found": [
        EventBinding(widget="grid", action="highlight_cell", 
                    params={"position": "${event.node.position}", "style": "goal"}, order=1),
        EventBinding(widget="hud", action="show_message", 
                    params={"text": "Goal Found!", "style": "success"}, order=2)
    ]
}

# Event data contains dynamic parameters (resolved at runtime)
event_data = {
    "type": "enqueue",
    "node": {"position": [3, 4], "color": "red", "weight": 5}
}
```

- **Static widget configs**: Widget size, appearance, behavior set at config time
- **Dynamic parameter templates**: `${event.node.position}`, `${event.node.color}` resolved at runtime
- **Event data**: Contains dynamic values (positions, colors, weights) from algorithm execution
- **Generic widget methods**: `highlight_cell`, `add_element`, `remove_element`, `show_message`
- **Execution order**: Multiple widgets can respond to same event in configured order

## 8. Director Integration (Updated for v2.0)
- Director pulls algorithm adapter via registry.
- SceneEngine handles event routing through scene configuration.
- **Event data contains dynamic parameters** resolved at runtime with full context.
- Run time per event from `TimingConfig.events`, hybrid with narration.

```python
class Director:
    def __init__(self, scene, storyboard, timing, scene_config, **kwargs):
        self.scene_engine = SceneEngine(scene_config)
        # Director delegates event routing to SceneEngine
    
    def _play_events(self, beat, run_time, context):
        adapter = self.registry.get_algorithm(context.algorithm)
        for event in adapter.run(context.scenario):
            # Route through scene configuration
            self.scene_engine.process_event(event, run_time, context)
```

## 9. Scene Configuration Integration (New Section)

### 9.1 Event Binding Configuration
Scene configurations define how VizEvents bind to widget actions:

```python
@dataclass
class EventBinding:
    widget: str = Field(..., description="Target widget name")
    action: str = Field(..., description="Widget method to call")
    params: dict[str, Any] = Field(default_factory=dict)
    order: int = Field(1, description="Execution order")
    conditions: dict[str, Any] = Field(default_factory=dict)  # Optional conditions

class SceneConfig(BaseModel):
    widgets: dict[str, WidgetSpec]
    event_bindings: dict[str, list[EventBinding]]
```

### 9.2 Dynamic Parameter Resolution System
Event data contains dynamic parameters with template resolution at runtime:

```python
# Event data structure (from algorithm adapters):
event_data = {
    "type": "enqueue",
    "node": {
        "position": [3, 4],    # Dynamic: from algorithm
        "color": "red",        # Dynamic: from algorithm state
        "weight": 5            # Dynamic: from algorithm
    }
}

# Scene config has static parameters with dynamic templates:
EventBinding(
    widget="grid", 
    action="highlight_cell", 
    params={
        "style": "frontier",           # Static: widget behavior
        "position": "${event.node.position}",  # Dynamic: resolved from event
        "color": "${event.node.color}"         # Dynamic: resolved from event
    }
)

# Runtime parameter resolution in SceneEngine:
def resolve_event_parameters(static_params: dict, event_data: dict, context: dict) -> dict:
    resolved = {}
    for key, value in static_params.items():
        if isinstance(value, str) and value.startswith("${"):
            # Dynamic template resolution
            if value.startswith("${event."):
                # Resolve event data path like "${event.node.position}"
                path = value[8:-1]  # Remove ${event. and }
                resolved[key] = _resolve_event_path(path, event_data)
            elif value.startswith("${config."):
                # Resolve config path like "${config.colors.frontier}"
                path = value[9:-1]  # Remove ${config. and }
                resolved[key] = _resolve_config_path(path, context["config"])
            elif value.startswith("${timing."):
                # Resolve timing path like "${timing.events}"
                path = value[9:-1]  # Remove ${timing. and }
                resolved[key] = _resolve_timing_path(path, context["timing"])
        else:
            # Static value
            resolved[key] = value
    return resolved

def _resolve_event_path(path: str, event_data: dict) -> Any:
    """Resolve event data path like 'node.position' or 'node.color'"""
    keys = path.split('.')
    result = event_data
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return None
    return result
```

### 9.3 Event Processing Flow
SceneEngine processes events with dynamic parameter resolution:

1. **Event Received**: VizEvent from algorithm adapter with dynamic data
2. **Binding Lookup**: Find event_bindings for event.type
3. **Widget Resolution**: Get widget instances from scene configuration
4. **Parameter Resolution**: Merge static config params with dynamic event data
5. **Action Execution**: Call widget methods with resolved parameters
6. **Order Enforcement**: Execute bindings in specified order

```python
class SceneEngine:
    def process_event(self, event: VizEvent, run_time: float, context: dict):
        bindings = self.scene_config.event_bindings.get(event.type, [])
        
        # Sort by execution order
        bindings.sort(key=lambda b: b.order)
        
        for binding in bindings:
            widget = self.widgets[binding.widget]
            # Resolve dynamic templates with full context
            resolved_params = self.resolve_event_parameters(
                binding.params,  # Static parameters with dynamic templates
                event.payload,   # Dynamic event data
                context          # Full context (config, timing, etc.)
            )
            
            # Call generic widget method
            method = getattr(widget, binding.action)
            method(**resolved_params)
```

## 10. Testing Strategy
- **Unit tests**: Golden event sequences for known scenarios.
- **Fuzz tests**: Randomized scenarios, ensure determinism.
- **Coverage**: Ensure all VizEvent types have scene configuration bindings.
- **Dynamic Resolution Tests**: Validate parameter template resolution with event data.
- **Template Tests**: Test `${event.*}`, `${config.*}`, `${timing.*}` template resolution.

## 11. Extensibility
- Adding new algorithm: implement Adapter, register with scene configuration.
- No Director/Storyboard changes required.
- External contributors can ship Adapters + SceneConfigs as plugins.
- Scene configurations support algorithm-specific event bindings.

## 12. Failure Modes
- Adapter throws exception → Director surfaces with algorithm name + step index.
- Unknown event type → SceneEngine fails with context (adapter + index).
- Empty event stream → log warning.
- Missing widget in scene configuration → clear error with available widgets.
- Template resolution failure → error with template syntax and available context.
- Missing event data path → error with available event data structure.

## 13. Architectural Decision: Static Widget Configs + Dynamic Event Parameters

### 13.1 Why This Architecture Makes Sense

**Widgets = Static Configuration (Hydra-zen First)**
- Widgets are **visual components** with **configuration** (size, appearance, layout)
- These are **setup decisions**, not runtime decisions
- Perfect for hydra-zen static configuration and CLI overrides

**Events = Dynamic Parameters (Runtime Resolution)**
- Events are **algorithm data** with **dynamic values** (positions, colors, states)
- These are **algorithm output**, not configuration
- Perfect for runtime parameter resolution with full context

### 13.2 Benefits of This Approach

✅ **Hydra-zen First**: Scene configs are pure and predictable  
✅ **Runtime Flexibility**: Dynamic parameters from algorithm execution  
✅ **Clear Separation**: Configuration vs runtime behavior  
✅ **Best of Both Worlds**: Static setup + dynamic data  

### 13.3 Example Flow

1. **Scene Config**: "Grid should be 15x15, queue should show 10 items" (static)
2. **Event Data**: "Node at [3,4] is being visited, color it red" (dynamic)
3. **Resolution**: "Highlight cell at [3,4] with red color on 15x15 grid" (merge)

## 14. Open Questions
- Should we support **batched events** for performance? (Phase 2)
- Should we **standardize payload keys** (`node`, `pos`, `weight`) across all graph algorithms? (Phase 1+)
- Scene configuration composition and inheritance patterns? (Future)

---
