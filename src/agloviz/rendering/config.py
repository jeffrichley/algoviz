"""Render Configuration Models - Hydra-zen First.

Configuration models for video rendering using Pydantic validation
and hydra-zen structured configs.
"""

from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field
from hydra_zen import builds


class RenderFormat(str, Enum):
    """Supported video output formats."""
    MP4 = "mp4"
    GIF = "gif" 
    PNG_SEQUENCE = "png_sequence"


class RenderQuality(str, Enum):
    """Render quality presets."""
    DRAFT = "draft"     # Fast, low quality for previews
    MEDIUM = "medium"   # Balanced quality/speed
    HIGH = "high"       # High quality for final output


class RenderConfig(BaseModel):
    """Video rendering configuration.
    
    Defines output format, quality, resolution and encoding settings
    for algorithm visualization videos.
    """
    resolution: tuple[int, int] = Field(default=(1280, 720), description="Video resolution (width, height)")
    frame_rate: int = Field(default=30, description="Frames per second")
    format: RenderFormat = Field(default=RenderFormat.MP4, description="Output format")
    quality: RenderQuality = Field(default=RenderQuality.MEDIUM, description="Quality preset")
    output_dir: Path = Field(default=Path("output/"), description="Output directory")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


# Hydra-zen structured config for RenderConfig
RenderConfigZen = builds(
    RenderConfig,
    populate_full_signature=True
)
