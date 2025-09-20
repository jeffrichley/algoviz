# ALGOViz Design Doc — Plugin & Extension System

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
Allow external packages to extend ALGOViz (algorithms, widgets, actions, themes, storyboards) **without modifying core code**. Provide robust discovery, versioning, and error isolation.

## 2. Non‑Goals
- Security sandboxing (future; initial model trusts installed plugins).
- Distribution (PyPI publishing guidance is separate).

## 3. Extension Points
- **Algorithms**: provide `AlgorithmAdapter` and optional routing map.
- **Widgets**: implement `Widget` contract and register factory.
- **Actions**: register action name → callable for Storyboard.
- **Themes/Templates**: provide YAML assets.
- **Storyboards**: ship `.yaml` files addressable by name.

## 4. Discovery Mechanisms
1. **Python entry points** (recommended):  
   `pyproject.toml`
   ```toml
   [project.entry-points."agloviz.plugins"]
   my_pkg = "my_pkg.plugins:register"
   ```
2. **Local plugins directory**: `plugins/` scanned at startup.
3. **Config-driven**: `plugins.yaml` with module paths.

## 5. Plugin API
```python
# my_pkg/plugins.py
def register(registry) -> None:
    registry.register_algorithm("a_star", a_star_adapter_factory)
    registry.register_widget("priority_queue", PriorityQueueWidget)
    registry.register_action("celebrate_goal", celebrate_goal_action)
    registry.register_storyboard("a_star_default", "pkg://my_pkg/storyboards/a_star.yaml")
```

- The **registry** exposes `register_algorithm`, `register_widget`, `register_action`, `register_storyboard`, `register_theme`.

## 6. Versioning & Compatibility
- Plugins may declare `requires={"agloviz": ">=1.2,<2.0"}`.
- On load, **PluginManager** performs semver compatibility checks.
- Incompatible plugins are skipped with clear diagnostics.

### Namespacing Rules (Explicit)
- **MANDATORY**: All plugin resources MUST be namespaced by the providing package name
- **Action handlers**: `register_action("my_pkg.trace_path", ...)` 
- **Widget names**: `register_widget("my_pkg.priority_queue", ...)`
- **Algorithm keys**: `register_algorithm("my_pkg.a_star", ...)`
- **Storyboards**: `register_storyboard("my_pkg.a_star_default", ...)`
- **Themes**: `register_theme("my_pkg.dark_mode", ...)`
- The registry enforces uniqueness by full name; non-namespaced registrations are rejected
- Core ALGOViz resources use the "core" namespace implicitly (e.g., "core.bfs", "core.queue")

## 7. Namespacing
- All plugin resources are **namespaced** by package name, e.g., `my_pkg.a_star`.
- **Action names** are namespaced as `pkg.action` in the action registry.
- Prevents collisions: two plugins can both provide an `a_star` storyboard or `celebrate` action under their own namespace.

## 8. Error Isolation
- Plugin load failures:
  - Soft fail with detailed error (traceback trimmed) and continue loading others.
  - Record failures in metadata JSON for reproducibility.
- Optional **quarantine** mode: disable failing plugin next runs until cleared.

## 9. CLI Integration
```bash
agloviz plugins list           # names, versions, entry points, status
agloviz plugins verify         # dry-run: load + sanity checks
agloviz render -a my_pkg.a_star --scenario demo.yaml
```

## 10. Testing & Certification
- Provide a **plugin test harness** library:
  - Validate event determinism for adapters.
  - Validate storyboard schemas.
  - Smoke-render preview frames headless.
- Optionally label plugins as **verified** in `agloviz plugins list`.

## 11. Packaging & Assets
- Plugins can include asset files (YAMLs, images, audio) via standard Python package data.
- Use `pkg://` URIs to reference packaged assets.

## 12. Security Considerations
- Plugins run arbitrary code. Document risk; provide `--no-plugins` safe mode.
- Future: subprocess sandbox or WASI for untrusted sources.

## 13. Open Questions
- Hot reload for local dev (`--reload-plugins`)?
- Configurable plugin load order/priority?

---
