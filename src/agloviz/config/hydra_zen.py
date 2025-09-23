"""Hydra-zen configuration builders for ALGOViz.

This module contains all builds() definitions that create structured configs
from our Pydantic models and component classes.
"""

from hydra_zen import builds

from ..core.director import Director
from ..rendering.config import RenderConfig, RenderFormat, RenderQuality
from ..rendering.renderer import SimpleRenderer
from .models import ScenarioConfig, SceneConfig, ThemeConfig, TimingConfig, TimingMode

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
DraftTimingConfig = builds(
    TimingConfig,
    mode=TimingMode.DRAFT,
    ui=0.5,
    events=0.4,
    effects=0.25,
    waits=0.25,
    multipliers={"draft": 0.5, "normal": 1.0, "fast": 0.25}
)

NormalTimingConfig = builds(
    TimingConfig,
    mode=TimingMode.NORMAL,
    ui=1.0,
    events=0.8,
    effects=0.5,
    waits=0.5,
    multipliers={"draft": 0.5, "normal": 1.0, "fast": 0.25}
)

FastTimingConfig = builds(
    TimingConfig,
    mode=TimingMode.FAST,
    ui=0.25,
    events=0.2,
    effects=0.125,
    waits=0.125,
    multipliers={"draft": 0.5, "normal": 1.0, "fast": 0.25}
)

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

# BFS Dynamic Scene with dynamic parameter templates
BFSDynamicSceneConfig = builds(
    SceneConfig,
    name="bfs_dynamic",
    algorithm="bfs",
    widgets={
        "grid": {"_target_": "agloviz.widgets.grid.GridWidget", "width": 15, "height": 15},
        "queue": {"_target_": "agloviz.widgets.queue.QueueWidget", "max_visible_items": 12}
    },
    event_bindings={
        "enqueue": [
            {
                "widget": "queue",
                "action": "add_element",
                "params": {
                    "element": "${event_data:node.id}",
                    "style": "frontier",
                    "duration": "${timing_value:events}"
                },
                "order": 1
            },
            {
                "widget": "grid",
                "action": "highlight_cell",
                "params": {
                    "position": "${event_data:node.position}",
                    "color": "${event_data:node.color}",
                    "duration": "${timing_value:effects}"
                },
                "order": 2
            }
        ],
        "dequeue": [
            {
                "widget": "queue",
                "action": "remove_element",
                "params": {
                    "index": 0,
                    "animation_duration": "${timing_value:ui}"
                },
                "order": 1
            }
        ]
    }
)

# =====================================================================
# DIRECTOR CONFIGURATIONS
# =====================================================================

# Director structured config using hydra-zen builds()
DirectorConfigZen = builds(
    Director,
    storyboard="${storyboard}",
    timing="${timing}",
    scene_config="${scene_config}",
    mode="normal",  # Default mode
    with_voice=False,  # Default voice disabled
    timing_tracker=None,  # Created internally
    populate_full_signature=True
)
