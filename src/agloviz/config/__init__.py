"""Configuration system for ALGOViz.

This module provides the configuration management system with support for
YAML files, CLI overrides, environment variables, and validation using
hydra-zen for dynamic configuration generation.
"""

from .builders import (
    RenderConfigBuilder,
    ScenarioConfigBuilder,
    SubtitlesConfigBuilder,
    ThemeConfigBuilder,
    TimingConfigBuilder,
    VideoConfigBuilder,
    VoiceoverConfigBuilder,
)
from .manager import ConfigError, ConfigManager
from .models import (
    RenderConfig,
    RenderFormat,
    RenderQuality,
    ScenarioConfig,
    SubtitleFormat,
    SubtitleMode,
    SubtitlesConfig,
    ThemeConfig,
    TimingConfig,
    TimingMode,
    VideoConfig,
    VoiceoverBackend,
    VoiceoverConfig,
)
from .store import add_all_to_hydra_store
from .timing import TimingRecord, TimingTracker, create_timing_tracker

__all__ = [
    # Models
    "VideoConfig",
    "ScenarioConfig",
    "ThemeConfig",
    "VoiceoverConfig",
    "SubtitlesConfig",
    "RenderConfig",
    "TimingConfig",
    # Enums
    "TimingMode",
    "VoiceoverBackend",
    "SubtitleMode",
    "SubtitleFormat",
    "RenderQuality",
    "RenderFormat",
    # Builders (hydra-zen)
    "VideoConfigBuilder",
    "ScenarioConfigBuilder",
    "ThemeConfigBuilder",
    "VoiceoverConfigBuilder",
    "SubtitlesConfigBuilder",
    "RenderConfigBuilder",
    "TimingConfigBuilder",
    # Manager
    "ConfigManager",
    "ConfigError",
    # Store
    "add_all_to_hydra_store",
    # Timing
    "TimingTracker",
    "TimingRecord",
    "create_timing_tracker",
]
