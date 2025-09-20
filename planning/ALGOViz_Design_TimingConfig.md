# ALGOViz Design Doc — TimingConfig

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
The **TimingConfig** is the single source of truth for durations and pacing in ALGOViz. It provides consistent rules for UI transitions, algorithm events, effects, waits, and narration hybrid timing.

## 2. Non‑Goals
- No direct control of storyboard beats (Storyboard defines that)
- No algorithm event semantics (Adapters handle that)
- No narration synthesis (Voiceover handles that)

## 3. Responsibilities
- Define base durations for categories (UI, events, effects, waits).  
- Support global pacing modes (draft, normal, fast).  
- Allow per‑beat overrides (`min_duration`, `max_duration`).  
- Cooperate with Voiceover for hybrid timing.  
- Provide debugging & export of actual timings.  

## 4. Structure
```python
from dataclasses import dataclass, field

@dataclass
class TimingConfig:
    ui: float = 1.0
    events: float = 0.5
    effects: float = 1.0
    waits: float = 0.5

    mode: str = "normal"
    multipliers: dict[str, float] = field(default_factory=lambda: {
        "draft": 0.5, "normal": 1.0, "fast": 0.25
    })

    def base_for(self, action: str, mode: str | None = None) -> float:
        bucket = self._bucket_for_action(action)
        m = self.multipliers[mode or self.mode]
        return getattr(self, bucket) * m

    def _bucket_for_action(self, action: str) -> str:
        # Map action name → category (ui/events/effects/waits)
        ...
```

- **Buckets**: `ui`, `events`, `effects`, `waits`  
- **Mode multipliers**: adjust globally  
- **base_for**: resolve category + apply multiplier  

## 5. Integration
- Director asks `timing.base_for(beat.action)` each beat.  
- Voiceover hybrid: `run_time = max(base, narration_duration)`.  
- Storyboard can clamp with `min_duration`/`max_duration`.  
- TimingTracker logs actual vs expected durations.  

## 6. Modes
| Mode | Multiplier | Use Case |
|------|------------|----------|
| `draft` | 0.5 | Developer iteration (fast) |
| `normal` | 1.0 | Default playback |
| `fast` | 0.25 | Quick review in CI |

## 7. Debugging / Tracking
```python
class TimingTracker:
    def __init__(self): self.records = []
    def log(self, beat, expected: float, actual: float): ...
    def export_csv(self, path): ...
```

- Director logs each beat with expected vs actual duration.  
- CSV/JSON export enables QA & CI diffing.  

## 8. Testing Strategy
- Unit test `base_for` bucket resolution.  
- Regression test: fixed storyboard → fixed total runtime.  
- Integration test with fake Voiceover to assert hybrid rule.  

## 9. Extensibility
- Add new buckets if needed (e.g., narration, complexity overlays).  
- Per‑scenario overrides: ScenarioConfig can patch base values.  
- Per‑action fine‑tuning: extend `_bucket_for_action`.  

## 10. Failure Modes
- Unknown action bucket → default to `ui` + log warning.  
- Invalid multiplier key → fallback to normal.  
- TimingTracker export fails → warn, continue render.  

## 11. Open Questions
- Should we allow **dynamic pacing** (shorter waits if narration long)?  
- Should Tracker output be part of final video metadata (JSON sidecar)?  
