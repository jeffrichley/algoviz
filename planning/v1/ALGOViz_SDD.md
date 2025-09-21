# ALGOViz System Design Document (SDD)

## 1. Introduction
ALGOViz is a next-generation framework for algorithm visualization videos. It is designed to move beyond monolithic scene code (e.g., the current 2000+ line BFS scene) and provide a **modular, event-driven, and extensible** system that supports:
- Multiple algorithms (BFS, DFS, Dijkstra, A*…)
- Configurable storyboards (acts, shots, beats)
- Unified timing control
- Reusable UI widgets (Queue, Stack, HUD, Legend, PathTracer)
- Narration (voiceover with CoquiTTS)
- Subtitles (Phase 3)
- Bookmarks for word-level sync (scaffolded now, full later)

This document captures the agreed architecture, design patterns, and behavior of ALGOViz.

---

## 2. Goals
- Replace monolithic scenes with a **layered architecture**.
- Enable rapid addition of new algorithms without editing core code.
- Centralize timing to maintain consistency across all animations.
- Integrate narration and future subtitle export cleanly.
- Provide a world-class developer and contributor experience.

---

## 3. High-Level Architecture

### Flow
1. **Algorithm Adapter** → emits `VizEvent`s.
2. **Routing Map** → maps events to widget/grid actions.
3. **Storyboard DSL** → declarative script (acts → shots → beats).
4. **Director** → orchestrates storyboard execution, applies timing, syncs voiceover.
5. **Widgets** → visual components (QueueView, StackView, HUD, etc.).
6. **Output** → rendered video, optional voiceover + subtitles.

### Package Layout
```
agloviz/
├─ adapters/          # Algorithm event emitters (BFS, DFS, etc.)
├─ core/
│  ├─ scene_base.py   # Base scene class
│  ├─ storyboard.py   # DSL for acts/shots/beats
│  ├─ director.py     # Orchestration (timing + voiceover)
│  ├─ timing.py       # TimingConfig + TimingTracker
│  ├─ scenario.py     # Scenario loader (YAML)
│  ├─ themes.py       # Visual styles, palettes
│  ├─ registry.py     # Algorithm + widget registry
│  └─ component_registry.py
├─ widgets/           # QueueView, StackView, HUD, PathTracer, etc.
├─ config/            # YAML configs: scenarios, themes, storyboards
├─ plugins/           # 3rd party algorithm extensions
├─ cli.py             # Typer CLI
└─ py.typed
```

---

## 4. Storyboard DSL

### Beat Schema
```python
@dataclass
class Beat:
    action: str
    args: dict[str, Any] = field(default_factory=dict)
    narration: str | None = None
    bookmarks: dict[str, str] = field(default_factory=dict)
    min_duration: float | None = None
    max_duration: float | None = None
```

### Example YAML
```yaml
acts:
  - title: "Introduction"
    shots:
      - beats:
          - action: show_title
            args: {text: "Breadth-First Search"}
            narration: "This is Breadth-First Search, or BFS."
          - action: show_grid
            narration: "Here is the grid environment."
  - title: "Algorithm"
    shots:
      - beats:
          - action: play_events
            routing: bfs_routing
            narration: "We enqueue and dequeue nodes until the goal is reached."
            bookmarks:
              enqueue: "queue.highlight"
              dequeue: "queue.pop_highlight"
              goal: "grid.goal_flash"
  - title: "Conclusion"
    shots:
      - beats:
          - action: trace_path
            narration: "Here is the path we discovered."
          - action: outro
            narration: "And that concludes BFS."
```

---

## 5. Director Responsibilities
- Parse storyboard → iterate acts/shots/beats.
- For each beat:
  - Apply `TimingConfig` base run_time.
  - If narration present → use CoquiTTS voiceover, run animations in `with self.voiceover(...)`.
  - Apply **Hybrid Timing Rule**:  
    ```python
    run_time = max(timing.base, tracker.duration)
    if beat.max_duration:
        run_time = min(run_time, beat.max_duration)
    ```
  - Dispatch action (grid, widgets, HUD, etc.).
  - Trigger bookmarks if defined.
- Log execution via `TimingTracker`.
- Export subtitles (Phase 3).

---

## 6. Timing System
- Centralized config in `timing.yaml`.
- Modes: `draft`, `normal`, `fast`.
- Example:
```yaml
modes:
  normal:
    ui: 1.0
    events: 0.8
    effects: 0.5
  fast:
    ui: 0.5
    events: 0.3
    effects: 0.2
```

---

## 7. Voiceover Integration
- Narration scaffolded now (`narration` field on Beat).
- **Default Mode:** silent unless `--with-voiceover` CLI flag is passed.
- **Audio Service:** CoquiTTS by default.
- **Hybrid timing:** visuals never cut off narration, narration never shortens visuals.
- **Bookmarks:** scaffolded now, full routing later.
- **Subtitles:** Phase 3 (export SRT from narration fields).

---

## 8. Scenario Runtime Contract

Adapters rely on a consistent **Scenario** interface to query grid/graph properties during algorithm execution. This contract bridges the gap between static configuration (YAML files) and runtime algorithm needs.

- **Scenario Runtime Contract**: adapters can rely on the runtime exposing `neighbors(node)`, `in_bounds(pos)`, `passable(pos)`, `cost(a,b)`, `width`, `height`. (See section 8.1 Core Interface for full details)

### 8.1 Core Interface
```python
class Scenario(Protocol):
    # Grid properties
    width: int
    height: int
    start: tuple[int, int]
    goal: tuple[int, int]
    
    # Navigation queries
    def neighbors(self, node: tuple[int, int]) -> list[tuple[int, int]]:
        """Return valid neighboring positions from the given node."""
        ...
    
    def in_bounds(self, node: tuple[int, int]) -> bool:
        """Check if node coordinates are within grid boundaries."""
        ...
    
    def passable(self, node: tuple[int, int]) -> bool:
        """Check if node is not an obstacle and can be traversed."""
        ...
    
    # Weighted graph support (for Dijkstra, A*)
    def cost(self, from_node: tuple[int, int], to_node: tuple[int, int]) -> float:
        """Return movement cost between adjacent nodes. Default: 1.0.
        
        Raises ValueError if nodes are not adjacent.
        Returns float('inf') for impassable transitions.
        """
        ...

# Optional grid-based helpers (mixin for grid scenarios)
class GridScenarioMixin:
    def manhattan_distance(self, a: tuple[int, int], b: tuple[int, int]) -> int:
        """Manhattan distance heuristic for grid-based A*."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def euclidean_distance(self, a: tuple[int, int], b: tuple[int, int]) -> float:
        """Euclidean distance heuristic for grid-based A*."""
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5
```

### 8.2 Configuration to Runtime Mapping
The `ScenarioConfig` from the Configuration System loads static data:
```yaml
# scenario.yaml
scenario:
  name: "maze_small"
  grid_file: "grids/maze_small.yaml"  # Contains obstacle positions
  start: [0, 0]
  goal: [9, 9]
  weighted: false
```

The **ScenarioLoader** uses factory patterns to convert configuration into runtime `Scenario` objects:
```python
class ScenarioLoader:
    @staticmethod
    def from_file(path: str) -> Scenario:
        """Load scenario from YAML file path."""
        ...
    
    @staticmethod
    def from_config(config: ScenarioConfig) -> Scenario:
        """Convert ScenarioConfig to runtime Scenario."""
        ...
    
    @staticmethod
    def random_grid(width: int, height: int, obstacle_density: float = 0.2) -> Scenario:
        """Generate random grid scenario for testing."""
        ...
```

### 8.3 Step Indexing Strategy
Adapters yield **raw events without step indices**. The Director or AdapterWrapper automatically assigns sequential step numbers:

```python
class AdapterWrapper:
    def run_with_indexing(self, adapter, scenario) -> Iterator[VizEvent]:
        for i, event in enumerate(adapter.run(scenario)):
            yield VizEvent(event.type, event.payload, step_index=i, event.metadata)
```

### 8.4 Adapter Usage Examples
```python
# BFS Adapter - yields raw events, no step indexing
def run(self, scenario: Scenario) -> Iterator[VizEvent]:
    queue = deque([scenario.start])
    visited = {scenario.start}
    
    yield VizEvent("enqueue", {"node": scenario.start})
    
    while queue:
        node = queue.popleft()
        yield VizEvent("dequeue", {"node": node})
        
        if node == scenario.goal:
            yield VizEvent("goal_found", {"node": node})
            break
            
        for neighbor in scenario.neighbors(node):
            if neighbor not in visited and scenario.passable(neighbor):
                visited.add(neighbor)
                queue.append(neighbor)
                yield VizEvent("enqueue", {"node": neighbor})

# A* Adapter with grid mixin
def run(self, scenario: Scenario & GridScenarioMixin) -> Iterator[VizEvent]:
    def heuristic(node):
        return scenario.manhattan_distance(node, scenario.goal)
    
    # Use scenario.cost() for edge weights
    for neighbor in scenario.neighbors(current):
        edge_cost = scenario.cost(current, neighbor)
        # ... A* logic
```

### 8.5 Grid File Format
Grid files referenced by `ScenarioConfig.grid_file` follow this structure:
```yaml
# grids/maze_small.yaml
width: 10
height: 10
default_cost: 1.0  # Uniform weight for all edges

obstacles:
  - [1, 1]
  - [1, 2]
  - [2, 1]

# Optional: per-edge weight overrides
weights:  
  - from: [0, 0]
    to: [0, 1] 
    cost: 2.5
  - from: [3, 4]
    to: [3, 5]
    cost: 0.5  # Fast lane
```

### 8.6 Testing Contract Compliance
Comprehensive test harness ensures all scenario implementations satisfy the contract:

```python
class ContractTestHarness:
    def verify_scenario(self, scenario: Scenario) -> list[str]:
        """Return list of contract violations, empty if compliant."""
        violations = []
        
        # Basic bounds checking
        if not scenario.in_bounds(scenario.start):
            violations.append("start position out of bounds")
        if not scenario.in_bounds(scenario.goal):
            violations.append("goal position out of bounds")
            
        # Neighbor contract compliance
        for x in range(scenario.width):
            for y in range(scenario.height):
                node = (x, y)
                if scenario.passable(node):
                    neighbors = scenario.neighbors(node)
                    for neighbor in neighbors:
                        if not scenario.in_bounds(neighbor):
                            violations.append(f"neighbors({node}) returned out-of-bounds {neighbor}")
                        if not scenario.passable(neighbor):
                            violations.append(f"neighbors({node}) returned impassable {neighbor}")
        
        # Cost function compliance
        test_node = scenario.start
        neighbors = scenario.neighbors(test_node)
        if neighbors:
            try:
                cost = scenario.cost(test_node, neighbors[0])
                if cost < 0:
                    violations.append("cost() returned negative value")
            except Exception as e:
                violations.append(f"cost() failed for adjacent nodes: {e}")
                
            # Test non-adjacent cost (should raise or return inf)
            non_adjacent = (scenario.width + 10, scenario.height + 10)
            try:
                cost = scenario.cost(test_node, non_adjacent)
                if cost != float('inf'):
                    violations.append("cost() should return inf or raise for non-adjacent nodes")
            except ValueError:
                pass  # Expected behavior
                
        return violations

# Usage in test suites
def test_grid_scenario_contract():
    scenario = ScenarioLoader.from_file("grids/test_maze.yaml")
    harness = ContractTestHarness()
    violations = harness.verify_scenario(scenario)
    assert not violations, f"Contract violations: {violations}"
```

**Test Categories:**
- **Unit tests**: Protocol compliance for all scenario implementations
- **Property tests**: `neighbors() ⊆ in_bounds ∧ passable`
- **Integration tests**: Adapters run successfully against various scenario configurations  
- **Grid validation**: YAML dimensions match obstacle/weight coordinates
- **Edge cases**: Empty grids, single-cell paths, unreachable goals

---

## 9. CLI Experience
```
agloviz algo list
agloviz render --algo bfs --scenario demo.yaml --mode fast
agloviz render --algo a_star --scenario maze.yaml --with-voiceover --voice-service coqui
agloviz preview --algo bfs --scenario demo.yaml --frames 120
```

---

## 9. Testing & CI
- **Adapters:** deterministic VizEvents.  
- **Storyboards:** unit tests with mock Director.  
- **Timing:** assert run_times respect config + narration.  
- **Voiceover:** test narration injection + duration matching.  
- **CI Outputs:** preview GIFs, timing CSVs, optional subtitles.

---

## 10. Roadmap
- **Phase 0:** Scaffold (Beat schema, TimingConfig, narration fields, CLI flags).  
- **Phase 1:** Extract BFS → adapter + storyboard.  
- **Phase 2:** Add widgets (QueueView, HUD, Legend).  
- **Phase 3:** Full voiceover + subtitles.  
- **Phase 4:** Plugin registry, more algorithms.  
- **Phase 5:** Bookmark routing + localization.

---

## 11. Decisions Locked
- Scaffold narration now.  
- Hybrid timing is default.  
- Inline narration (YAML) for MVP.  
- Silent default; voice enabled with flag.  
- CoquiTTS as audio backend.  
- Bookmarks scaffolded now.  
- Subtitles in Phase 3.

---

## 12. Open Questions
- Bookmark schema refinement (literal vs regex vs word index).  
- Scenario complexity: grid only, or general graphs too?  
- Should narrator voice style (pitch, speed) be per-beat or global?  

---

# ✅ Conclusion
This System Design Document specifies how ALGOViz will behave as a **modular, event-driven, narrated algorithm visualization framework**. It captures all locked decisions and phases, ensuring implementation is coherent, extensible, and world-class.
