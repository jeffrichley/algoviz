# ALGOViz Design Doc — Dependency Injection (DI) Strategy

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

> This document specifies **how ALGOViz constructs and wires objects** (adapters, director, widgets, voiceover engines, pipelines) using **configuration-driven dependency injection** built on **Hydra + hydra‑zen + OmegaConf**. It is intentionally more detailed than any other doc because DI failures can silently degrade quality and developer experience.

---

## 1. Problem Statement & Goals

**Problem.** ALGOViz is highly modular (Storyboard DSL, Director, Adapters, Widgets, Voiceover, Rendering). Without a disciplined construction pattern, we risk:
- Hard-coded dependencies (tight coupling)
- Brittle test setups
- Unclear swap points (e.g., voiceover backend, renderer engine)
- Configuration sprawl and inconsistent overrides

**Goal.** Provide a **configuration-first DI approach** that:
1. **Instantiates** objects from config (classes/functions) via `_target_`.
2. **Wires** nested dependencies (e.g., Director → VoiceoverEngine → CoquiTTS).
3. **Swaps** implementations via YAML/CLI (no code changes).
4. **Scopes** object lifetimes (singleton vs per-run vs per-act/per-shot).
5. **Validates** config → objects with clear errors.
6. **Works with plugins** and matches our testing + CI needs.

**Non-Goals.**
- Full enterprise DI container with AOP, interceptors, or reflection-based injection.
- Runtime mutation of the graph beyond documented scopes.

---

## 2. Technology Choices

- **Hydra**: config composition & runtime **instantiation** (`hydra.utils.instantiate`).
- **hydra‑zen**: ergonomic helpers to **build structured configs for callables/classes**, recursive instantiation, and integration with type hints.
- **OmegaConf**: hierarchical config store, deep merge from multiple YAMLs + CLI overrides.
- **Pydantic** (v1 or v2): **final validation** of merged config trees (schema + cross-field checks).

> Design stance: **Load/Merge with OmegaConf → Instantiate with hydra‑zen/Hydra → Validate models with Pydantic where applicable** (e.g., ScenarioConfig, TimingConfig).

---

## 3. Object Graph Overview

The “canonical” graph (top-level run):

```
VideoRun (ephemeral)
└─ Director (per-run)
   ├─ Storyboard (immutable; parsed)
   ├─ TimingConfig (immutable; validated)
   ├─ VoiceoverEngine (optional; per-run or per-act)
   ├─ ComponentRegistry (singleton-ish; factories and registrations)
   ├─ AlgorithmAdapter (per-run, bound to Scenario)
   ├─ RenderPipeline (per-run)
   │  ├─ FrameRenderer (per-run)
   │  ├─ Encoder (per-run)
   │  ├─ SubtitleExporter (per-run)
   │  └─ MetadataExporter (per-run)
   └─ ScenarioRuntime (per-run; provides neighbors(), etc.)
```

**Scopes.**
- **Singleton** (process): `ComponentRegistry` registrations, PluginManager, Config schema definitions.
- **Per‑run**: Director, Adapter, VoiceoverEngine, RenderPipeline.
- **Per‑act/shot** (optional): transient widget instances, temporary voiceover contexts.

---

## 4. Config-Driven Instantiation (Hydra Core)

Hydra uses `_target_` to point at a Python import path. hydra‑zen wraps this with `builds` to infer parameters from signatures.

### 4.1 Example: Director & Dependencies

```yaml
# config/run.yaml
director:
  _target_: agloviz.core.director.Director
  storyboard: ${storyboard}
  timing: ${timing}
  registry: ${registry}
  voiceover: ${voiceover}          # may be null if with_voiceover=false
  mode: ${timing.mode}
  with_voice: ${voiceover.enabled}

storyboard:
  _target_: agloviz.core.storyboard.load_storyboard
  path: "storyboards/bfs_default.yaml"

timing:
  _target_: agloviz.config.timing.make_timing_config
  mode: "normal"

voiceover:
  _target_: agloviz.voice.coqui.CoquiTTS
  enabled: false
  lang: "en"
  voice: "en_US"
  speed: 1.0

registry:
  _target_: agloviz.core.registry.build_component_registry
  plugins: ${plugins}

plugins:
  _target_: agloviz.plugins.manager.PluginManager
  search_entry_points: true
  plugin_dirs: ["./plugins"]
```

Invoked from code:

```python
from hydra_zen import instantiate

def main(cfg):  # cfg is an OmegaConf tree
    director = instantiate(cfg.director)  # recursively instantiates sub-objects
    director.run()
```

### 4.2 CLI Overrides (DI-friendly)

```bash
# Switch voiceover on and change voice + speed
agloviz render -a bfs -s maze.yaml   voiceover.enabled=true voiceover.voice=en_US_male_1 voiceover.speed=0.95
```

Hydra composes and instantiates the updated object graph.

---

## 5. hydra‑zen “builds” Patterns

hydra‑zen provides `builds(MyClass, ...)` to produce a config schema that mirrors the constructor signature.

```python
# di/builders.py
from hydra_zen import builds
from agloviz.core.director import Director
from agloviz.voice.coqui import CoquiTTS
from agloviz.core.registry import build_component_registry

DirectorConf = builds(Director, populate_full_signature=True)
VoiceoverConf = builds(CoquiTTS, populate_full_signature=True)
RegistryConf = builds(build_component_registry, populate_full_signature=True)
```

Now you can store these **typed** configs in Hydra’s ConfigStore and compose safely. This also enables IDE autocomplete for config fields and reduces typo risks.

---

## 6. Scopes & Lifecycles

We explicitly define lifetimes to avoid accidental singleton leaks or expensive re-instantiates.

| Component            | Scope      | Rationale |
|---------------------|------------|-----------|
| PluginManager       | Singleton  | Scanning is costly; results cached. |
| ComponentRegistry   | Singleton* | Registration of factories is static; instances created per‑run. |
| Director            | Per‑run    | Holds run state (acts/shots). |
| AlgorithmAdapter    | Per‑run    | Bound to Scenario; deterministic event stream. |
| VoiceoverEngine     | Per‑run    | Manages TTS model cache; per‑act contexts inside. |
| RenderPipeline      | Per‑run    | Holds run-level RenderConfig; idempotent across runs. |
| Widgets (instances) | Per‑shot   | Enter/exit animations; no cross‑shot state. |
| ScenarioRuntime     | Per‑run    | Provides neighbors(), validates scenario. |

\* **ComponentRegistry**: the registry object is process-singleton for **registrations**; `get(name)` returns **new instances** per run/shot as needed.

**Implementation.** A tiny DI/lifecycle helper provides a **Context** object:

```python
class Context:
    def __init__(self):
        self._singletons = {}

    def singleton(self, key, factory):
        if key not in self._singletons:
            self._singletons[key] = factory()
        return self._singletons[key]
```

Hydra instantiation can hand in `Context` where needed (e.g., to `build_component_registry`).

---

## 7. Construction Strategies

### 7.1 Pure `_target_` Graphs (Simple)
Everything is `_target_` and recursively instantiates. Minimal code, fast iteration.

**Pros**: Simple mental model; CLI overrides work everywhere.  
**Cons**: Harder to inject fakes in deep nodes without named anchors; lifecycle policies ad‑hoc.

### 7.2 Factory + `_target_` Hybrid (Recommended)
Top-level objects are `_target_`; complex children use **factories** that know about lifecycles and caching.

Example: `build_component_registry` registers widget **factories**; Director asks for instances per shot. This makes widgets cheap to swap and easy to test.

### 7.3 Provider Objects (Advanced)
Introduce **Provider** interfaces when creation is non-trivial (e.g., GPU‑backed TTS with warmup). Providers expose `get()` and handle caching.

---

## 8. Validation Pipeline

We separate concerns:
1. **OmegaConf/Hydra**: load + merge YAML + CLI → `cfg` tree.
2. **hydra‑zen/Hydra**: instantiate **objects** per `_target_` and nested configs.
3. **Pydantic**: validate **domain models** (ScenarioConfig, TimingConfig, VoiceoverConfig).

Example:

```python
from pydantic import BaseModel

class ScenarioModel(BaseModel):
    grid_file: str
    start: tuple[int,int]
    goal: tuple[int,int]

def make_scenario_runtime(cfg) -> "ScenarioRuntime":
    model = ScenarioModel(**cfg)  # raises on invalid
    return ScenarioRuntime.from_model(model)
```

> Rule: **Object boundaries** are the validation gates. Fail fast with clear messages (include originating YAML filename and pointer).

---

## 9. Error Handling & Diagnostics

**Classification & Guidance**
- **Instantiation error**: `_target_` import path missing or constructor error.  
  - Message: `Failed to instantiate VoiceoverEngine (agloviz.voice.coqui.CoquiTTS): No module named 'coqittts'`  
  - Action: verify dependency, plugin, or import path.

- **Wiring error**: missing sub-config or type.  
  - Message: `Director.voiceover expected VoiceoverEngine, got dict at 'voiceover'`  
  - Action: check config node/override; show offending path `director.voiceover`.

- **Validation error (Pydantic)**: field type mismatch or cross-field check fail.  
  - Message: `ScenarioConfig.goal must be in-bounds; got [100,100] for grid 10x10`  
  - Action: point to `scenario.yaml:line`, show values.

**Traceability**
- Always include `Act/Shot/Beat` context when errors occur at runtime.
- Emit a **construction report** (optional): JSON of `_target_` tree, concrete types, and resolved parameters.

---

## 10. Testing the DI Graph

**Unit Tests**
- Instantiate isolated nodes with minimal configs, assert types and defaults.
- Mock factories/providers to simulate heavy deps (e.g., Coqui warmup).

**Integration Tests**
- Compose a full run with a tiny storyboard; verify that `Director`, `Adapter`, `VoiceoverEngine`, and `RenderPipeline` instantiate and interact.

**Golden DI Snapshots**
- Serialize instantiated graph (type names + parameter hashes) to a snapshot; diff on PRs to detect unintended DI changes.

**Fault Injection**
- Intentionally break `_target_` path or remove a sub-node; ensure error messages are crisp and actionable.

---

## 11. Namespacing & Plugins

Plugins register into the same DI world without stepping on core.

- **Action names**: `pkg_name.action_name` in the registry.
- **Widget names**: `pkg_name.widget_name` in ComponentRegistry.
- **Algorithm keys**: `pkg_name.algo` to avoid collisions.
- **Assets**: `pkg://pkg_name/path` resolution in loaders.
- **File naming**: All ALGOViz design documents and core config files use the `ALGOViz_` prefix for consistency

Hydra configs shipped by plugins can be discovered and composed (e.g., `+my_pkg/a_star.yaml`).

---

## 12. Example: Two Swappable Voiceover Engines

**YAML**

```yaml
# voiceover/coqui.yaml
voiceover:
  _target_: agloviz.voice.coqui.CoquiTTS
  enabled: true
  lang: "en"
  voice: "en_US"
  speed: 1.0

# voiceover/recorder.yaml
voiceover:
  _target_: agloviz.voice.recorder.RecorderService
  enabled: true
  input_wav: "tracks/teacher.wav"
```

**CLI**

```bash
agloviz render -a bfs -s maze.yaml --config voiceover/recorder.yaml
```

No code change; Director receives a different implementation.

---

## 13. Example: Widget Registry via DI Factories

```python
# core/registry.py
def build_component_registry(plugins) -> "ComponentRegistry":
    reg = ComponentRegistry()
    # Core
    reg.register("grid", lambda: GridWidget())
    reg.register("queue", lambda: QueueWidget())
    reg.register("legend", lambda: LegendWidget())
    # Plugins
    for wname, factory in plugins.widget_factories():
        reg.register(wname, factory)
    return reg
```

**Storyboard beat → Director** asks registry for instances per shot.

---

## 14. Lifecycle Tuning (Singleton vs Per-run vs Transient)

We guide authors with **policy**:

- **Singleton**: pure registries, static data, caches safe to share.  
- **Per‑run**: anything that depends on the scenario or run config (Director, Adapter, Pipeline).  
- **Transient**: visual elements attached to a shot/act; impacts animation lifecycle and memory.

**Anti-patterns**
- Don’t make a widget instance a singleton; state bleeds across shots.
- Don’t pass OmegaConf nodes deep into runtime objects; materialize typed objects first.

---

## 15. Performance Considerations

- **Warmup** heavy services (e.g., TTS model) at DI time to amortize cost; expose an async `prewarm()` if needed.  
- **Memoize** common constructions keyed by config hash in test/CI to speed up repeat runs.  
- Prefer factory return of **lightweight** objects for per-shot usage.

---

## 16. Security & Trust Model

- Plugins run code on import; provide `--no-plugins` mode.  
- Allow **allowlist** / **blocklist** of plugin packages in config.  
- Voiceover engines should never exfiltrate narration unless user opts-in to remote APIs.

---

## 17. Developer Experience Enhancements

- **Config Autocomplete**: using hydra‑zen `builds(..., populate_full_signature=True)` and typed stubs.  
- **Explain** command (future): `agloviz di-explain` prints the resolved `_target_` graph with source files/line numbers.  
- **Docstrings to Config**: surface constructor docstrings in CLI help for config fields.

---

## 18. Migration Plan (from current codebase)

**Phase 0 (Scaffold)**
- Introduce `_target_`-based configs for Director, Voiceover, Registry.  
- Wrap existing constructors; no behavior change.

**Phase 1 (Adapters/Widgets)**
- Migrate BFSAdapter and core widgets to DI-managed factories.  
- Remove direct imports from monolithic scenes; use registry.

**Phase 2 (Rendering/Plugins)**
- RenderPipeline via DI; add PluginManager to registry build.  
- Provide example plugin with alternative widget.

**Phase 3 (Voiceover Full)**
- Enable Coqui via DI; hybrid timing validated against DI graph.

**Phase 4+**
- Optional providers for persistence, telemetry, and hot-reload.

---

## 19. Reference Code Skeleton

```python
# main.py
from hydra_zen import instantiate
from omegaconf import OmegaConf

def run(cfg):
    director = instantiate(cfg.director)
    return director.run()

if __name__ == "__main__":
    # Hydra's @hydra.main typically wraps this; sketch only
    cfg = OmegaConf.load("config/run.yaml")
    run(cfg)
```

```python
# voice/coqui.py
class CoquiTTS:
    def __init__(self, enabled: bool, lang: str, voice: str, speed: float):
        self.enabled = enabled
        # lazy-load model if enabled
```

```python
# core/director.py
class Director:
    def __init__(self, storyboard, timing, registry, voiceover=None, mode="normal", with_voice=False):
        self.storyboard = storyboard
        self.timing = timing
        self.registry = registry
        self.voiceover = voiceover if with_voice else None
```

---

## 20. Open Questions

1. **DI Scopes beyond per-run?** Do we want explicit per‑act scopes for certain services (e.g., localized TTS voice)?  
2. **Explainability tooling**: ship a `di-explain` command early?  
3. **Pydantic v2** migration path with `BaseModel` validation at DI boundaries?  
4. **Hydra job directories**: adopt or override to our `renders/` layout?

---

# ✅ Summary

This DI Strategy gives ALGOViz a **config-first, testable, and swappable** construction plan using **Hydra + hydra‑zen + OmegaConf + Pydantic**. It formalizes object **lifecycles**, encourages **factory-based** registry patterns, and lays out **error handling, testing, and plugin namespacing**. With this in place, we can add/replace core components (adapters, widgets, renderers, voiceover engines) **without touching core code**, ensuring long-term maintainability and a world-class developer experience.
