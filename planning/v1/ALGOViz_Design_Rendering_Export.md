# ALGOViz Design Doc — Rendering & Export Pipeline

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
Define the end-to-end pipeline that turns a **Storyboard + Director run** into final **media artifacts** (MP4, GIF, PNG frame sequences, SRT subtitles, JSON sidecars). Provide clear configuration knobs for quality, deterministic outputs for CI, and safe failure behavior.

## 2. Non‑Goals
- Scene authoring and beat sequencing (handled by **Storyboard** and **Director**).
- Algorithm semantics (handled by **Adapters & VizEvents**).
- Voice synthesis (handled by **Voiceover Integration**).

## 3. Responsibilities
1. Convert Director output (a Scene/Sequence) into **frames**.
2. Encode frames into **video/gif** using ffmpeg with reproducible settings.
3. Export **subtitles** from narration (SRT) and **sidecar metadata** (JSON).
4. Support **preview** vs **final** quality modes.
5. Provide **caching** and **incremental** rerenders (act/shot granularity).
6. Expose **observability**: render time, fps achieved, drop frames, I/O stats.

## 4. Architecture Overview

```
Storyboard → Director → Scene/Sequence → Frame Render → Encode → Artifacts
                                     ↘ (TimingTracker) ↘ (SRT/JSON)
```

### Components
- **FrameRenderer**: Uses Manim to render Scene/Sequence into image frames.
- **Encoder**: Wraps ffmpeg; supports MP4 (libx264/libx265), GIF, PNG sequences.
- **SubtitleExporter**: Builds SRT from `Beat.narration` & TimingTracker.
- **MetadataExporter**: Dumps JSON with timing, config, git SHA for provenance.
- **CacheManager**: Content-addressed cache on `(algo, storyboard hash, config)`.

## 5. Data Models

### 5.1 RenderConfig
```python
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

@dataclass
class RenderConfig:
    resolution: tuple[int, int] = (1920, 1080)
    frame_rate: int = 30
    pixel_aspect: float = 1.0
    format: Literal["mp4", "gif", "png_sequence"] = "mp4"
    codec: Literal["libx264", "libx265"] = "libx264"
    crf: int = 18                      # quality for x264/x265 (lower is better)
    preset: Literal["ultrafast","fast","medium","slow","veryslow"] = "medium"
    bitrate: str | None = None         # e.g., "6M" (overrides crf if set)
    keyint: int = 60                   # GOP size (2 sec @30fps)
    faststart: bool = True             # mp4 faststart for web
    output_dir: Path = Path("renders/")
    overwrite: bool = True
    preview: bool = False              # enables draft settings (lower res/fps/crf)
```

### 5.2 ArtifactManifest
```python
@dataclass
class ArtifactManifest:
    video_path: Path | None
    frames_dir: Path | None
    srt_path: Path | None
    metadata_path: Path
```

## 6. Pipeline API

```python
class RenderPipeline:
    def __init__(self, frame_renderer, encoder, subtitle_exporter, metadata_exporter, cache):
        ...

    def render(self, sequence, storyboard, config: RenderConfig, tracking) -> ArtifactManifest:
        # 1) Resolve cache key; short-circuit if hit and overwrite=False.
        # 2) Render frames (act/shot granular caching if available).
        # 3) Encode to requested format.
        # 4) Export SRT (if narration present).
        # 5) Write metadata JSON (timings, config snapshot, git SHA).
        # 6) Return manifest.
        ...

    def render_preview(self, scene, config: RenderConfig) -> ArtifactManifest:
        # Single-shot quick preview for fast iteration
        ...
```

## 7. Rendering Details

### 7.1 Frame Rendering (Manim)
- Use Manim's headless renderer; disable antialias for previews.
- **Determinism**: 
  - Seed random number generators with fixed values
  - Fix floating-point tolerances for consistent positioning
  - **Font pinning**: Ship default font with checksum; verify on load to prevent cross-platform rendering differences
  - Disable font fallback chains that vary by system
- **Chunking**: render at shot granularity; cache per shot using content hash:
  - Hash includes: storyboard YAML, adapter version, scenario, timing mode, theme, render config, font checksum.
- **Parallelism**: optional per-shot parallel rendering (respect CPU/IO).

### 7.2 Encoding (ffmpeg)
> We standardize on ffmpeg encoders `libx264` / `libx265`; the resulting bitstream
> is H.264 / H.265. Avoid bare "h264/h265" in config examples.

- MP4 (libx264/libx265): use `-pix_fmt yuv420p`, `-movflags +faststart` if `faststart`.
- GIF: palette generation for high quality; limit fps for file size.
- PNG sequence: named `frame_%06d.png` for stable lexicographic order.
- **Audio**: if voiceover enabled, mux audio track; set AAC `-b:a 192k` default.

### 7.3 Subtitles
- **Phase 3**: Standard **SRT** sidecar files with `HH:MM:SS,mmm` ranges per narrated beat.
- Beat IDs embedded in comments for traceability.
- **Post-Phase 3**: Optional **burn-in** subtitles via ffmpeg `subtitles` filter (nicety, not core requirement).
- **Source**: SRT timestamps are derived from TimingTracker actuals after hybrid timing execution (not pre-computed estimates)
- **Generation**: Subtitles are generated from narration text combined with actual timing measurements from the rendering process

## 7.4 Subtitles Exporter

The **SubtitleExporter** component handles subtitle generation with two distinct modes for different use cases:

### 7.4.1 Subtitle Modes

**Baseline Mode (Default)**
- Uses TimingTracker actuals from hybrid timing execution
- Fast generation, suitable for drafts and most content
- Timestamps align with beat boundaries from storyboard execution
- No additional dependencies beyond core ALGOViz

**Whisper-Align Mode (Polish)**
- Optional enhancement using Whisper ASR for precise word-level alignment
- Requires Whisper dependency and audio track from voiceover
- Generates more accurate timestamps for professional content
- Fallback to baseline mode if Whisper unavailable

### 7.4.2 Configuration Schema

```yaml
subtitles:
  enabled: true
  mode: baseline       # [baseline | whisper-align]
  format: srt          # [srt | vtt]
  burn_in: false       # burn subtitles into video (optional)
```

### 7.4.3 CLI Usage Examples

```bash
# Basic subtitle export (baseline mode)
agloviz render --algo bfs --scenario maze.yaml --with-subtitles

# Enable whisper alignment for polish
agloviz render --algo bfs --scenario maze.yaml --with-subtitles subtitles.mode=whisper-align

# Burn subtitles into video
agloviz render --algo bfs --scenario maze.yaml --with-subtitles --subtitles-burn-in

# Override format and mode via CLI
agloviz render --algo bfs --scenario maze.yaml --with-subtitles subtitles.format=vtt subtitles.mode=whisper-align
```

### 7.4.4 Output Artifacts

**Baseline Mode Output:**
- `video.srt` - Final subtitle file with beat-aligned timestamps
- `metadata.json` - Includes subtitle generation method and timing source

**Whisper-Align Mode Output:**
- `video.srt.draft` - Initial baseline subtitles (preserved for comparison)
- `video.srt` - Final whisper-aligned subtitles with word-level precision
- `metadata.json` - Includes Whisper model version and alignment metrics

**Burn-in Mode:**
- Video file includes embedded subtitles (no separate .srt file needed)
- Original .srt files still generated for accessibility

### 7.5 Metadata JSON
```json
{
  "version": "1.0.0",
  "git_sha": "abc1234",
  "algo": "bfs",
  "scenario": "maze_small.yaml",
  "timing_mode": "normal",
  "render": {"resolution": [1920,1080], "fps": 30, "codec": "libx264"},
  "durations": {"total_seconds": 76.7, "beats": [{"id":"1-1-2","expected":0.8,"actual":0.83}]}
}
```

## 8. Quality Profiles
| Profile  | Resolution | FPS | CRF | Notes |
|----------|------------|-----|-----|------|
| `draft`  | 1280×720   | 24  | 28  | Fast iteration, lower quality |
| `medium` | 1920×1080  | 30  | 18  | Default |
| `high`   | 2560×1440  | 60  | 16  | Showcase / final |

Profiles map to `RenderConfig` presets.

**Important — Quality vs Timing are independent:** render *quality* controls encoder
fidelity (resolution, fps, CRF), while *timing mode* controls animation pacing.
Changing one does not implicitly change the other.

## 9. CLI Integration
```bash
agloviz render --algo bfs --scenario maze.yaml --format mp4 --quality high --with-voiceover
agloviz preview --algo bfs --scenario maze.yaml --frames 120 --quality draft
agloviz render --algo a_star --scenario maze.yaml --format png_sequence --output-dir out/frames
```

## 10. Testing Strategy
- **Unit**: ensure `RenderConfig` maps to correct ffmpeg args.
- **Integration**: storyboard → frames → mp4; assert duration within epsilon.
- **Regression**: frame diff (SSIM/PSNR) against golden frames (tolerances for antialias).
- **Subtitles**: timestamps monotonic; non-overlapping ranges.
- **Cache**: identical inputs hit cache; change in storyboard hash invalidates.

## 11. Performance & Caching
- Cache key = SHA256 of (algo, storyboard, scenario, timing, theme, render profile).
- Reuse previously rendered shots; only re-encode video if needed.
- Optionally compress frame cache with Zstd.

## 12. Failure Modes & Handling
- Missing ffmpeg → actionable error with install hint.
- Disk full → fail fast, suggest `--output-dir` or clean cache.
- Codec not supported → fallback to libx264; warn.
- Subtitle export fails → continue with video, emit warning.

## 13. Observability
- Log per-act/shot render time, fps, encode bitrate, final size.
- Emit metrics to JSON for CI dashboards.

## 14. Security & Licensing
- Ensure fonts and audio assets used are licensed.
- When muxing audio, include license text in metadata if required.

## 15. Open Questions
- Per-OS encoding defaults (Windows/macOS/Linux)?
- Hardware encoders (NVENC/VAAPI) opt-in?

---
