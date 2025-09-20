"""Hydra-zen configuration builders for ALGOViz.

This module provides hydra-zen builders that dynamically generate structured
configs for all ALGOViz configuration models, enabling type-safe DI.
"""

from hydra_zen import builds

from .models import (
    RenderConfig,
    ScenarioConfig,
    SubtitlesConfig,
    ThemeConfig,
    TimingConfig,
    VideoConfig,
    VoiceoverConfig,
)

# Build dynamic configs with full signature population for type safety
ScenarioConfigBuilder = builds(
    ScenarioConfig,
    populate_full_signature=True,
    zen_partial=False,
)

ThemeConfigBuilder = builds(
    ThemeConfig,
    populate_full_signature=True,
    zen_partial=False,
)

VoiceoverConfigBuilder = builds(
    VoiceoverConfig,
    populate_full_signature=True,
    zen_partial=False,
)

SubtitlesConfigBuilder = builds(
    SubtitlesConfig,
    populate_full_signature=True,
    zen_partial=False,
)

RenderConfigBuilder = builds(
    RenderConfig,
    populate_full_signature=True,
    zen_partial=False,
)

TimingConfigBuilder = builds(
    TimingConfig,
    populate_full_signature=True,
    zen_partial=False,
)

VideoConfigBuilder = builds(
    VideoConfig,
    populate_full_signature=True,
    zen_partial=False,
)

# Export all builders for easy import
__all__ = [
    "ScenarioConfigBuilder",
    "ThemeConfigBuilder",
    "VoiceoverConfigBuilder",
    "SubtitlesConfigBuilder",
    "RenderConfigBuilder",
    "TimingConfigBuilder",
    "VideoConfigBuilder",
]
