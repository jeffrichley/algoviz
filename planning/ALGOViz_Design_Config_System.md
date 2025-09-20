# ALGOViz Design Doc — Configuration System

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
Provide a single, validated **configuration tree** that governs scenarios, timing, themes, voiceover, and rendering. Ensure predictable precedence: **defaults → YAML → CLI → env (optional)**, and produce a canonical merged config for reproducibility.

## 2. Non‑Goals
- UI theme design details (handled by Themes doc).
- Video encoding specifics (Render Pipeline doc).

## 3. Requirements
- Strong typing and validation (Pydantic).
- Helpful errors with file/line context.
- Merging strategy with explicit precedence.
- Ability to **dump merged config** for artifact reproducibility.

## 4. Configuration Layers
1. **Defaults** baked into models.
2. **YAML files** (scenario/theme/timing/voice/render).
3. **CLI overrides**.
4. **Environment variables** (optional; namespaced).

## 5. Data Model

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Tuple

class ScenarioConfig(BaseModel):
    name: str
    grid_file: str                 # path to grid/maze YAML
    start: Tuple[int,int]
    goal: Tuple[int,int]
    obstacles: list[Tuple[int,int]] = []
    weighted: bool = False

class ThemeConfig(BaseModel):
    name: str = "default"
    colors: dict[str, str] = Field(default_factory=dict)  # role -> hex

class VoiceoverConfig(BaseModel):
    enabled: bool = False
    backend: Literal["coqui"] = "coqui"  # CoquiTTS is the default backend
    lang: str = "en"
    voice: str = "en_US"
    speed: float = 1.0

class SubtitlesConfig(BaseModel):
    enabled: bool = False
    mode: Literal["baseline", "whisper-align"] = "baseline"
    format: Literal["srt", "vtt"] = "srt"
    burn_in: bool = False

class RenderConfig(BaseModel):
    resolution: Tuple[int,int] = (1920,1080)
    frame_rate: int = 30
    quality: Literal["draft","medium","high"] = "medium"
    format: Literal["mp4","gif","png_sequence"] = "mp4"

class TimingConfig(BaseModel):
    mode: Literal["draft","normal","fast"] = "normal"
    ui: float = 1.0           # UI transition timing bucket
    events: float = 0.8       # Algorithm event timing bucket  
    effects: float = 0.5      # Visual effects timing bucket
    waits: float = 0.5        # Wait/pause timing bucket
    multipliers: dict[str, float] = {"draft": 0.5, "normal": 1.0, "fast": 0.25}
    # Supports hybrid timing: narration duration takes precedence when longer than base timing

class VideoConfig(BaseModel):
    scenario: ScenarioConfig
    theme: ThemeConfig = ThemeConfig()
    voiceover: VoiceoverConfig = VoiceoverConfig()
    subtitles: SubtitlesConfig = SubtitlesConfig()
    render: RenderConfig = RenderConfig()
    timing: TimingConfig = TimingConfig()
```

## 6. ConfigManager

```python
class ConfigManager:
    def load(self, *yaml_paths: str) -> VideoConfig:
        # parse YAMLs, merge into defaults
        ...

    def apply_cli_overrides(self, cfg: VideoConfig, **overrides) -> VideoConfig:
        ...

    def apply_env(self, cfg: VideoConfig, prefix="AGLOVIZ_") -> VideoConfig:
        ...

    def validate(self, cfg: VideoConfig) -> None:
        # pydantic validation + custom cross-field checks
        ...

    def dump(self, cfg: VideoConfig, path: str) -> None:
        # write merged config for reproducibility
        ...
```

### Precedence Rules (highest wins)
1. CLI overrides (`--render.quality high`).
2. Env vars (`AGLOVIZ_RENDER_QUALITY=high`).
3. YAML files (in order passed; later wins).
4. Defaults.

Related: See **Scenario/Theme Merge Precedence** (ALGOViz_Scenario_Theme_Merge_Precedence.md) for a concrete example
of merging scenario.yaml + timing.yaml + theme.yaml with CLI overrides, including a before/after snippet.

## 7. Example YAMLs

### scenario.yaml
```yaml
scenario:
  name: "maze_small"
  grid_file: "grids/maze_small.yaml"
  start: [0,0]
  goal: [9,9]
  obstacles: []
```

### timing.yaml
```yaml
timing:
  mode: normal
  ui: 1.0
  events: 0.8
  effects: 0.5
  waits: 0.5
```

### voiceover.yaml
```yaml
voiceover:
  enabled: false
  backend: coqui
  lang: en
  voice: en_US
  speed: 1.0
```

### subtitles.yaml
```yaml
subtitles:
  enabled: true
  mode: baseline
  format: srt
  burn_in: false
```

## 8. CLI Override Example: Subtitle Mode Enhancement

**Base Configuration (subtitles.yaml):**
```yaml
subtitles:
  enabled: true
  mode: baseline
  format: srt
```

**CLI Override:**
```bash
agloviz render --algo bfs --scenario maze.yaml --with-subtitles subtitles.mode=whisper-align
```

**Merged Result:**
```yaml
subtitles:
  enabled: true
  mode: whisper-align  # CLI override applied
  format: srt
  burn_in: false       # default value
```

This demonstrates how CLI flags can upgrade subtitle generation from fast baseline mode to high-quality whisper alignment without modifying configuration files.

## 9. Integration
- CLI loads YAML(s), applies CLI/env, validates, and passes a **fully formed VideoConfig** to Director/RenderPipeline.
- Director should rely on **config accessors** only, never raw YAML.

## 10. Testing Strategy
- Unit: precedence and merge correctness.
- Property: invalid configs surface actionable errors.
- Snapshot: dumping merged config produces stable output.

## 11. Failure Modes
- Unknown keys → fail with exact path (`timing.fooo`).
- Type mismatch → show expected/actual types and file location.
- Missing required fields (e.g., `scenario.start`) → fail fast.

## 12. Observability
- CLI flag `--dump-config merged.yaml` to store merged config with artifacts.

## 13. Open Questions
- Support for **includes** (YAML anchors, file imports)?
- Config profiles (teaching vs prod) as preset bundles?

---


