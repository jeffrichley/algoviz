"""Configuration models for ALGOViz.

This module provides Pydantic models for all configuration aspects of ALGOViz,
including scenarios, themes, timing, and other core configurations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple
from pathlib import Path
from pydantic import BaseModel, Field


class TimingMode(str, Enum):
    """Timing modes for video generation."""
    DRAFT = "draft"
    NORMAL = "normal"
    FAST = "fast"


class ScenarioConfig(BaseModel):
    """Configuration for algorithm scenarios."""
    name: str = Field(..., description="Scenario name")
    obstacles: List[Tuple[int, int]] = Field(default_factory=list, description="List of obstacle positions")
    start: Tuple[int, int] = Field(default=(0, 0), description="Starting position")
    goal: Tuple[int, int] = Field(default=(9, 9), description="Goal position")
    grid_size: Tuple[int, int] = Field(default=(10, 10), description="Grid dimensions")
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"


class ThemeConfig(BaseModel):
    """Configuration for visual themes."""
    name: str = "default"
    colors: Dict[str, str] = Field(
        default_factory=lambda: {
            "visited": "#4CAF50",
            "frontier": "#2196F3",
            "goal": "#FF9800",
            "path": "#E91E63",
            "obstacle": "#424242",
            "grid": "#E0E0E0",
        },
        description="Color scheme for different elements"
    )
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"


class TimingConfig(BaseModel):
    """Configuration for timing and animation speeds."""
    mode: TimingMode = TimingMode.NORMAL
    step_duration: float = Field(default=1.0, ge=0.1, le=10.0, description="Duration of each algorithm step")
    effect_duration: float = Field(default=0.5, ge=0.1, le=10.0, description="Duration of visual effects")
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"


@dataclass
class WidgetConfigSpec:
    """Widget configuration specification for hydra-zen."""
    _target_: str
    # Widget-specific parameters will be added dynamically
    
    class Config:
        extra = "allow"  # Allow widget-specific parameters


class SceneConfig(BaseModel):
    """Complete scene configuration for algorithm visualization.
    
    Fully hydra-zen compatible scene configuration that defines:
    - Algorithm-specific widget layouts
    - Widget parameters and customizations
    - Event binding configurations
    """
    name: str = Field(..., description="Scene configuration name")
    algorithm: str = Field(..., description="Target algorithm (bfs, dfs, dijkstra)")
    widgets: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Widget configurations with _target_ and parameters or instantiated widgets"
    )
    event_bindings: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Event to widget action bindings"
    )
    
    class Config:
        extra = "forbid"
        validate_assignment = True
        arbitrary_types_allowed = True  # Allow widget objects
