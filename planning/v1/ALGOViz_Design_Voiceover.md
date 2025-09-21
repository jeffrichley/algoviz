# ALGOViz Design Doc — Voiceover Integration

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
Add **narration** to algorithm videos with **CoquiTTS** (default), keeping the framework clean and declarative. Voiceover must be centralized (no scattered `with self.voiceover(...)` blocks) and respect **hybrid timing**.

## 2. Non‑Goals
- Full audio production tooling (noise reduction, EQ, mixing)
- Human recording UX (RecorderService later as plugin)
- Complex bookmark routing (Phase 5)

## 3. Requirements
- **Silent by default**; enable with `--with-voiceover`.
- **Inline narration** per Beat; optional global language/voice settings.
- **Hybrid timing** (never clip narration; do not speed up visuals below base).
- **Bookmarks scaffold**: literal word → action name.
- **Subtitles** in Phase 3 (SRT generation).
- **Narration scaffolding**: inline text fields in beats serve dual purpose for TTS and subtitle generation.

## 4. Architecture
```
Storyboard (narration text, bookmarks)
        ↓
Director (central voiceover coordinator)
        ↓
VoiceoverEngine (CoquiTTS adapter; can swap backends)
        ↓
Scene (VoiceoverScene wrapper when enabled)
```
- **Director** decides whether to wrap a beat with voiceover based on flags + narration presence.
- **VoiceoverEngine** abstracts engine specifics; returns a `tracker` with `.duration` and (future) bookmark callbacks.

## 5. API Sketch

### 5.1 Director Usage
```python
if self.with_voice and beat.narration:
    with self.voiceover(text=beat.narration, lang=config.lang, voice=config.voice) as tracker:
        self._register_bookmarks(beat, tracker)  # scaffold only
        run_time = max(timing_base, tracker.duration)
        call_action(run_time)
else:
    call_action(timing_base)
```

### 5.2 Voiceover Engine Interface
```python
class VoiceoverEngine(Protocol):
    def context(self, text: str, *, lang: str, voice: str):
        """Return a context manager yielding a Tracker(duration: float)."""
        ...
```
- Initial backend: **CoquiTTS** (configurable voice, speed).  
- Later backends: RecorderService, external TTS APIs.

## 6. Configuration
```yaml
voiceover:
  enabled: false
  backend: coqui
  lang: en
  voice: "en_US"
  speed: 1.0
```
- CLI flags override config: `--with-voiceover`, `--voice-service coqui`, `--voice-lang en`.

## 7. Bookmarks (Scaffold Now)
- Schema: `bookmarks: { "enqueue": "queue.highlight_frontier" }`  
- **v1**: Literal word matches; store mapping and **log occurrences** if word appears in text.  
- **Future**: Word-boundary callbacks when engine supports phoneme alignment.
- **Phase 5**: Wire to Director so when the engine signals the word boundary, it dispatches the action.

## 8. Subtitles (Phase 3)
- **Core deliverable**: Generate `.srt` sidecar files from `(act, shot, beat)` and TTS duration.  
- If voiceover off, optionally generate from narration only with synthetic timing (base per-beat durations).  
- Styling left to player; we output standard SRT.
- **Burn-in**: Optional post-Phase 3 enhancement, not core requirement.
- **Timing Sources**: SRT timestamps are derived from TimingTracker actuals by default; in polish mode, Whisper can refine timings for word-level precision.
- **Dual Mode Support**: baseline mode uses beat boundaries, whisper-align mode provides enhanced accuracy.

## 9. Error Handling
- Backend missing or misconfigured → fallback to silent; warn once.  
- TTS failure for a beat → log and continue beat with visuals only.  
- Language/voice not found → fallback to defaults; warn.

## 10. Testing
- Inject a fake engine returning `duration=1.23` and assert hybrid timing.  
- Validate SRT lines format and timestamps monotonicity.  
- Bookmark scaffold: ensure mapping loads; simulate a word hit and check logging.

## 11. Performance
- Cache synthesized audio per `(text, lang, voice, speed)` hash to disk.  
- Prewarm Coqui model before first beat to avoid first-call latency.  
- Batch synthesis per act when possible.

## 12. Security & Privacy
- Avoid sending text to external services unless explicitly chosen by user.  
- For local Coqui, ensure model files are versioned and licensed appropriately.  
- If RecorderService added, store audio locally with opt‑in consent.

## 13. Open Questions
- Should subtitles be generated when voiceover is disabled (using base timings)?  
- Fine-grained word boundary signaling from Coqui (may need phoneme alignment later).
