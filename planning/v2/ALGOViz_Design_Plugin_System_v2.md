# ALGOViz Design Doc — Plugin & Extension System v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Updated for Widget Architecture v2.0 - scene configuration integration)
**Supersedes:** planning/v1/ALGOViz_Design_Plugin_System.md

---

## 1. Purpose
Allow external packages to extend ALGOViz (algorithms, widgets, scene configurations, themes, storyboards) **without modifying core code**. Provide robust discovery, versioning, and error isolation while supporting the multi-level widget hierarchy and scene configuration system.

## 2. Non‑Goals
- Security sandboxing (future; initial model trusts installed plugins).
- Distribution (PyPI publishing guidance is separate).

## 3. Extension Points
- **Algorithms**: provide `AlgorithmAdapter` and scene configuration.
- **Widgets**: implement multi-level widget hierarchy contracts and register factory.
- **Scene Configurations**: provide declarative event binding configurations.
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

## 5. Plugin API (Updated for v2.0)
```python
# my_pkg/plugins.py
def register(registry) -> None:
    # Algorithm registration (unchanged)
    registry.register_algorithm("a_star", a_star_adapter_factory)
    
    # Widget registration (updated for scene system)
    registry.register_widget("advanced_grid", AdvancedGridWidget)
    registry.register_scene_config("a_star_scene", AStarSceneConfig)
    
    # Storyboard registration (unchanged)
    registry.register_storyboard("a_star_default", "pkg://my_pkg/storyboards/a_star.yaml")
    
    # Theme registration (unchanged)  
    registry.register_theme("my_pkg.dark_mode", "pkg://my_pkg/themes/dark.yaml")
```

- The **registry** exposes `register_algorithm`, `register_widget`, `register_scene_config`, `register_storyboard`, `register_theme`.
- **Removed**: `register_action` - actions are now handled by scene configurations

## 6. Versioning & Compatibility
- Plugins may declare `requires={"agloviz": ">=2.0,<3.0"}`.
- On load, **PluginManager** performs semver compatibility checks.
- Incompatible plugins are skipped with clear diagnostics.

### Namespacing Rules (Explicit)
- **MANDATORY**: All plugin resources MUST be namespaced by the providing package name
- **Widget names**: `register_widget("my_pkg.priority_queue", ...)`
- **Algorithm keys**: `register_algorithm("my_pkg.a_star", ...)`
- **Scene configurations**: `register_scene_config("my_pkg.a_star_scene", ...)`
- **Storyboards**: `register_storyboard("my_pkg.a_star_default", ...)`
- **Themes**: `register_theme("my_pkg.dark_mode", ...)`
- The registry enforces uniqueness by full name; non-namespaced registrations are rejected
- Core ALGOViz resources use the "core" namespace implicitly (e.g., "core.bfs", "core.array_widget")

## 7. Widget Plugin Integration (New Section)

### 7.1 Widget Plugin Protocol
Widgets must conform to the multi-level hierarchy:

```python
# Level 2: Data Structure Widget Plugin
class PriorityQueueWidget(BaseModel):
    """Plugin widget for priority queue visualization."""
    elements: list[TokenWidget] = Field(default_factory=list)
    layout: QueueLayout
    
    def add_element(self, element: Any, priority: int, **kwargs) -> None:
        """Add element with priority (generic data structure operation)."""
        
    def remove_element(self, **kwargs) -> Any:
        """Remove highest priority element (generic operation)."""
        
    def highlight_element(self, identifier: Any, style: str, **kwargs) -> None:
        """Highlight specific element (generic visual operation)."""
    
    # NO event handling - pure visual operations only
```

### 7.2 Scene Configuration Plugins
Plugins provide scene configurations for algorithm-specific behavior:

```python
class AStarSceneConfig(BaseModel):
    """A* algorithm scene configuration."""
    
    @staticmethod
    def create() -> SceneConfig:
        return SceneConfig(
            widgets={
                "grid": WidgetSpec(name="grid", _target_="pathfinding.grid.PathfindingGrid"),
                "queue": WidgetSpec(name="queue", _target_="structures.priority_queue.PriorityQueueWidget")
            },
            event_bindings={
                "node_expanded": [
                    EventBinding(widget="grid", action="highlight_element", 
                               params={"index": "${event.pos}", "style": "expanded"}, order=1),
                    EventBinding(widget="queue", action="add_element", 
                               params={"element": "${event.neighbors}", "priority": "${event.f_score}"}, order=2)
                ]
            }
        )
```

### 7.3 Plugin Widget Discovery
```python
# Plugin widget registration with multi-level hierarchy
def register(registry) -> None:
    # Level 2: Data structure widgets
    registry.register_widget("structures.priority_queue", PriorityQueueWidget)
    registry.register_widget("structures.binary_heap", BinaryHeapWidget)
    
    # Level 3: Domain-specific extensions
    registry.register_widget("pathfinding.a_star_grid", AStarGridWidget)
    registry.register_widget("sorting.comparison_array", ComparisonArrayWidget)
    
    # Scene configurations for algorithm families
    registry.register_scene_config("pathfinding.a_star", AStarSceneConfig)
    registry.register_scene_config("sorting.quicksort", QuicksortSceneConfig)
```

## 8. Namespacing
- All plugin resources are **namespaced** by package name, e.g., `my_pkg.a_star`.
- **Widget names** follow hierarchy: `my_pkg.structures.priority_queue` or `my_pkg.pathfinding.a_star_grid`.
- **Scene configurations** are namespaced as `pkg.algorithm` in the scene registry.
- Prevents collisions: two plugins can both provide an `a_star` scene config or `priority_queue` widget under their own namespace.

## 9. Error Isolation
- Plugin load failures:
  - Soft fail with detailed error (traceback trimmed) and continue loading others.
  - Record failures in metadata JSON for reproducibility.
- Optional **quarantine** mode: disable failing plugin next runs until cleared.

## 10. CLI Integration
```bash
agloviz plugins list           # names, versions, entry points, status
agloviz plugins verify         # dry-run: load + sanity checks
agloviz render -a my_pkg.a_star --scenario demo.yaml --scene my_pkg.a_star_scene
```

## 11. Testing & Certification
- Provide a **plugin test harness** library:
  - Validate event determinism for adapters.
  - Validate scene configuration schemas.
  - Validate widget hierarchy compliance.
  - Smoke-render preview frames headless.
- Optionally label plugins as **verified** in `agloviz plugins list`.

## 12. Packaging & Assets
- Plugins can include asset files (YAMLs, images, audio) via standard Python package data.
- Use `pkg://` URIs to reference packaged assets.

## 13. Security Considerations
- Plugins run arbitrary code. Document risk; provide `--no-plugins` safe mode.
- Future: subprocess sandbox or WASI for untrusted sources.

## 14. Open Questions
- Hot reload for local dev (`--reload-plugins`)?
- Configurable plugin load order/priority?
- Scene configuration composition and inheritance?

---
