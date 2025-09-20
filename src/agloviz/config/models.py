"""Configuration models for ALGOViz.

This module provides Pydantic models for all configuration aspects of ALGOViz,
including scenarios, themes, voiceover, subtitles, rendering, and timing.
"""

from enum import Enum

from pydantic import BaseModel, Field


class TimingMode(str, Enum):
    """Timing modes for video generation."""
    DRAFT = "draft"
    NORMAL = "normal"
    FAST = "fast"


class VoiceoverBackend(str, Enum):
    """Supported voiceover backends."""
    COQUI = "coqui"


class SubtitleMode(str, Enum):
    """Subtitle generation modes."""
    BASELINE = "baseline"
    WHISPER_ALIGN = "whisper-align"


class SubtitleFormat(str, Enum):
    """Subtitle file formats."""
    SRT = "srt"
    VTT = "vtt"


class RenderQuality(str, Enum):
    """Render quality presets."""
    DRAFT = "draft"
    MEDIUM = "medium"
    HIGH = "high"


class RenderFormat(str, Enum):
    """Output video formats."""
    MP4 = "mp4"
    GIF = "gif"
    PNG_SEQUENCE = "png_sequence"


class ScenarioConfig(BaseModel):
    """Configuration for algorithm scenarios."""
    name: str = Field(min_length=1, description="Scenario name must not be empty")
    grid_file: str
    start: tuple[int, int]
    goal: tuple[int, int]
    obstacles: list[tuple[int, int]] = Field(default_factory=list)
    weighted: bool = False


class ThemeConfig(BaseModel):
    """Configuration for visual themes."""
    name: str = "default"
    colors: dict[str, str] = Field(
        default_factory=lambda: {
            "visited": "#4CAF50",
            "frontier": "#2196F3",
            "goal": "#FF9800",
            "path": "#E91E63",
            "obstacle": "#424242",
            "grid": "#E0E0E0",
        }
    )


class VoiceoverConfig(BaseModel):
    """Configuration for voiceover generation."""
    enabled: bool = False
    backend: VoiceoverBackend = VoiceoverBackend.COQUI
    lang: str = "en"
    voice: str = "en_US"
    speed: float = Field(default=1.0, ge=0.1, le=3.0)


class SubtitlesConfig(BaseModel):
    """Configuration for subtitle generation."""
    enabled: bool = False
    mode: SubtitleMode = SubtitleMode.BASELINE
    format: SubtitleFormat = SubtitleFormat.SRT
    burn_in: bool = False


class RenderConfig(BaseModel):
    """Configuration for video rendering."""
    resolution: tuple[int, int] = (1920, 1080)
    frame_rate: int = Field(default=30, ge=1, le=120)
    quality: RenderQuality = RenderQuality.MEDIUM
    format: RenderFormat = RenderFormat.MP4


class TimingConfig(BaseModel):
    """Configuration for timing and pacing."""
    mode: TimingMode = TimingMode.NORMAL
    ui: float = Field(default=1.0, ge=0.1, le=10.0)
    events: float = Field(default=0.8, ge=0.1, le=10.0)
    effects: float = Field(default=0.5, ge=0.1, le=10.0)
    waits: float = Field(default=0.5, ge=0.1, le=10.0)
    multipliers: dict[str, float] = Field(
        default_factory=lambda: {
            "draft": 0.5,
            "normal": 1.0,
            "fast": 0.25,
        }
    )

    def base_for(self, action: str, mode: str | None = None) -> float:
        """Get base timing for an action in the specified mode."""
        bucket = self._bucket_for_action(action)
        multiplier = self.multipliers.get(mode or self.mode.value, 1.0)
        return getattr(self, bucket) * multiplier

    def _bucket_for_action(self, action: str) -> str:
        """Map action name to timing bucket (ui/events/effects/waits)."""
        # Default mapping - can be extended based on action patterns
        action_lower = action.lower()

        if any(keyword in action_lower for keyword in ["show", "hide", "transition", "fade"]):
            return "ui"
        elif any(keyword in action_lower for keyword in ["enqueue", "dequeue", "visit", "explore"]):
            return "events"
        elif any(keyword in action_lower for keyword in ["highlight", "animate", "trace"]):
            return "effects"
        elif any(keyword in action_lower for keyword in ["wait", "pause", "delay"]):
            return "waits"
        else:
            # Default to ui timing for unknown actions
            return "ui"


class VideoConfig(BaseModel):
    """Top-level configuration for video generation."""
    scenario: ScenarioConfig
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    voiceover: VoiceoverConfig = Field(default_factory=VoiceoverConfig)
    subtitles: SubtitlesConfig = Field(default_factory=SubtitlesConfig)
    render: RenderConfig = Field(default_factory=RenderConfig)
    timing: TimingConfig = Field(default_factory=TimingConfig)
