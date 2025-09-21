# ALGOViz Design Doc — Adapters & VizEvents

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
The **Adapter + VizEvent system** is the bridge between **algorithms** and the **visual layer**. Adapters translate pure algorithm logic into declarative `VizEvent`s. These events drive visual updates, narration, and testing.

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

## 7. Routing Maps
Routing maps connect VizEvents → widget updates.

```python
routing_map_bfs = {
    "enqueue": ["queue.highlight_enqueue", "grid.mark_frontier"],
    "dequeue": ["queue.highlight_dequeue"],
    "goal_found": ["grid.flash_goal", "hud.show_success"]
}
```

- Stored in registry, keyed by algorithm name.
- Overrideable by Storyboard beat args.

## 8. Director Integration
- Director pulls algorithm adapter via registry.
- Iterates over events and dispatches to registered handlers.
- Run time per event from `TimingConfig.events`, hybrid with narration.

## 9. Testing Strategy
- **Unit tests**: Golden event sequences for known scenarios.
- **Fuzz tests**: Randomized scenarios, ensure determinism.
- **Coverage**: Ensure all VizEvent types have at least one route.

## 10. Extensibility
- Adding new algorithm: implement Adapter, register VizEvents + routing map.
- No Director/Storyboard changes required.
- External contributors can ship Adapters as plugins.

## 11. Failure Modes
- Adapter throws exception → Director surfaces with algorithm name + step index.
- Unknown event type → registry fail with context (adapter + index).
- Empty event stream → log warning.

## 12. Open Questions
- Should we support **batched events** for performance? (Phase 2)
- Should we **standardize payload keys** (`node`, `pos`, `weight`) across all graph algorithms? (Phase 1+)
