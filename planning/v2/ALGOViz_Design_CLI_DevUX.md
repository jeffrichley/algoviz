# ALGOViz Design Doc — CLI & Developer UX

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
Deliver a **world‑class command‑line interface** for educators, creators, and contributors to render, preview, test, and extend ALGOViz. Emphasize clarity, speed, and great error messages.

## 2. Non‑Goals
- GUI application (future possibility).
- IDE integration (out of scope).

## 3. Principles
- **Predictable defaults** (silent unless `--with-voiceover`, `quality=medium`).  
- **Short commands** for common tasks, **rich help** for depth.  
- **Actionable errors** with Act/Shot/Beat context.  
- **Deterministic outputs** for CI and reproducibility.  

## 4. Framework
- Implemented with **Typer**.
- Colorized output via Rich.
- Autocompletion scripts for bash/zsh/fish.

## 5. Commands & Flags

### 5.1 `agloviz algo list`
- Lists available algorithms (core + plugins), shows adapter version and routing availability.

### 5.2 `agloviz render`
```
agloviz render --algo bfs --scenario config/scenarios/maze.yaml                --quality high --format mp4 --with-voiceover                --output-dir out/videos --dump-config out/merged.yaml
```
**Flags**
- `--algo, -a`: algorithm key (supports namespaces `pkg.algo`).
- `--scenario, -s`: YAML path.
- `--quality`: `draft|medium|high`.
- `--timing-mode`: `draft|normal|fast`.
- `--format`: `mp4|gif|png_sequence`.
- `--with-voiceover`: enable TTS (Coqui).
- `--voice-lang`, `--voice`, `--voice-speed`.
- `--with-subtitles`: emit .srt sidecar by default.
- `--subtitles-burn-in`: burn SRT into the video via ffmpeg (off by default).
- `subtitles.mode=whisper-align`: enable alignment pass for enhanced timing precision.
- `--bookmarks-log`: log literal-word bookmark hits during narration.
- `--output-dir`: artifact directory.
- `--dump-config`: write merged config.
- `--debug`: verbose logs.

> **💡 Subtitles Behavior**: Subtitles are **silent by default** and only emitted when explicitly requested with `--with-subtitles`. This ensures clean output directories unless subtitle generation is intentionally enabled.

> **�� Tip**: `--quality` and `--timing-mode` are **independent**:
> - **Quality** affects encode/output fidelity (resolution, bitrate, compression)
> - **Timing** affects animation pacing (how fast beats play)
> 
> Example: `--quality high --timing-mode fast` = beautiful video, quick pacing

**Important — Quality vs Timing are independent:** render *quality* controls encoder
fidelity (resolution, fps, CRF), while *timing mode* controls animation pacing.
Changing one does not implicitly change the other.

### 5.3 `agloviz preview`
- Quick low‑res render of first N frames or first act.
```
agloviz preview -a bfs -s maze.yaml --frames 180 --quality draft
```

### 5.4 `agloviz test`
- Runs golden regression tests: renders to frames, compares SSIM/PSNR.
```
agloviz test --golden tests/golden/bfs.yaml --update-golden
```

### 5.5 `agloviz plugins`
- `agloviz plugins list` — show plugin status, versions, entry points.  
- `agloviz plugins verify` — dry‑run load and smoke test.

### 5.6 `agloviz config`
- `agloviz config validate path.yaml`
- `agloviz config dump --out merged.yaml`

## 6. Developer Workflow (Happy Path)
1. Create adapter `MyAlgoAdapter` → deterministic `VizEvent`s.
2. Add widgets if necessary; register in registry.
3. Author storyboard YAML with beats + (optional) narration.
4. Run `agloviz preview` to iterate quickly.
5. Commit storyboards/config; PR triggers `agloviz test` in CI.
6. After approval, `agloviz render` with `--quality high` for final deliverable.

## 7. Error Messaging
- Unknown action: `Unknown action "trace_paht" at Act 2 / Shot 1 / Beat 3 (typo?)`
- Adapter crash: show algorithm name, step index, and suggest minimal repro.
- Config error: show file:line and offending key/type.

## 8. Telemetry & Logs
- Optional `--metrics out.json` writes render metrics (time, frames, bitrate).
- `--profile` prints slowest beats (hotspots for optimization).

## 9. CI/CD Integration
- GitHub Actions recipe: cache frames, produce preview GIFs, upload artifacts.
- Status checks: config validate, unit tests, golden render diffs.

## 10. Security & Safety
- `--no-plugins` disables plugin discovery.
- Warn if loading unverified plugins; show source package.

## 11. Internationalization
- `--locale` switches narration language (when external narration files exist).

## 12. Open Questions
- Interactive stepping through beats (`--interactive`)?
- Batch rendering (`--all-scenarios`, `--all-algos`)?

---
