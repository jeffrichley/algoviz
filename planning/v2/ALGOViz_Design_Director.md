# ALGOViz Design Doc — Director

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
The **Director** is the **conductor**: it executes storyboards, applies timing, coordinates voiceover, routes algorithm events, and manages transitions. It centralizes concerns so beats stay declarative.

## 2. Non‑Goals
- Implementing algorithm logic (Adapters do that)
- Low-level drawing of widgets (Widgets do that)
- TTS engine specifics (Voiceover doc)

## 3. Responsibilities
1. Load & validate a `Storyboard`.
2. Resolve **actions** to callables via registry.
3. Resolve **routing maps** for `play_events`.
4. Apply **TimingConfig** (modes + categories).
5. Integrate **voiceover** with **hybrid timing**.
6. Handle **bookmarks** (scaffold now; full routing later).
7. Record timings via **TimingTracker**.
8. Manage act/shot transitions (fades, waits).

## 4. Class Sketch
```python
class Director:
    def __init__(self, scene, storyboard, timing, registry, voiceover=None, *, mode="normal", with_voice=False):
        self.scene = scene
        self.storyboard = storyboard
        self.timing = timing
        self.registry = registry
        self.voiceover = voiceover   # None unless enabled
        self.mode = mode
        self.with_voice = with_voice

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
        base = self.timing.base_for(beat.action, mode=self.mode)  # e.g., ui/events/effects bucket
        def invoke(run_time):
            handler = self.registry.resolve_action(beat.action)
            handler(self.scene, beat.args, run_time, context={"ai": ai, "si": si, "bi": bi})

        if self.with_voice and beat.narration and self.voiceover:
            with self.voiceover(text=beat.narration) as tracker:
                self._register_bookmarks(beat, tracker)  # scaffold; no-op until Phase 5
                run_time = max(base, tracker.duration)
                if beat.max_duration: run_time = min(run_time, beat.max_duration)
                if beat.min_duration: run_time = max(run_time, beat.min_duration)
                invoke(run_time)
        else:
            run_time = base
            if beat.min_duration: run_time = max(run_time, beat.min_duration)
            if beat.max_duration: run_time = min(run_time, beat.max_duration)
            invoke(run_time)
```

## 5. Event Playback (`play_events`)
- Director obtains **AlgorithmAdapter** from registry (based on `--algo`).
- Adapter yields `VizEvent`s.  
- Director looks up **routing map** (dict `EventType -> [handler_names]`).  
- For each event, call handlers (widgets/grid/HUD), applying `timing.events` as the base per-step duration (scaled by mode).  
- If narration context exists, the overall beat respects **hybrid timing** (longer of base vs speech).

## 6. Actions & Routing
- **Actions**: functions with signature `(scene, args, run_time, context)`.
- **Routing**: mapping names → callables; kept in registry.  
- Routing maps can be overridden per beat (`args.routing`), per algorithm, or globally.

## 7. Timing
- `TimingConfig` provides buckets: `ui`, `events`, `effects`, `waits`.
- Mode multipliers: `draft`, `normal`, `fast`.
- Hybrid rule ensures narration never gets clipped.
- **Quality vs Timing Independence**: Render quality (resolution, codec settings) and timing mode (animation pacing) are completely independent settings

## 8. Transitions
- `_enter_act/_exit_act` and `_enter_shot/_exit_shot` can perform fades or waits (using `timing.waits`).  
- Defaults conservative; overridable via storyboard beats (e.g., `action: frame_stage`).

## 9. Error Handling
- Unknown action or routing handler → fail with location context (Act/Shot/Beat).  
- Adapter errors → surface with algorithm name and event index.  
- Voiceover disabled but narration present → log once per act.

## 10. Testing
- Mock registry/scene and run a miniature storyboard.  
- Verify call order, `run_time` calculations, and that `play_events` iterates events.  
- Ensure timing tracker produces consistent CSV/JSON.  
- Voiceover path: inject fake `tracker.duration` and assert hybrid rule.

## 11. Performance
- Avoid per-beat heavy computations.  
- Pre‑resolve handlers and routing maps once per act.  
- Batch UI updates where possible (e.g., LaggedStart for groups).

## 12. Open Questions
- Per‑event vs per‑beat timing overrides (v1 = per‑beat only).  
- Late‑binding of routing during narration bookmarks (Phase 5).
