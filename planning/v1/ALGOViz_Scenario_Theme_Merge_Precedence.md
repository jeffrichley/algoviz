

# 🔀 Scenario/Theme Merge Precedence

## Purpose

When multiple YAML configuration files are used (e.g., `scenario.yaml`, `timing.yaml`, `theme.yaml`), ALGOViz must merge them into a single canonical `VideoConfig`. CLI overrides then apply on top as the final step. This ensures a predictable, reproducible configuration regardless of how many sources are layered.

## Precedence Rules

1. **Defaults** (hardcoded)
2. **Scenario YAML** (grid, start/goal, algorithm)
3. **Timing YAML** (pacing, mode, overrides)
4. **Theme YAML** (colors, fonts, styles)
5. **CLI overrides** (highest priority)

If two files define the same field, the later one in precedence wins. CLI always overrides YAML.

---

## Example

### scenario.yaml

```yaml
scenario:
  grid: "mazes/maze1.txt"
  start: [0, 0]
  goal: [9, 9]
render:
  resolution: [1280, 720]
```

### timing.yaml

```yaml
timing:
  mode: draft
  ui: 0.75
```

### theme.yaml

```yaml
theme:
  grid_color: "#333333"
  highlight_color: "#ffcc00"
render:
  resolution: [1920, 1080]  # overrides scenario.yaml
```

### CLI

```
--render.quality=high --timing.mode=normal
```

---

## Canonical Merged Output

```yaml
scenario:
  grid: "mazes/maze1.txt"
  start: [0, 0]
  goal: [9, 9]

timing:
  mode: normal            # CLI overrides timing.yaml
  ui: 0.75

theme:
  grid_color: "#333333"
  highlight_color: "#ffcc00"

render:
  resolution: [1920, 1080]  # theme.yaml overrides scenario.yaml
  quality: high             # CLI override
```

---

## Implementation Notes

* ConfigManager merges YAMLs in the order loaded (scenario → timing → theme).
* Deep merge: nested dicts merge field by field rather than replacing whole sections.
* CLI flags map directly to fields (dot notation supported).
* Final merged config can be exported with `agloviz config dump` for reproducibility.
