"""Configuration models for ALGOViz.

This module provides Pydantic models for all configuration aspects of ALGOViz,
including scenarios, themes, timing, and other core configurations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TimingMode(str, Enum):
    """Timing modes for video generation."""
    DRAFT = "draft"
    NORMAL = "normal"
    FAST = "fast"


class ScenarioConfig(BaseModel):
    """Configuration for algorithm scenarios."""
    name: str = Field(..., description="Scenario name")
    obstacles: list[tuple[int, int]] = Field(default_factory=list, description="List of obstacle positions")
    start: tuple[int, int] = Field(default=(0, 0), description="Starting position")
    goal: tuple[int, int] = Field(default=(9, 9), description="Goal position")
    grid_size: tuple[int, int] = Field(default=(10, 10), description="Grid dimensions")

    class Config:
        """Pydantic configuration."""
        extra = "forbid"


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
        },
        description="Color scheme for different elements"
    )

    class Config:
        """Pydantic configuration."""
        extra = "forbid"


class TimingConfig(BaseModel):
    """Configuration for timing and animation speeds with bucket system."""
    mode: TimingMode = TimingMode.NORMAL
    ui: float = Field(default=1.0, ge=0.1, le=10.0, description="UI transition timing bucket")
    events: float = Field(default=0.8, ge=0.1, le=10.0, description="Algorithm event timing bucket")
    effects: float = Field(default=0.5, ge=0.1, le=10.0, description="Visual effects timing bucket")
    waits: float = Field(default=0.5, ge=0.1, le=10.0, description="Wait/pause timing bucket")
    multipliers: dict[str, float] = Field(
        default_factory=lambda: {"draft": 0.5, "normal": 1.0, "fast": 0.25},
        description="Mode multipliers for timing adjustments"
    )

    def base_for(self, action: str, mode: str | None = None) -> float:
        """Get base duration for an action with optional mode override."""
        bucket = self._bucket_for_action(action)
        m = self.multipliers[mode or self.mode.value]
        return getattr(self, bucket) * m

    def _bucket_for_action(self, action: str) -> str:
        """Map action name to timing category bucket."""
        # Map action name → category (ui/events/effects/waits)
        if action in ["show_title", "show_grid", "hide_grid", "show_widgets", "hide_widgets"]:
            return "ui"
        elif action in ["place_start", "place_goal", "visit_node", "add_to_queue", "remove_from_queue"]:
            return "events"
        elif action in ["highlight", "animate_path", "fade_out", "pulse"]:
            return "effects"
        else:
            # Default to ui bucket for unknown actions
            return "ui"

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
    widgets: dict[str, Any] = Field(
        default_factory=dict,
        description="Widget configurations with _target_ and parameters or instantiated widgets"
    )
    event_bindings: dict[str, list[dict[str, Any]]] = Field(
        default_factory=dict,
        description="Event to widget action bindings"
    )

    class Config:
        extra = "forbid"
        validate_assignment = True
        arbitrary_types_allowed = True  # Allow widget objects
