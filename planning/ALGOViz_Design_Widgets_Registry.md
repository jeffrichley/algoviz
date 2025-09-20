# ALGOViz Design Doc — Widgets & Component Registry

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
Widgets are **reusable, declarative UI/visual components** such as grids, queues, HUDs, and legends. The **Component Registry** acts as a service locator and dependency injector, decoupling visualization logic from algorithm adapters and the Director.

## 2. Non‑Goals
- Timing rules (TimingConfig owns that)
- Narration or voiceover handling (Voiceover owns that)
- Algorithm semantics (Adapters emit events)

## 3. Widget Contract
```python
class Widget(Protocol):
    def show(self, scene, **kwargs): ...
    def update(self, scene, event: VizEvent, run_time: float): ...
    def hide(self, scene): ...
```

- **show**: Initialize and render widget (enter animation).  
- **update**: React to VizEvents or storyboard beats.  
- **hide**: Clean teardown (exit animation).  

All widgets are stateless at creation and hold internal state only while active in a scene.

## 4. Examples
- **QueueWidget**: Visual representation of BFS queue.  
- **StackWidget**: Visual representation of DFS stack.  
- **PriorityQueueWidget**: For Dijkstra/A*.  
- **GridWidget**: 2D grid with colored cells.  
- **LegendWidget**: Key for colors/symbols.  
- **HUDWidget**: Overlay for complexity/time counters.  
- **PathTracer**: Animated highlight of final solution path.  

## 5. Component Registry
```python
class ComponentRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, name: str, factory: Callable[[], Widget]):
        self._registry[name] = factory

    def get(self, name: str) -> Widget:
        if name not in self._registry:
            raise KeyError(f"Widget '{name}' not registered")
        return self._registry[name]()
```

- **register**: Register widget factory once at startup.  
- **get**: Retrieve a fresh widget instance for a scene.  

## 6. Director Integration
- Storyboard beat `show_widgets` resolves to `registry.get()` calls.  
- VizEvents routed by Director call `widget.update(scene, event, run_time)`.  
- When shot/act ends, Director invokes `widget.hide()`.  

## 7. Storyboard Actions → Widgets
| Action | Widget(s) | Example |
|--------|-----------|---------|
| `show_widgets` | QueueWidget, HUDWidget, LegendWidget | BFS intro |
| `play_events` | GridWidget, QueueWidget | Node expansions |
| `trace_path` | PathTracer | Final path |
| `show_complexity` | HUDWidget | Show O(n) |

## 8. Testing Strategy
- **Unit**: Mock scene + event; assert widget updates correctly.  
- **Snapshot**: Render widget to image for regression testing.  
- **Integration**: Run Director with mock adapter → ensure widgets respond.  

## 9. Extensibility
- Adding a widget = implement contract + register.  
- Storyboards and Adapters do not change.  
- External plugins may register widgets.  

## 10. Failure Modes
- Missing widget name → Director surfaces error.  
- Widget update fails → log + skip beat (do not crash render).  
- Registry collision → fail early at startup.  

## 11. Open Questions
- Should registry allow **namespacing** (e.g., `algo.queue`, `ui.hud`)?  
- Do we need **per‑algorithm default widget bundles**?  
