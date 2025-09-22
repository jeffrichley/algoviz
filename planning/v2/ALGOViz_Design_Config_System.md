# ALGOViz Design Doc — Configuration System v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0 - Hydra-zen First)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Updated for Hydra-zen First Philosophy)
**Supersedes:** planning/v1/ALGOViz_Design_Config_System.md

---

## 1. Purpose
Provide a single, validated **configuration tree** that governs scenarios, timing, themes, voiceover, and rendering using **hydra-zen first** architecture. Ensure predictable precedence: **defaults → YAML → CLI → env (optional)**, and produce a canonical merged config for reproducibility through Hydra's structured configuration system.

## 2. Non‑Goals
- UI theme design details (handled by Themes doc).
- Video encoding specifics (Render Pipeline doc).

## 3. Requirements
- **Hydra-zen first** architecture with structured configs and ConfigStore
- Strong typing and validation (Pydantic + hydra-zen).
- Helpful errors with file/line context through Hydra's validation.
- Merging strategy with explicit precedence via Hydra composition.
- Ability to **dump merged config** for artifact reproducibility.
- Configuration composition and template support via hydra-zen.

## 4. Configuration Layers
1. **Defaults** baked into structured config templates via ConfigStore.
2. **YAML files** (scenario/theme/timing/voice/render) using Hydra composition.
3. **CLI overrides** via Hydra's override syntax.
4. **Environment variables** (optional; namespaced) via Hydra.

## 5. Data Model (Hydra-zen First)

### 5.1 Pydantic Validation Models
```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Tuple

# Pydantic models for validation - these define the data structure
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
    multipliers: dict[str, float] = Field(default_factory=lambda: {"draft": 0.5, "normal": 1.0, "fast": 0.25})
    # Supports hybrid timing: narration duration takes precedence when longer than base timing

class VideoConfig(BaseModel):
    scenario: ScenarioConfig
    theme: ThemeConfig
    voiceover: VoiceoverConfig
    subtitles: SubtitlesConfig
    render: RenderConfig
    timing: TimingConfig
```

### 5.2 Hydra-zen Structured Configs
```python
from hydra_zen import builds, make_config, instantiate
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig

# Create structured configs using builds() - these are the hydra-zen templates
ScenarioConfigZen = builds(
    ScenarioConfig,
    name="${scenario.name}",
    grid_file="${scenario.grid_file}",
    start="${scenario.start}",
    goal="${scenario.goal}",
    obstacles="${scenario.obstacles:[]}",
    weighted="${scenario.weighted:false}",
    zen_partial=True,
    populate_full_signature=True
)

ThemeConfigZen = builds(
    ThemeConfig,
    name="${theme.name:default}",
    colors="${theme.colors:{}}",
    zen_partial=True,
    populate_full_signature=True
)

VoiceoverConfigZen = builds(
    VoiceoverConfig,
    enabled="${voiceover.enabled:false}",
    backend="${voiceover.backend:coqui}",
    lang="${voiceover.lang:en}",
    voice="${voiceover.voice:en_US}",
    speed="${voiceover.speed:1.0}",
    zen_partial=True,
    populate_full_signature=True
)

SubtitlesConfigZen = builds(
    SubtitlesConfig,
    enabled="${subtitles.enabled:false}",
    mode="${subtitles.mode:baseline}",
    format="${subtitles.format:srt}",
    burn_in="${subtitles.burn_in:false}",
    zen_partial=True,
    populate_full_signature=True
)

RenderConfigZen = builds(
    RenderConfig,
    resolution="${render.resolution:[1920,1080]}",
    frame_rate="${render.frame_rate:30}",
    quality="${render.quality:medium}",
    format="${render.format:mp4}",
    zen_partial=True,
    populate_full_signature=True
)

TimingConfigZen = builds(
    TimingConfig,
    mode="${timing.mode:normal}",
    ui="${timing.ui:1.0}",
    events="${timing.events:0.8}",
    effects="${timing.effects:0.5}",
    waits="${timing.waits:0.5}",
    multipliers="${timing.multipliers:{draft: 0.5, normal: 1.0, fast: 0.25}}",
    zen_partial=True,
    populate_full_signature=True
)

# Main video configuration using composition
VideoConfigZen = make_config(
    scenario=ScenarioConfigZen,
    theme=ThemeConfigZen,
    voiceover=VoiceoverConfigZen,
    subtitles=SubtitlesConfigZen,
    render=RenderConfigZen,
    timing=TimingConfigZen,
    hydra_defaults=["_self_"]
)
```

### 5.3 ConfigStore Registration
```python
def register_configs():
    """Register all configuration templates with ConfigStore"""
    cs = ConfigStore.instance()
    
    # Register individual config sections
    cs.store(name="scenario_base", node=ScenarioConfigZen)
    cs.store(name="theme_base", node=ThemeConfigZen)
    cs.store(name="voiceover_base", node=VoiceoverConfigZen)
    cs.store(name="subtitles_base", node=SubtitlesConfigZen)
    cs.store(name="render_base", node=RenderConfigZen)
    cs.store(name="timing_base", node=TimingConfigZen)
    
    # Register main video configuration
    cs.store(name="video_config", node=VideoConfigZen)
    
    # Register common presets
    cs.store(group="scenario", name="maze_small", node=builds(
        ScenarioConfig,
        name="maze_small",
        grid_file="grids/maze_small.yaml",
        start=[0, 0],
        goal=[9, 9],
        obstacles=[],
        zen_partial=True
    ))
    
    cs.store(group="timing", name="draft", node=builds(
        TimingConfig,
        mode="draft",
        ui=0.5,
        events=0.4,
        effects=0.25,
        waits=0.25,
        zen_partial=True
    ))
    
    cs.store(group="timing", name="fast", node=builds(
        TimingConfig,
        mode="fast",
        ui=0.25,
        events=0.2,
        effects=0.1,
        waits=0.1,
        zen_partial=True
    ))
```

## 6. ConfigManager (Hydra-zen Integration)

```python
from hydra_zen import instantiate
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig, OmegaConf
import hydra

class ConfigManager:
    def __init__(self):
        # Register all configs on initialization
        register_configs()
    
    @hydra.main(version_base=None, config_path="configs", config_name="video_config")
    def load_with_hydra(self, cfg: DictConfig) -> VideoConfig:
        """Load configuration using Hydra's composition system"""
        # Instantiate the configuration using hydra-zen
        video_config = instantiate(cfg)
        
        # Validate using Pydantic
        if not isinstance(video_config, VideoConfig):
            video_config = VideoConfig(**OmegaConf.to_container(cfg, resolve=True))
        
        return video_config
    
    def load_from_config(self, cfg: DictConfig) -> VideoConfig:
        """Load configuration from a DictConfig (for programmatic use)"""
        # Instantiate using hydra-zen
        video_config = instantiate(cfg)
        
        # Ensure Pydantic validation
        if not isinstance(video_config, VideoConfig):
            video_config = VideoConfig(**OmegaConf.to_container(cfg, resolve=True))
        
        return video_config

    def validate(self, cfg: VideoConfig) -> None:
        """Validate configuration (Pydantic handles this automatically)"""
        # Pydantic validation happens during instantiation
        # Additional cross-field validation can be added here
        pass
    
    def dump(self, cfg: DictConfig, path: str) -> None:
        """Write resolved configuration for reproducibility"""
        resolved_cfg = OmegaConf.to_yaml(cfg, resolve=True)
        with open(path, 'w') as f:
            f.write(resolved_cfg)
    
    def get_config_from_store(self, name: str, group: Optional[str] = None) -> DictConfig:
        """Retrieve configuration template from ConfigStore"""
        cs = ConfigStore.instance()
        if group:
            config_name = f"{group}/{name}"
        else:
            config_name = name
        
        repo = cs.get_repo()
        config_result = repo[config_name]
        return config_result.node
```

### Precedence Rules (highest wins) - Hydra Native
1. CLI overrides (`--render.quality=high` or `render.quality=high`).
2. Hydra composition and overrides in config files.
3. ConfigStore defaults and templates.
4. Built-in defaults in structured configs.

Related: See **Scenario/Theme Merge Precedence** (ALGOViz_Scenario_Theme_Merge_Precedence.md) for a concrete example
of merging scenario.yaml + timing.yaml + theme.yaml with CLI overrides, including a before/after snippet.

## 7. Example Hydra Configuration Files

### config.yaml (Main Configuration)
```yaml
# @package _global_
defaults:
  - scenario: maze_small
  - theme: default
  - timing: normal
  - voiceover: disabled
  - subtitles: disabled
  - render: medium_quality
  - _self_

# Override specific values
scenario:
  name: "custom_maze"
  
timing:
  mode: "normal"
  ui: 1.2
```

### configs/scenario/maze_small.yaml
```yaml
# @package scenario
_target_: agloviz.config.models.ScenarioConfig
  name: "maze_small"
  grid_file: "grids/maze_small.yaml"
start: [0, 0]
goal: [9, 9]
  obstacles: []
weighted: false
```

### configs/timing/normal.yaml
```yaml
# @package timing
_target_: agloviz.config.models.TimingConfig
mode: "normal"
  ui: 1.0
  events: 0.8
  effects: 0.5
  waits: 0.5
multipliers:
  draft: 0.5
  normal: 1.0
  fast: 0.25
```

### configs/voiceover/enabled.yaml
```yaml
# @package voiceover
_target_: agloviz.config.models.VoiceoverConfig
enabled: true
backend: "coqui"
lang: "en"
voice: "en_US"
  speed: 1.0
```

### configs/subtitles/whisper.yaml
```yaml
# @package subtitles
_target_: agloviz.config.models.SubtitlesConfig
  enabled: true
mode: "whisper-align"
format: "srt"
  burn_in: false
```

## 8. CLI Override Examples with Hydra

### Basic Override
```bash
# Using Hydra's override syntax
agloviz render scenario=maze_small timing=draft render.quality=high

# Using structured override
agloviz render scenario.start=[1,1] scenario.goal=[8,8] timing.mode=fast
```

### Configuration Composition
```bash
# Compose multiple configs
agloviz render scenario=maze_large timing=normal voiceover=enabled subtitles=whisper

# Override composed configs
agloviz render scenario=maze_large timing=normal timing.ui=1.5 render.quality=draft
```

### Advanced Composition Example
**CLI Command:**
```bash
agloviz render scenario=maze_small timing=draft subtitles.mode=whisper-align render.quality=high
```

**Effective Configuration (resolved):**
```yaml
scenario:
  _target_: agloviz.config.models.ScenarioConfig
  name: "maze_small"
  grid_file: "grids/maze_small.yaml" 
  start: [0, 0]
  goal: [9, 9]
  obstacles: []
  weighted: false

timing:
  _target_: agloviz.config.models.TimingConfig
  mode: "draft"
  ui: 0.5
  events: 0.4
  effects: 0.25
  waits: 0.25

subtitles:
  _target_: agloviz.config.models.SubtitlesConfig
  enabled: true
  mode: "whisper-align"  # CLI override applied
  format: "srt"
  burn_in: false

render:
  _target_: agloviz.config.models.RenderConfig
  quality: "high"  # CLI override applied
  resolution: [1920, 1080]
  frame_rate: 30
  format: "mp4"
```

## 9. Integration with Hydra-zen

### Director Integration
```python
@hydra.main(version_base=None, config_path="configs", config_name="video_config")
def main(cfg: DictConfig) -> None:
    # Instantiate configuration using hydra-zen
    video_config = instantiate(cfg)
    
    # Pass to Director - Director receives fully validated Pydantic model
    director = Director(video_config)
    director.run()

# Alternative: Programmatic usage
def create_director_from_config(config_overrides: dict = None) -> Director:
    cs = ConfigStore.instance()
    base_config = cs.get_repo()["video_config"].node
    
    if config_overrides:
        # Apply overrides using OmegaConf
        override_config = OmegaConf.create(config_overrides)
        merged_config = OmegaConf.merge(base_config, override_config)
    else:
        merged_config = base_config
    
    # Instantiate and validate
    video_config = instantiate(merged_config)
    return Director(video_config)
```

### RenderPipeline Integration
```python
class RenderPipeline:
    def __init__(self, render_config: RenderConfig):
        self.config = render_config
    
    @classmethod
    def from_hydra_config(cls, cfg: DictConfig) -> 'RenderPipeline':
        """Create RenderPipeline from Hydra configuration"""
        render_config = instantiate(cfg.render)
        return cls(render_config)
```

## 10. Testing Strategy

### Unit Tests
```python
def test_config_instantiation():
    """Test that structured configs instantiate correctly"""
    cs = ConfigStore.instance()
    register_configs()
    
    config = cs.get_repo()["scenario_base"].node
    scenario = instantiate(config, name="test", grid_file="test.yaml", start=[0,0], goal=[1,1])
    
    assert isinstance(scenario, ScenarioConfig)
    assert scenario.name == "test"

def test_config_composition():
    """Test that config composition works correctly"""
    cfg = OmegaConf.create({
        "scenario": {"_target_": "ScenarioConfig", "name": "test", "grid_file": "test.yaml", "start": [0,0], "goal": [1,1]},
        "timing": {"_target_": "TimingConfig", "mode": "draft"}
    })
    
    video_config = instantiate(cfg)
    assert isinstance(video_config["scenario"], ScenarioConfig)
    assert isinstance(video_config["timing"], TimingConfig)
```

### Property Tests
```python
def test_invalid_configs_fail_validation():
    """Test that invalid configurations are caught by Pydantic"""
    with pytest.raises(ValidationError):
        instantiate(builds(ScenarioConfig, start="invalid"))  # Should be tuple
```

### Snapshot Tests
```python
def test_config_dump_stability():
    """Test that dumped configs are stable and reproducible"""
    cfg = OmegaConf.create({"scenario": ScenarioConfigZen})
    
    manager = ConfigManager()
    manager.dump(cfg, "test_output.yaml")
    
    # Load and compare
    loaded = OmegaConf.load("test_output.yaml")
    assert loaded == cfg
```

## 11. Failure Modes (Enhanced with Hydra)

- **Unknown keys** → Hydra fails with exact path (`timing.fooo`) and suggestions.
- **Type mismatch** → Pydantic shows expected/actual types with Hydra context.
- **Missing required fields** → Hydra + Pydantic validation fails fast with clear messages.
- **Invalid _target_** → Hydra-zen instantiate() fails with import/callable errors.
- **Circular references** → OmegaConf detects and reports circular interpolations.

## 12. Observability (Enhanced)

- **CLI flag** `--cfg job` to print resolved configuration.
- **Hydra output directory** contains full resolved config automatically.
- **ConfigStore inspection** via `hydra.core.config_store.ConfigStore.instance().get_repo()`.
- **OmegaConf resolver** integration for custom interpolations.

## 13. Advanced Features

### Custom Resolvers
```python
from omegaconf import OmegaConf

# Register custom resolvers for common patterns
OmegaConf.register_new_resolver("grid_path", lambda name: f"grids/{name}.yaml")
OmegaConf.register_new_resolver("output_path", lambda name: f"output/{name}")

# Usage in config:
# grid_file: ${grid_path:maze_small}  # Resolves to "grids/maze_small.yaml"
```

### Config Templates and Inheritance
```python
# Base template
BaseScenarioTemplate = builds(
    ScenarioConfig,
    weighted=False,
    obstacles=[],
    zen_partial=True
)

# Specialized templates
MazeScenarioTemplate = builds(
    BaseScenarioTemplate,
    grid_file="${grid_path:${scenario.name}}",
    zen_partial=True
)

# Register templates
cs.store(group="scenario_template", name="base", node=BaseScenarioTemplate)
cs.store(group="scenario_template", name="maze", node=MazeScenarioTemplate)
```

## 14. Migration Guide

### From Pure Pydantic to Hydra-zen
1. **Keep existing Pydantic models** for validation
2. **Create structured configs** using `builds()` 
3. **Register with ConfigStore** using appropriate groups
4. **Update instantiation** to use `instantiate()` instead of direct construction
5. **Convert YAML files** to use `_target_` syntax and Hydra composition

### Example Migration
```python
# Before: Pure Pydantic
config = ScenarioConfig(name="test", grid_file="test.yaml", start=[0,0], goal=[1,1])

# After: Hydra-zen
scenario_config = builds(ScenarioConfig, name="test", grid_file="test.yaml", start=[0,0], goal=[1,1])
config = instantiate(scenario_config)
```

## 15. Open Questions

- **Support for includes** → Hydra composition handles this natively
- **Config profiles** → Use Hydra config groups and composition  
- **Runtime config modification** → Use OmegaConf.merge() and re-instantiate
- **Config validation** → Combine Hydra's structural validation with Pydantic's data validation

---


