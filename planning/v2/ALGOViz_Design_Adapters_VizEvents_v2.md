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

## 7. Routing Maps (Updated for v2.0)
Scene configuration routing replaces simple routing maps:

```python
# OLD v1.0 - Hard-coded BFS-specific methods
routing_map_bfs = {
    "enqueue": ["queue.highlight_enqueue", "grid.mark_frontier"],
    "dequeue": ["queue.highlight_dequeue"],
    "goal_found": ["grid.flash_goal", "hud.show_success"]
}

# NEW v2.0 - Scene configuration with generic methods
BFSSceneConfig.create().event_bindings = {
    "enqueue": [
        EventBinding(widget="queue", action="enqueue", params={"value": "${event.node}"}, order=1),
        EventBinding(widget="grid", action="highlight_element", params={"index": "${event.pos}", "style": "frontier"}, order=2)
    ],
    "dequeue": [
        EventBinding(widget="queue", action="dequeue", params={}, order=1)
    ],
    "goal_found": [
        EventBinding(widget="grid", action="highlight_element", params={"index": "${event.pos}", "style": "goal"}, order=1),
        EventBinding(widget="hud", action="show_message", params={"text": "Goal Found!", "style": "success"}, order=2)
    ]
}
```

- **Generic widget methods**: `highlight_element`, `enqueue`, `dequeue`, `show_message`
- **Parameter templates**: `${event.node}`, `${event.pos}` resolve to event data
- **Execution order**: Multiple widgets can respond to same event in configured order

## 8. Director Integration (Updated for v2.0)
- Director pulls algorithm adapter via registry.
- SceneEngine handles event routing through scene configuration.
- Events routed to generic widget methods with parameter template resolution.
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

### 9.2 Parameter Template System
Templates resolve event data to widget method parameters:

```python
# Template examples:
"${event.node}"          # Resolves to event.payload["node"]
"${event.pos}"           # Resolves to event.payload["pos"]
"${config.colors.frontier}"  # Resolves to configuration value
"${timing.fast}"         # Resolves to timing configuration

# Runtime resolution in SceneEngine:
def resolve_template(template: str, context: dict) -> Any:
    if template.startswith("${event."):
        key = template[8:-1]  # Remove ${event. and }
        return context["event"].payload[key]
    elif template.startswith("${config."):
        path = template[9:-1].split(".")
        return get_nested_value(context["config"], path)
    # ... other template types
```

### 9.3 Widget Resolution Process
SceneEngine resolves events to widget actions:

1. **Event Received**: VizEvent from algorithm adapter
2. **Binding Lookup**: Find event_bindings for event.type
3. **Widget Resolution**: Get widget instances from scene configuration
4. **Parameter Resolution**: Resolve template parameters with event context
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
            resolved_params = self.resolve_parameters(binding.params, {
                "event": event,
                "config": context.config,
                "timing": context.timing
            })
            
            # Call generic widget method
            method = getattr(widget, binding.action)
            method(**resolved_params)
```

## 10. Testing Strategy
- **Unit tests**: Golden event sequences for known scenarios.
- **Fuzz tests**: Randomized scenarios, ensure determinism.
- **Coverage**: Ensure all VizEvent types have scene configuration bindings.
- **Scene Configuration Tests**: Validate parameter template resolution.

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
- Template resolution failure → error with template and available context.

## 13. Open Questions
- Should we support **batched events** for performance? (Phase 2)
- Should we **standardize payload keys** (`node`, `pos`, `weight`) across all graph algorithms? (Phase 1+)
- Scene configuration composition and inheritance patterns? (Future)

---
