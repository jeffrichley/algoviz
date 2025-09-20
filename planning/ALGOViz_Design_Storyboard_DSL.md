# ALGOViz Design Doc — Storyboard DSL

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
Define a **declarative DSL** for describing videos as *Acts → Shots → Beats*. The DSL removes imperative scene sprawl, enables reuse, and serves as the bridge between **data (VizEvents)** and **presentation (widgets/grid)**.

## 2. Non‑Goals
- Rendering specifics of Manim objects (left to Director & Widgets)
- Voice synthesis specifics (Voiceover doc)
- Algorithm semantics (Adapters & VizEvents doc)

## 3. Requirements
- Human‑readable YAML/JSON with strict validation
- Minimal surface area: each **Beat** is one *action* + *args*
- Optional **narration** and **bookmarks** per Beat
- Permissive defaults; forward‑compatible for future actions

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

### 4.2 YAML Example
```yaml
acts:
  - title: "Intro"
    shots:
      - beats:
          - action: show_title
            args: {text: "Breadth-First Search"}
            narration: "This video explains Breadth-First Search."
          - action: show_grid
            narration: "Here is our grid environment."
  - title: "Run BFS"
    shots:
      - beats:
          - action: show_widgets
            args: {queue: true, hud: true, legend: true}
            narration: "We maintain a queue for the frontier."
          - action: play_events
            args: {routing: "bfs_routing"}
            narration: "We enqueue and dequeue nodes level by level until we reach the goal."
            bookmarks:
              enqueue: "queue.highlight_frontier"
              dequeue: "queue.highlight_head"
              goal: "grid.flash_goal"
  - title: "Results"
    shots:
      - beats:
          - action: trace_path
            narration: "Here is the path we discovered."
          - action: outro
```

## 5. Actions (initial set)
| Action | Description | Expected Args |
|---|---|---|
| `show_title` | Show title card | `text: str` |
| `show_grid` | Draw / reveal grid | *none* |
| `place_start` | Place start token | *optional:* `pos` |
| `place_goal` | Place goal token | *optional:* `pos` |
| `place_obstacles` | Render obstacles | list of cells |
| `show_widgets` | Show HUD/Legend/DS views | booleans: `queue`, `stack`, `pqueue`, `legend`, `hud` |
| `play_events` | Stream adapter events via routing | `routing: str` |
| `trace_path` | Visualize shortest path | *optional args* |
| `show_complexity` | Display complexity text | O-notations |
| `celebrate_goal` | Confetti/pulse | *optional* |
| `outro` | Fade out/credits | *optional* |

> New actions should follow the convention **small, composable, idempotent**. The Director maps an action name to a callable (registry).

## 6. Validation & Loading
- Pydantic models mirror the dataclasses (for runtime validation).
- Strict keys; unknown keys flag warnings (fail in CI).
- Provide helpful error messages: include act/shot indexes for context.

## 7. Execution Contract
- The **Director** iterates acts → shots → beats.
- For each **Beat**:
  1. Compute base `run_time` from `TimingConfig` by action class (e.g., UI vs events vs effects).
  2. If narration present and voiceover enabled, open `voiceover(text)` context and use hybrid timing:  
     `run_time = max(base, tracker.duration)`; clamp by `max_duration` if provided.
  3. Invoke **Action Handler** with `(scene, args, run_time, context)`.
  4. If **bookmarks** defined, Director pre-registers literal-word triggers → action callables.

### 7.1 Bookmarks Scaffold (v1 Implementation)
- **Current Phase**: Bookmarks are scaffolded for future functionality
- **v1 Behavior**: Literal word matching with log-only output
- **Schema**: `bookmarks: { "enqueue": "queue.highlight_frontier" }`
- **Implementation**: When TTS processes narration text, if a bookmark word appears literally in the text, log the occurrence
- **Future Phases**: Word-boundary callbacks will trigger the mapped actions in real-time during playback

## 8. Extensibility
- New actions: register via `core.registry` with `name -> callable`.
- External packages can ship storyboard YAMLs and action handlers via entry points.
- Inline narration now; later: external narration or i18n bundles.

## 9. Failure Modes & Handling
- Unknown action → fail fast with clear message (“Unknown action ‘X’ at Act 2/Shot 1/Beat 3”).
- Missing required args → validation error before render.
- Bookmark word never occurs → log warning; continue.
- Narration enabled but engine missing → fallback to silent; warn.

## 10. Testing Strategy
- YAML schema tests (bad/missing/extra keys).
- Golden storyboards (snapshots) parsed ⇒ round-trip to dataclasses.
- Action contracts mocked; ensure Director calls with correct `run_time` and args.
- Bookmarks: simulate “spoken words” and assert actions fire.

## 11. Performance
- Keep YAML small; prefer references to shared sequences if needed (future).
- Pre-parse and memoize storyboards in CLI to avoid repeated parsing.
- No heavy computation; this layer stays declarative.

## 12. Open Questions
- Bookmark matching: literal word vs token index vs regex (v1 = literal word).  
- Per-beat vs per-shot narration defaults (v1 = per-beat only).
