"""Hydra-zen configuration builders for ALGOViz.

This module contains all builds() definitions that create structured configs
from our Pydantic models and component classes.
"""

from hydra_zen import builds
from .models import ScenarioConfig, ThemeConfig, TimingConfig, TimingMode, SceneConfig
from ..rendering.renderer import SimpleRenderer
from ..rendering.config import RenderConfig, RenderQuality, RenderFormat

# =====================================================================
# RENDERER CONFIGURATIONS
# =====================================================================

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

# =====================================================================
# SCENARIO CONFIGURATIONS
# =====================================================================

# Scenario configurations
MazeSmallConfig = builds(
    ScenarioConfig,
    name="maze_small",
    obstacles=[(1, 1), (2, 2), (3, 1)],
    start=(0, 0),
    goal=(9, 9),
    grid_size=(10, 10)
)

MazeLargeConfig = builds(
    ScenarioConfig,
    name="maze_large", 
    obstacles=[(1, 1), (2, 2), (3, 1), (5, 5)],
    start=(0, 0),
    goal=(19, 19),
    grid_size=(20, 20)
)

WeightedGraphConfig = builds(
    ScenarioConfig,
    name="weighted_graph",
    obstacles=[],
    start=(0, 0),
    goal=(9, 9),
    grid_size=(10, 10)
)

# =====================================================================
# THEME CONFIGURATIONS
# =====================================================================

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

# =====================================================================
# TIMING CONFIGURATIONS
# =====================================================================

# Timing configurations
DraftTimingConfig = builds(TimingConfig, mode=TimingMode.DRAFT)
NormalTimingConfig = builds(TimingConfig, mode=TimingMode.NORMAL)
FastTimingConfig = builds(TimingConfig, mode=TimingMode.FAST)

# =====================================================================
# SCENE CONFIGURATION BUILDERS  
# =====================================================================

# BFS Scene Configurations - Using the working pattern from render_pure_zen.py
BFSBasicSceneConfig = builds(
    SceneConfig,
    name="bfs_basic",
    algorithm="bfs",
    widgets={
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget"},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget"}
    },
    event_bindings={
        "enqueue": [
            {"widget": "queue", "action": "add_element", "order": 1},
            {"widget": "grid", "action": "highlight_cell", "params": {"color": "blue"}, "order": 2}
        ],
        "dequeue": [
            {"widget": "queue", "action": "remove_element", "order": 1}
        ]
    }
)

# BFS Advanced Scene with custom widget parameters (proves CLI overrides work)
BFSAdvancedSceneConfig = builds(
    SceneConfig,
    name="bfs_advanced",
    algorithm="bfs",
    widgets={
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget", "width": 15, "height": 15},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget", "max_visible_items": 12}
    },
    event_bindings={
        "enqueue": [
            {"widget": "queue", "action": "add_element", "order": 1},
            {"widget": "grid", "action": "highlight_cell", "params": {"color": "blue"}, "order": 2}
        ],
        "dequeue": [
            {"widget": "queue", "action": "remove_element", "order": 1}
        ]
    }
)
