# ALGOViz Hydra-zen Refactor Plan

## 🎯 **Overview**

This plan outlines the complete refactor of our CLI system from manual configuration management to proper hydra-zen patterns, while maintaining Typer as our CLI framework and properly separating concerns.

## 🔍 **Current Problems**

### ❌ **What's Wrong with `render_app.py` (288 lines)**

1. **Manual ConfigStore Management**: `setup_configstore()`, `register_scene_configs()` called in every command
2. **Manual Config Loading**: Custom `_load_config_from_store()` functions with error handling
3. **Manual Object Instantiation**: Explicit `instantiate(config_node)` calls throughout
4. **Manual Override Parsing**: 40+ lines of custom `_apply_overrides()` logic
5. **Repetitive Typer Boilerplate**: 200+ lines of repetitive CLI command definitions
6. **No Reproducibility**: No automatic config saving or experiment tracking
7. **Limited Override Support**: Only basic `key=value`, no deep nested overrides

### ✅ **What Hydra-zen Provides Automatically**

1. **Automatic Config Management**: No manual ConfigStore calls needed
2. **Automatic Object Instantiation**: Objects passed to functions already instantiated
3. **Native Override Support**: `key=value` and `key.nested.deep=value` patterns
4. **Rich Help Generation**: Config groups, current values, automatic validation
5. **Reproducible Runs**: Automatic config saving with timestamps
6. **Multi-run Support**: Built-in experiment sweeps and parallelization
7. **Type Safety**: Full type checking through `builds()` signature inspection

## 🏗️ **New Architecture: Proper Separation of Concerns**

### **Configuration Layer (Outside CLI)**
- **`src/agloviz/config/hydra_zen.py`** - All `builds()` and configuration definitions
- **`src/agloviz/config/store.py`** - All `store()` registrations and ConfigStore setup
- **Existing config files** - Keep existing Pydantic models, enhance with hydra-zen

### **Core Logic Layer**
- **`src/agloviz/core/render_functions.py`** - Pure functions that receive instantiated objects
- **Existing core modules** - SceneEngine, Director, etc. work unchanged

### **CLI Layer (Typer + Hydra-zen)**
- **`src/agloviz/cli/render_zen.py`** - Typer app that uses hydra-zen for config management
- **Main functions** - Receive instantiated objects from hydra-zen
- **CLI commands** - Typer commands that call hydra-zen functions via `zen().call()`

## 📝 **Detailed Implementation Steps**

### **STEP 1: Create Hydra-zen Configuration Builders**

**File**: `src/agloviz/config/hydra_zen.py`

**Purpose**: All `builds()` definitions for our components, separated from CLI logic

**Content Structure**:
```python
"""Hydra-zen configuration builders for ALGOViz.

This module contains all builds() definitions that create structured configs
from our Pydantic models and component classes.
"""

from hydra_zen import builds
from .models import RenderConfig, ScenarioConfig, ThemeConfig, TimingConfig, TimingMode
from ..rendering.renderer import SimpleRenderer
from ..rendering.config import RenderQuality, RenderFormat

# Renderer configurations
DraftRenderer = builds(
    SimpleRenderer,
    render_config=builds(
        RenderConfig,
        quality=RenderQuality.DRAFT,
        resolution=(854, 480),
        frame_rate=15,
        format=RenderFormat.MP4
    )
)

MediumRenderer = builds(
    SimpleRenderer,
    render_config=builds(
        RenderConfig,
        quality=RenderQuality.MEDIUM,
        resolution=(1280, 720),
        frame_rate=30,
        format=RenderFormat.MP4
    )
)

HDRenderer = builds(
    SimpleRenderer,
    render_config=builds(
        RenderConfig,
        quality=RenderQuality.HIGH,
        resolution=(1920, 1080),
        frame_rate=60,
        format=RenderFormat.MP4
    )
)

# Scenario configurations
MazeSmallConfig = builds(
    ScenarioConfig,
    name="maze_small",
    obstacles=[(1, 1), (2, 2), (3, 1)],
    start=(0, 0),
    goal=(9, 9)
)

MazeLargeConfig = builds(
    ScenarioConfig,
    name="maze_large", 
    obstacles=[(1, 1), (2, 2), (3, 1), (5, 5)],
    start=(0, 0),
    goal=(19, 19)
)

WeightedGraphConfig = builds(
    ScenarioConfig,
    name="weighted_graph",
    obstacles=[],
    start=(0, 0),
    goal=(9, 9)
)

# Theme configurations
DefaultThemeConfig = builds(ThemeConfig, name="default")

DarkThemeConfig = builds(
    ThemeConfig,
    name="dark",
    colors={
        "visited": "#BB86FC",
        "frontier": "#03DAC6", 
        "goal": "#CF6679",
        "path": "#FF9800",
        "obstacle": "#1F1B24",
        "grid": "#2D2D2D"
    }
)

HighContrastThemeConfig = builds(
    ThemeConfig,
    name="high_contrast",
    colors={
        "visited": "#00FF00",
        "frontier": "#0000FF",
        "goal": "#FF0000", 
        "path": "#FFFF00",
        "obstacle": "#000000",
        "grid": "#FFFFFF"
    }
)

# Timing configurations
DraftTimingConfig = builds(TimingConfig, mode=TimingMode.DRAFT)
NormalTimingConfig = builds(TimingConfig, mode=TimingMode.NORMAL)
FastTimingConfig = builds(TimingConfig, mode=TimingMode.FAST)
```

**Key Benefits**:
- All configuration logic in one place
- Type-safe through `builds()` signature inspection
- Easy to add new configurations
- Separated from CLI concerns

---

### **STEP 2: Create Hydra-zen Store Registration**

**File**: `src/agloviz/config/store.py` (enhance existing)

**Purpose**: All `store()` registrations and setup functions

**Content Structure**:
```python
"""Hydra-zen store registration and setup for ALGOViz.

This module handles all store() registrations and provides setup functions
for initializing the hydra-zen configuration system.
"""

from hydra_zen import store
from hydra.core.config_store import ConfigStore
from .hydra_zen import (
    # Renderer configs
    DraftRenderer, MediumRenderer, HDRenderer,
    # Scenario configs  
    MazeSmallConfig, MazeLargeConfig, WeightedGraphConfig,
    # Theme configs
    DefaultThemeConfig, DarkThemeConfig, HighContrastThemeConfig,
    # Timing configs
    DraftTimingConfig, NormalTimingConfig, FastTimingConfig
)

def register_hydra_zen_configs():
    """Register all hydra-zen configurations in appropriate groups."""
    
    # Renderer configurations
    renderer_store = store(group="renderer")
    renderer_store(DraftRenderer, name="draft")
    renderer_store(MediumRenderer, name="medium")
    renderer_store(HDRenderer, name="hd")
    
    # Scenario configurations
    scenario_store = store(group="scenario")
    scenario_store(MazeSmallConfig, name="maze_small")
    scenario_store(MazeLargeConfig, name="maze_large")
    scenario_store(WeightedGraphConfig, name="weighted_graph")
    
    # Theme configurations
    theme_store = store(group="theme")
    theme_store(DefaultThemeConfig, name="default")
    theme_store(DarkThemeConfig, name="dark")
    theme_store(HighContrastThemeConfig, name="high_contrast")
    
    # Timing configurations
    timing_store = store(group="timing")
    timing_store(DraftTimingConfig, name="draft")
    timing_store(NormalTimingConfig, name="normal")
    timing_store(FastTimingConfig, name="fast")

def setup_hydra_zen_store():
    """Setup complete hydra-zen store with all configurations."""
    # Register all hydra-zen configs
    register_hydra_zen_configs()
    
    # Add to Hydra's global store
    store.add_to_hydra_store()
    
    return store

def get_config_store():
    """Get configured ConfigStore instance."""
    cs = ConfigStore.instance()
    return cs

# Backward compatibility with existing system
def setup_configstore():
    """Legacy function for backward compatibility."""
    return setup_hydra_zen_store()
```

**Key Benefits**:
- Centralized configuration registration
- Clear separation from CLI logic
- Backward compatibility maintained
- Easy to extend with new config groups

---

### **STEP 3: Create Main Render Functions (Pure Logic)**

**File**: `src/agloviz/core/render_functions.py` (new file)

**Purpose**: Pure functions that receive instantiated objects from hydra-zen

**Content Structure**:
```python
"""Core render functions for ALGOViz.

These functions receive fully instantiated objects from hydra-zen and contain
the pure business logic for rendering algorithm visualizations.
"""

from typing import Any, Dict
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from ..rendering.renderer import SimpleRenderer
from ..config.models import ScenarioConfig, ThemeConfig, TimingConfig
from ..core.scene import SceneEngine

console = Console()

def render_algorithm_video(
    algorithm: str,
    renderer: SimpleRenderer,
    scenario_config: ScenarioConfig,
    theme_config: ThemeConfig,
    timing_config: TimingConfig,
    output_path: str = "output.mp4"
) -> Dict[str, Any]:
    """Main render function - receives fully instantiated objects from hydra-zen.
    
    This function contains pure business logic and receives all dependencies
    as already-instantiated objects from hydra-zen, eliminating all manual
    configuration management.
    
    Args:
        algorithm: Algorithm name (e.g., "bfs", "dfs", "dijkstra")
        renderer: Fully configured SimpleRenderer instance
        scenario_config: Instantiated scenario configuration
        theme_config: Instantiated theme configuration  
        timing_config: Instantiated timing configuration
        output_path: Path for output video file
        
    Returns:
        Dictionary with render results and metadata
    """
    console.print(Panel(
        f"🎬 Rendering [bold cyan]{algorithm}[/] visualization", 
        title="ALGOViz Hydra-zen Render"
    ))
    
    console.print("✨ All configurations automatically instantiated by hydra-zen!")
    console.print(f"📊 Renderer: {renderer.config.quality.value} @ {renderer.config.resolution}")
    console.print(f"🗺️  Scenario: {scenario_config.name}")
    console.print(f"🎨 Theme: {theme_config.name}")
    console.print(f"⏱️  Timing: {timing_config.mode.value}")
    console.print(f"🚀 Output: [bold green]{output_path}[/]")
    
    # Create scene configuration from existing scene system
    scene_config = _create_scene_config(algorithm, scenario_config, theme_config)
    
    # All objects are already instantiated by hydra-zen!
    result = renderer.render_algorithm_video(
        algorithm=algorithm,
        scenario_config=scenario_config,
        scene_config=scene_config,
        theme_config=theme_config,
        timing_config=timing_config,
        output_path=output_path
    )
    
    console.print(Panel(
        f"✅ Video rendered successfully!\n"
        f"📁 Output: {output_path}\n"
        f"⏱️  Duration: {result.get('duration', 'N/A')}s\n"
        f"📊 Resolution: {result.get('resolution', 'N/A')}\n"
        f"🎯 Algorithm: {algorithm}",
        title="[green]Render Complete[/]"
    ))
    
    return result

def preview_algorithm(
    algorithm: str,
    scenario_config: ScenarioConfig,
    frames: int = 120,
    output_path: str = "preview.mp4"
) -> Dict[str, Any]:
    """Preview render function - receives instantiated objects from hydra-zen.
    
    Args:
        algorithm: Algorithm name
        scenario_config: Instantiated scenario configuration
        frames: Maximum number of frames to render
        output_path: Path for preview output file
        
    Returns:
        Dictionary with preview results and metadata
    """
    console.print(Panel(
        f"👀 Previewing [bold cyan]{algorithm}[/] ({frames} frames)", 
        title="Quick Preview"
    ))
    
    from ..rendering.renderer import create_preview_renderer
    renderer = create_preview_renderer(max_frames=frames)
    result = renderer.render_preview(algorithm, scenario_config.name, output_path)
    
    console.print(Panel(
        f"✅ Preview rendered!\n"
        f"📁 Output: {output_path}\n"
        f"🎞️  Frames: {frames}\n"
        f"⚡ Mode: Draft quality",
        title="[green]Preview Complete[/]"
    ))
    
    return result

def _create_scene_config(algorithm: str, scenario_config: ScenarioConfig, theme_config: ThemeConfig) -> Dict[str, Any]:
    """Create scene configuration from algorithm and configs."""
    return {
        "name": f"{algorithm}_pathfinding",
        "algorithm": algorithm,
        "widgets": {
            "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
            "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
        },
        "event_bindings": {
            # Event bindings would be defined here based on algorithm
        }
    }
```

**Key Benefits**:
- Pure business logic, no configuration concerns
- Receives fully instantiated dependencies
- Easy to test and maintain
- Clear separation of concerns

---

### **STEP 4: Configure Main Functions with Defaults (CLI LAYER)**

**File**: `src/agloviz/cli/render_zen.py`

**Purpose**: Typer app that uses hydra-zen for configuration management

**Content Structure**:
```python
"""ALGOViz Render CLI with Hydra-zen Integration.

This module provides a Typer-based CLI that uses hydra-zen for powerful
configuration management while maintaining familiar CLI patterns.
"""

import typer
from typing import List, Optional
from pathlib import Path
from hydra_zen import store, zen
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..config.store import setup_hydra_zen_store
from ..core.render_functions import render_algorithm_video, preview_algorithm

app = typer.Typer(
    name="render-zen",
    help="ALGOViz Rendering System with Hydra-zen Configuration",
    rich_markup_mode="rich"
)

console = Console()

def _setup_render_configs():
    """Setup render command configurations with hydra-zen.
    
    This is where we configure our main functions with default config selections.
    This is the appropriate place for CLI-specific configuration setup.
    """
    # Setup hydra-zen store with all configurations
    setup_hydra_zen_store()
    
    # Configure video command with defaults
    video_store = store(group="app")
    video_store(
        render_algorithm_video,
        algorithm="bfs",  # Default algorithm
        output_path="output.mp4",  # Default output
        hydra_defaults=[
            "_self_",
            {"renderer": "medium"},      # Default to medium quality
            {"scenario": "maze_small"},  # Default scenario
            {"theme": "default"},        # Default theme
            {"timing": "normal"}         # Default timing
        ],
        name="video"
    )
    
    # Configure preview command with defaults
    preview_store = store(group="app")
    preview_store(
        preview_algorithm,
        algorithm="bfs",
        frames=120,
        output_path="preview.mp4",
        hydra_defaults=[
            "_self_",
            {"scenario": "maze_small"}
        ],
        name="preview"
    )

@app.command()
def video(
    algorithm: str = typer.Argument("bfs", help="Algorithm to visualize (bfs, dfs, dijkstra)"),
    output: str = typer.Option("output.mp4", "--output", "-o", help="Output video file path"),
    renderer: str = typer.Option("medium", "--renderer", "-r", help="Renderer quality: draft/medium/hd"),
    scenario: str = typer.Option("maze_small", "--scenario", "-s", help="Scenario: maze_small/maze_large/weighted_graph"),
    theme: str = typer.Option("default", "--theme", "-t", help="Theme: default/dark/high_contrast"),
    timing: str = typer.Option("normal", "--timing", help="Timing: draft/normal/fast"),
    config_overrides: Optional[List[str]] = typer.Option(None, "--override", help="Config overrides (key=value)")
):
    """Render algorithm visualization to video using hydra-zen configuration.
    
    Examples:
        render-zen video bfs --renderer hd --scenario maze_large
        render-zen video dfs --override renderer.render_config.resolution=[1920,1080]
        render-zen video bfs --theme dark --timing fast
    """
    console.print(Panel(f"🎬 Rendering [bold cyan]{algorithm}[/] with hydra-zen", title="ALGOViz Render"))
    
    try:
        # Setup configurations
        _setup_render_configs()
        
        # Build override list
        overrides = [
            f"algorithm={algorithm}",
            f"output_path={output}",
            f"renderer={renderer}",
            f"scenario={scenario}",
            f"theme={theme}",
            f"timing={timing}"
        ]
        
        if config_overrides:
            overrides.extend(config_overrides)
        
        # Use zen to handle the actual rendering with hydra-zen instantiation
        # This is where hydra-zen takes over configuration management!
        result = zen(render_algorithm_video).call(
            config_name="app/video",
            overrides=overrides
        )
        
        console.print(f"✅ Render completed successfully!")
        return result
        
    except Exception as e:
        console.print(Panel(
            f"❌ Render failed: {str(e)}",
            title="[red]Render Error[/]",
            border_style="red"
        ))
        raise typer.Exit(1)

@app.command()
def preview(
    algorithm: str = typer.Argument("bfs", help="Algorithm to preview"),
    frames: int = typer.Option(120, "--frames", "-f", help="Number of frames to render"),
    output: str = typer.Option("preview.mp4", "--output", "-o", help="Preview output file"),
    scenario: str = typer.Option("maze_small", "--scenario", "-s", help="Scenario configuration"),
    config_overrides: Optional[List[str]] = typer.Option(None, "--override", help="Config overrides")
):
    """Quick preview render with limited frames.
    
    Examples:
        render-zen preview bfs --frames 60
        render-zen preview dfs --scenario maze_large --frames 180
    """
    console.print(Panel(f"👀 Previewing [bold cyan]{algorithm}[/] ({frames} frames)", title="Quick Preview"))
    
    try:
        _setup_render_configs()
        
        overrides = [
            f"algorithm={algorithm}",
            f"frames={frames}",
            f"output_path={output}",
            f"scenario={scenario}"
        ]
        
        if config_overrides:
            overrides.extend(config_overrides)
        
        result = zen(preview_algorithm).call(
            config_name="app/preview",
            overrides=overrides
        )
        
        console.print(f"✅ Preview completed successfully!")
        return result
        
    except Exception as e:
        console.print(Panel(f"❌ Preview failed: {str(e)}", title="[red]Preview Error[/]", border_style="red"))
        raise typer.Exit(1)

@app.command()
def list_configs(
    config_type: str = typer.Argument(..., help="Configuration type: renderer/scenario/theme/timing")
):
    """List available configurations from hydra-zen store.
    
    Examples:
        render-zen list-configs renderer
        render-zen list-configs scenario
    """
    console.print(Panel(f"📋 Available [bold cyan]{config_type}[/] configurations", title="Hydra-zen ConfigStore"))
    
    try:
        _setup_render_configs()
        
        # Get configurations from hydra-zen store
        config_store = store.get_store()
        
        if config_type not in ["renderer", "scenario", "theme", "timing"]:
            console.print(f"❌ Invalid config type: {config_type}")
            console.print("Available types: renderer, scenario, theme, timing")
            raise typer.Exit(1)
        
        # Create table showing available configs
        table = Table(title=f"{config_type.title()} Configurations")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        
        # This would list configs from the hydra-zen store
        # Implementation depends on hydra-zen store API
        configs = _get_configs_by_type(config_type)
        
        for config_name, description in configs.items():
            table.add_row(config_name, description)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error listing configs: {e}")
        raise typer.Exit(1)

def _get_configs_by_type(config_type: str) -> dict:
    """Get available configurations by type."""
    config_map = {
        "renderer": {"draft": "Low quality, fast render", "medium": "Balanced quality/speed", "hd": "High quality"},
        "scenario": {"maze_small": "Small 10x10 maze", "maze_large": "Large 20x20 maze", "weighted_graph": "Weighted graph"},
        "theme": {"default": "Default color scheme", "dark": "Dark mode colors", "high_contrast": "High contrast colors"},
        "timing": {"draft": "Fast timing for previews", "normal": "Standard timing", "fast": "Accelerated timing"}
    }
    return config_map.get(config_type, {})

if __name__ == "__main__":
    app()
```

**Key Benefits**:
- Familiar Typer CLI patterns maintained
- Hydra-zen handles all config complexity
- Rich help and error handling
- Support for deep overrides via `--override`

---

### **STEP 5: Update pyproject.toml Entry Point**

**File**: `pyproject.toml`

**Changes**:
```toml
[project.scripts]
agloviz = "agloviz.cli:app"                    # Keep existing legacy CLI
render = "agloviz.cli.render_app:app"          # Keep current manual CLI  
render-zen = "agloviz.cli.render_zen:app"      # Add new hydra-zen CLI
```

**Migration Strategy**:
1. **Phase 1**: Both CLIs available (`render` and `render-zen`)
2. **Phase 2**: Users can test and compare both approaches
3. **Phase 3**: Eventually replace `render` with `render-zen`

---

### **STEP 6: Integration with Existing Systems**

**Compatibility Measures**:

1. **Keep Existing Pydantic Models**: No changes to `src/agloviz/config/models.py`
2. **SceneEngine Compatibility**: Works with any config objects (Pydantic or hydra-zen)
3. **Backward Compatibility**: Legacy `setup_configstore()` still works
4. **Gradual Migration**: Can migrate one command at a time

**Testing Strategy**:
```python
# Test that both systems produce identical results
def test_cli_equivalence():
    # Test that render_app.py and render_zen.py produce same output
    old_result = run_old_cli("bfs", "medium", "maze_small")
    new_result = run_new_cli("bfs", "medium", "maze_small") 
    assert old_result == new_result
```

---

### **STEP 7: Enhanced Capabilities**

**New Features Available with Hydra-zen**:

1. **Deep Overrides**:
   ```bash
   render-zen video bfs --override renderer.render_config.resolution=[1920,1080]
   render-zen video bfs --override renderer.render_config.frame_rate=60
   render-zen video bfs --override scenario.start=[2,2] scenario.goal=[18,18]
   ```

2. **Multi-run Experiments**:
   ```bash
   render-zen video bfs --multirun renderer=draft,medium,hd
   render-zen video --multirun algorithm=bfs,dfs,dijkstra scenario=maze_small,maze_large
   ```

3. **Config Composition**:
   ```bash
   render-zen video bfs renderer=hd scenario=maze_large theme=dark timing=fast
   ```

4. **Reproducible Runs**:
   - Automatic config saving with timestamps
   - Full configuration logged for each run
   - Easy to reproduce exact runs

---

## 📊 **Expected Results**

### **Code Metrics**
- **Current**: 288 lines in `render_app.py`
- **New**: ~150 lines total across all files
- **Reduction**: ~50% less code
- **Eliminated**: All manual config management, override parsing, repetitive CLI code

### **New Capabilities**
- ✅ **Deep Overrides**: `renderer.render_config.resolution=[1920,1080]`
- ✅ **Multi-run Experiments**: `--multirun renderer=draft,medium,hd`
- ✅ **Config Composition**: Mix any config combinations automatically
- ✅ **Reproducible Runs**: Automatic config saving with timestamps
- ✅ **Rich Help**: Automatic help generation with current config values
- ✅ **Type Safety**: Full type checking through `builds()` signature inspection

### **Maintainability Improvements**
- ✅ **Single Source of Truth**: All configs defined in dedicated files
- ✅ **Clear Separation**: Config logic separate from CLI logic
- ✅ **No Boilerplate**: No manual CLI argument parsing or validation
- ✅ **Extensible**: Easy to add new commands, configs, or override patterns
- ✅ **Testable**: Pure functions easy to unit test

## 🎯 **Migration Timeline**

### **Phase 1: Parallel Implementation (Week 1)**
- Create `src/agloviz/config/hydra_zen.py`
- Create `src/agloviz/config/store.py` enhancements
- Create `src/agloviz/core/render_functions.py`
- Create `src/agloviz/cli/render_zen.py`
- Add `render-zen` entry point

### **Phase 2: Testing & Validation (Week 2)**
- Comprehensive testing of new CLI
- Performance comparison
- Feature parity validation
- User acceptance testing

### **Phase 3: Migration (Week 3)**
- Update documentation
- Migrate `render` entry point to new implementation
- Deprecate old implementation
- Clean up legacy code

## ⚠️ **Breaking Changes**

### **Minimal Breaking Changes**
- CLI command syntax remains largely the same
- New `--override` syntax for deep configuration changes
- Some command options may be renamed for consistency

### **Mitigation Strategies**
- Keep both CLIs available during transition
- Provide migration guide
- Maintain backward compatibility where possible

## ✅ **Success Criteria**

1. **✅ Functional Parity**: All existing render functionality works identically
2. **✅ Enhanced Capabilities**: Deep overrides and multi-run experiments work
3. **✅ Code Reduction**: Significant reduction in boilerplate code
4. **✅ Better UX**: Richer help, better error messages, more intuitive CLI
5. **✅ Maintainable**: Easier to add new configs, commands, and features
6. **✅ Type Safe**: Full type checking and validation
7. **✅ Reproducible**: Automatic experiment tracking and config saving

---

**This plan transforms our CLI from a manual, boilerplate-heavy implementation into a modern, powerful, hydra-zen native application that follows best practices and provides significantly enhanced capabilities while maintaining familiar CLI patterns.**
