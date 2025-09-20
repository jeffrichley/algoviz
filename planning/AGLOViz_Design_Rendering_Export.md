
# 🎬 Subtitles Exporter Design

## Overview

The **SubtitlesExporter** is responsible for producing human-readable subtitle tracks (SRT/VTT). It supports two **modes of operation**:

1. **Baseline (default)**

   * Uses the storyboard narration text + TimingTracker actuals.
   * Produces deterministic SRTs during CI/CD builds.
   * Fast, reproducible, and independent of external models.

2. **Whisper-aligned (optional)**

   * Runs Whisper (or another ASR/forced alignment engine) over the *final audio track*.
   * Produces a corrected SRT with real speech timings.
   * Suitable for polish phases, human voice recordings, or when precise alignment is required.

---

## Responsibilities

* **Baseline mode:**

  * Iterate over narration script fields in Storyboard.
  * Collect actual start/stop times from TimingTracker.
  * Export SRT entries per sentence or phrase.

* **Whisper-align mode:**

  * Take final rendered audio (post-TTS or recorded).
  * Run Whisper in forced-alignment mode.
  * Match recognized words against the script text (fallback if mismatch).
  * Export corrected SRT with exact word-level timestamps.

---

## Configuration

```yaml
subtitles:
  enabled: true
  mode: baseline   # [baseline | whisper-align]
  format: srt      # [srt | vtt]
  burn_in: false   # burn into video via ffmpeg
```

### CLI

```bash
# Default baseline SRT
algoviz render -a bfs -s maze.yaml --with-subtitles

# Whisper-aligned SRT
algoviz render -a bfs -s maze.yaml --with-subtitles subtitles.mode=whisper-align
```

---

## Output

* `video.mp4` (always)
* `video.srt` (if `--with-subtitles`)
* `video.srt.draft` (optional, keep baseline SRT for comparison)

---

## Data Flow

```
Storyboard narration → TimingTracker actuals → Baseline SRT
                               │
                               ▼
                     (optional Whisper)
                               │
                               ▼
                         Whisper-aligned SRT
```

* **Bookmarks:** in both modes, bookmarks are retained. In baseline mode they trigger at estimated word positions; in Whisper mode they snap to actual word boundaries.
* **Hybrid timing:** baseline mode already uses hybrid (script + actual delays). Whisper alignment refines this with phoneme-level accuracy.

---

## Performance & CI/CD

* **Baseline mode** is cheap and should be used in CI/CD runs.
* **Whisper-align mode** is GPU/CPU intensive; only run on-demand or in “publish” builds.

---

## Risks & Mitigations

* **ASR misrecognition** (e.g., Whisper mishears technical terms).

  * Mitigation: keep script text as ground truth and snap ASR timings to script tokens.
* **Extra runtime cost** (minutes per video).

  * Mitigation: make Whisper stage opt-in.
* **Drift between script and human recording.**

  * Mitigation: allow “tolerant alignment” — if ASR diverges, fall back to script-based timing.

---

✅ **Summary:**

* Default = Baseline subtitles (fast, reproducible).
* Whisper alignment = optional, Phase 4+ polish mode.
* Hooks (config + CLI) are scaffolded now so no redesign later.
