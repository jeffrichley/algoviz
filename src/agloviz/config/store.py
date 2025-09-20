"""Configuration store for ALGOViz using hydra-zen.

This module defines and stores all configuration presets using hydra-zen's
store API, eliminating the need for hand-written YAML files.
"""

from hydra_zen import store

from .builders import (
    RenderConfigBuilder,
    ScenarioConfigBuilder,
    SubtitlesConfigBuilder,
    ThemeConfigBuilder,
    TimingConfigBuilder,
    VideoConfigBuilder,
    VoiceoverConfigBuilder,
)
from .models import RenderFormat, RenderQuality, SubtitleFormat, TimingMode

# Create store instances for different config groups
scenario_store = store(group="scenario")
timing_store = store(group="timing")
theme_store = store(group="theme")
voiceover_store = store(group="voiceover")
subtitles_store = store(group="subtitles")
render_store = store(group="render")

# === SCENARIO CONFIGURATIONS ===

scenario_store(
    ScenarioConfigBuilder,
    name="maze_small",
    config_name="small_maze",
    grid_file="grids/maze_small.yaml",
    start=(0, 0),
    goal=(9, 9),
    obstacles=[],
    weighted=False,
)

scenario_store(
    ScenarioConfigBuilder,
    name="maze_large",
    config_name="large_maze",
    grid_file="grids/maze_large.yaml",
    start=(0, 0),
    goal=(19, 19),
    obstacles=[],
    weighted=False,
)

scenario_store(
    ScenarioConfigBuilder,
    name="weighted_grid",
    config_name="weighted",
    grid_file="grids/weighted_grid.yaml",
    start=(0, 0),
    goal=(9, 9),
    obstacles=[],
    weighted=True,
)

scenario_store(
    ScenarioConfigBuilder,
    name="obstacle_course",
    config_name="obstacles",
    grid_file="grids/obstacle_course.yaml",
    start=(0, 0),
    goal=(9, 9),
    obstacles=[(3, 3), (3, 4), (4, 3), (6, 7), (7, 6), (7, 7)],
    weighted=False,
)

# === TIMING CONFIGURATIONS ===

timing_store(
    TimingConfigBuilder,
    name="draft",
    config_name="draft_timing",
    mode=TimingMode.DRAFT,
    ui=0.5,
    events=0.3,
    effects=0.2,
    waits=0.2,
)

timing_store(
    TimingConfigBuilder,
    name="normal",
    config_name="normal_timing",
    mode=TimingMode.NORMAL,
    ui=1.0,
    events=0.8,
    effects=0.5,
    waits=0.5,
)

timing_store(
    TimingConfigBuilder,
    name="fast",
    config_name="fast_timing",
    mode=TimingMode.FAST,
    ui=0.25,
    events=0.2,
    effects=0.1,
    waits=0.1,
)

timing_store(
    TimingConfigBuilder,
    name="slow",
    config_name="slow_timing",
    mode=TimingMode.NORMAL,
    ui=2.0,
    events=1.5,
    effects=1.0,
    waits=1.0,
)

# === THEME CONFIGURATIONS ===

theme_store(
    ThemeConfigBuilder,
    name="default",
    config_name="default_theme",
    colors={
        "visited": "#4CAF50",
        "frontier": "#2196F3",
        "goal": "#FF9800",
        "path": "#E91E63",
        "obstacle": "#424242",
        "grid": "#E0E0E0",
    },
)

theme_store(
    ThemeConfigBuilder,
    name="dark",
    config_name="dark_theme",
    colors={
        "visited": "#66BB6A",
        "frontier": "#42A5F5",
        "goal": "#FFA726",
        "path": "#EC407A",
        "obstacle": "#212121",
        "grid": "#424242",
    },
)

theme_store(
    ThemeConfigBuilder,
    name="high_contrast",
    config_name="high_contrast_theme",
    colors={
        "visited": "#00FF00",
        "frontier": "#0000FF",
        "goal": "#FF0000",
        "path": "#FFFF00",
        "obstacle": "#000000",
        "grid": "#FFFFFF",
    },
)

theme_store(
    ThemeConfigBuilder,
    name="colorblind_friendly",
    config_name="colorblind_theme",
    colors={
        "visited": "#009E73",
        "frontier": "#0173B2",
        "goal": "#D55E00",
        "path": "#CC79A7",
        "obstacle": "#000000",
        "grid": "#F0F0F0",
    },
)

# === VOICEOVER CONFIGURATIONS ===

voiceover_store(
    VoiceoverConfigBuilder,
    name="disabled",
    config_name="no_voice",
    enabled=False,
)

voiceover_store(
    VoiceoverConfigBuilder,
    name="english_default",
    config_name="en_voice",
    enabled=True,
    lang="en",
    voice="en_US",
    speed=1.0,
)

voiceover_store(
    VoiceoverConfigBuilder,
    name="english_fast",
    config_name="en_fast",
    enabled=True,
    lang="en",
    voice="en_US",
    speed=1.25,
)

voiceover_store(
    VoiceoverConfigBuilder,
    name="english_slow",
    config_name="en_slow",
    enabled=True,
    lang="en",
    voice="en_US",
    speed=0.8,
)

# === SUBTITLE CONFIGURATIONS ===

subtitles_store(
    SubtitlesConfigBuilder,
    name="disabled",
    config_name="no_subtitles",
    enabled=False,
)

subtitles_store(
    SubtitlesConfigBuilder,
    name="srt_baseline",
    config_name="srt_basic",
    enabled=True,
    mode="baseline",
    format=SubtitleFormat.SRT,
    burn_in=False,
)

subtitles_store(
    SubtitlesConfigBuilder,
    name="srt_burned",
    config_name="srt_burned_in",
    enabled=True,
    mode="baseline",
    format=SubtitleFormat.SRT,
    burn_in=True,
)

subtitles_store(
    SubtitlesConfigBuilder,
    name="vtt_baseline",
    config_name="vtt_basic",
    enabled=True,
    mode="baseline",
    format=SubtitleFormat.VTT,
    burn_in=False,
)

# === RENDER CONFIGURATIONS ===

render_store(
    RenderConfigBuilder,
    name="draft",
    config_name="draft_render",
    resolution=(1280, 720),
    frame_rate=15,
    quality=RenderQuality.DRAFT,
    format=RenderFormat.MP4,
)

render_store(
    RenderConfigBuilder,
    name="medium",
    config_name="medium_render",
    resolution=(1920, 1080),
    frame_rate=30,
    quality=RenderQuality.MEDIUM,
    format=RenderFormat.MP4,
)

render_store(
    RenderConfigBuilder,
    name="high",
    config_name="high_render",
    resolution=(1920, 1080),
    frame_rate=60,
    quality=RenderQuality.HIGH,
    format=RenderFormat.MP4,
)

render_store(
    RenderConfigBuilder,
    name="gif_preview",
    config_name="gif_output",
    resolution=(1280, 720),
    frame_rate=15,
    quality=RenderQuality.DRAFT,
    format=RenderFormat.GIF,
)

# === DEFAULT VIDEO CONFIG ===

# Store the main video config with default selections
store(
    VideoConfigBuilder,
    name="default_video",
    hydra_defaults=[
        "_self_",
        {"scenario": "maze_small"},
        {"timing": "normal"},
        {"theme": "default"},
        {"voiceover": "disabled"},
        {"subtitles": "disabled"},
        {"render": "medium"},
    ],
)

def add_all_to_hydra_store() -> None:
    """Add all stored configurations to Hydra's config store."""
    scenario_store.add_to_hydra_store()
    timing_store.add_to_hydra_store()
    theme_store.add_to_hydra_store()
    voiceover_store.add_to_hydra_store()
    subtitles_store.add_to_hydra_store()
    render_store.add_to_hydra_store()
    store.add_to_hydra_store()  # Add the main store
