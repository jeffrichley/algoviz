# Migration to Full Hydra-zen CLI

## Overview

ALGOViz has been upgraded to use a full hydra-zen based CLI system that provides powerful configuration management and runtime overrides. The new CLI replaces the previous Typer-based system with a more flexible and powerful approach.

## New CLI Capabilities

### Scene Configuration Control

**Old way (not possible):**
- Had to modify code to change widget setups
- Limited to predefined configurations
- No runtime parameter overrides

**New way (full control):**
```bash
# Select scene variant
uv run render scene=bfs_advanced

# Override widget parameters
uv run render scene.widgets.grid.width=15

# Add new parameters to basic configs
uv run render scene=bfs_basic +scene.widgets.grid.width=15

# Combine multiple overrides
uv run render scene=bfs_advanced scene.widgets.grid.width=20 scene.widgets.queue.max_visible_items=15

# Mix with other configs
uv run render scene=bfs_advanced renderer=hd theme=dark timing=fast
```

### Available Scene Configurations

- **`bfs_basic`**: Basic BFS with grid + queue widgets (default parameters)
- **`bfs_advanced`**: BFS with custom widget parameters (width=15, height=15, max_visible_items=12)

### Available Configuration Groups

The new CLI provides 5 configuration groups:

1. **`renderer`**: `draft`, `hd`, `medium`
2. **`scenario`**: `maze_large`, `maze_small`, `weighted_graph`
3. **`scene`**: `bfs_advanced`, `bfs_basic`
4. **`theme`**: `dark`, `default`, `high_contrast`
5. **`timing`**: `draft`, `fast`, `normal`

## Migration Commands

### Basic Usage

**New CLI (recommended):**
```bash
# Basic rendering
uv run render

# With scene selection
uv run render scene=bfs_advanced

# With widget overrides
uv run render scene=bfs_advanced scene.widgets.grid.width=20

# With multiple config overrides
uv run render scene=bfs_advanced renderer=hd theme=dark
```

### Advanced Usage

**Widget Parameter Overrides:**
```bash
# Override existing parameters
uv run render scene=bfs_advanced scene.widgets.grid.width=20

# Add new parameters to basic configs
uv run render scene=bfs_basic +scene.widgets.grid.width=15 +scene.widgets.queue.max_visible_items=10

# Multiple widget overrides
uv run render scene=bfs_advanced scene.widgets.grid.width=20 scene.widgets.queue.max_visible_items=15
```

**Configuration Combinations:**
```bash
# High-quality rendering with advanced scene
uv run render scene=bfs_advanced renderer=hd

# Dark theme with fast timing
uv run render theme=dark timing=fast

# Custom scenario with advanced scene
uv run render scenario=maze_large scene=bfs_advanced
```

## Key Benefits

1. **Runtime Flexibility**: Override any widget parameter without code changes
2. **Configuration Composition**: Mix and match different config groups
3. **Type Safety**: All configurations are validated through hydra-zen
4. **Rich Help**: Use `--help` to see all available options and current values
5. **Consistent Interface**: All config groups follow the same override patterns

## Examples

### Basic Scene Selection
```bash
# Use basic BFS scene
uv run render scene=bfs_basic

# Use advanced BFS scene with custom parameters
uv run render scene=bfs_advanced
```

### Widget Customization
```bash
# Customize grid size
uv run render scene=bfs_basic +scene.widgets.grid.width=20 +scene.widgets.grid.height=20

# Customize queue behavior
uv run render scene=bfs_advanced scene.widgets.queue.max_visible_items=20
```

### Full Configuration Control
```bash
# Complete customization
uv run render \
  scene=bfs_advanced \
  scene.widgets.grid.width=25 \
  scene.widgets.queue.max_visible_items=15 \
  renderer=hd \
  theme=dark \
  timing=fast \
  scenario=maze_large
```

## Getting Help

Use the built-in help system to explore available options:

```bash
# See all available configurations
uv run render --help

# See specific configuration values
uv run render scene=bfs_advanced --help

# See hydra-specific help
uv run render --hydra-help
```

## Backward Compatibility

The old CLI system has been completely replaced. All functionality is now available through the new hydra-zen based CLI with significantly more flexibility and power.

## Troubleshooting

### Common Issues

1. **Override Syntax**: Use `+` prefix to add new parameters to basic configs
2. **Parameter Names**: Check `--help` to see exact parameter names
3. **Config Validation**: All overrides are validated - invalid parameters will show clear error messages

### Getting Support

- Use `uv run render --help` to see all available options
- Check the configuration output to understand current values
- All error messages provide clear guidance on correct syntax
