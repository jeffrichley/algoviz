"""Storyboard DSL implementation for ALGOViz.

This module provides the core data models, validation, and loading functionality
for the storyboard DSL that describes videos as Acts → Shots → Beats.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console

from agloviz.core.errors import ConfigError, FileContext


class Beat(BaseModel):
    """A single action within a shot."""

    action: str = Field(..., description="Action to execute")
    args: dict[str, Any] = Field(default_factory=dict, description="Action arguments")
    narration: str | None = Field(None, description="Narration text for this beat")
    bookmarks: dict[str, str] = Field(
        default_factory=dict, description="Bookmark word -> action mapping"
    )
    min_duration: float | None = Field(
        None, ge=0.1, le=30.0, description="Minimum duration override"
    )
    max_duration: float | None = Field(
        None, ge=0.1, le=30.0, description="Maximum duration override"
    )


class Shot(BaseModel):
    """A sequence of beats that form a coherent visual sequence."""

    beats: list[Beat] = Field(..., description="List of beats in this shot")


class Act(BaseModel):
    """A collection of shots that form a major section of the video."""

    title: str = Field(..., description="Title of this act")
    shots: list[Shot] = Field(..., description="List of shots in this act")


class Storyboard(BaseModel):
    """Complete storyboard containing all acts for a video."""

    acts: list[Act] = Field(..., description="List of acts in this storyboard")


class ActionRegistry:
    """Registry for storyboard actions."""

    def __init__(self):
        self._actions: dict[str, Callable] = {}
        self.console = Console()

    def register(self, name: str, handler: Callable) -> None:
        """Register an action handler.

        Args:
            name: Action name (e.g., 'show_title', 'play_events')
            handler: Callable that implements the action

        Raises:
            ConfigError: If action name is invalid or already registered
        """
        if not name or not isinstance(name, str):
            raise ConfigError(
                issue=f"Invalid action name: {name}",
                remedy="Action names must be non-empty strings",
            )

        if name in self._actions:
            raise ConfigError(
                issue=f"Action '{name}' is already registered",
                remedy="Use a different name or unregister the existing action",
            )

        self._actions[name] = handler
        self.console.print(f"[green]Registered action: {name}[/green]")

    def get(self, name: str) -> Callable:
        """Get action handler.

        Args:
            name: Action name to look up

        Returns:
            Action handler callable

        Raises:
            ConfigError: If action is not found
        """
        if name not in self._actions:
            available = (
                ", ".join(sorted(self._actions.keys())) if self._actions else "none"
            )
            raise ConfigError(
                issue=f"Unknown action '{name}'",
                remedy=f"Available actions: {available}",
            )

        return self._actions[name]

    def list_actions(self) -> list[str]:
        """List all registered action names."""
        return sorted(self._actions.keys())

    def clear(self) -> None:
        """Clear all registered actions."""
        self._actions.clear()


class StoryboardLoader:
    """Loads and validates storyboard YAML files."""

    def __init__(self):
        self.console = Console()

    def load_from_yaml(self, yaml_path: str) -> Storyboard:
        """Load storyboard from YAML with validation and error context.

        Args:
            yaml_path: Path to storyboard YAML file

        Returns:
            Validated Storyboard object

        Raises:
            ConfigError: If file cannot be loaded or validation fails
        """
        path = Path(yaml_path)

        if not path.exists():
            raise ConfigError(
                issue=f"Storyboard file not found: {yaml_path}",
                context=FileContext(str(path)),
                remedy="Verify the file path exists and is accessible",
            )

        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(
                issue=f"Invalid YAML syntax: {e}",
                context=FileContext(str(path)),
                remedy="Check YAML syntax and formatting",
            ) from e
        except Exception as e:
            raise ConfigError(
                issue=f"Failed to read file: {e}",
                context=FileContext(str(path)),
                remedy="Check file permissions and encoding",
            ) from e

        if not data:
            raise ConfigError(
                issue="Storyboard file is empty",
                context=FileContext(str(path)),
                remedy="Add storyboard content with acts, shots, and beats",
            )

        # Validate with Pydantic models
        try:
            storyboard = Storyboard(**data)
        except ValidationError as e:
            raise ConfigError(
                issue=f"Storyboard validation failed: {e}",
                context=FileContext(str(path)),
                remedy="Check storyboard structure and field types",
            ) from e

        return storyboard

    def validate_actions(
        self, storyboard: Storyboard, registry: ActionRegistry
    ) -> list[str]:
        """Validate that all actions in storyboard are registered.

        Args:
            storyboard: Storyboard to validate
            registry: Action registry to check against

        Returns:
            List of unknown actions found
        """
        unknown_actions = []

        for act_idx, act in enumerate(storyboard.acts):
            for shot_idx, shot in enumerate(act.shots):
                for beat_idx, beat in enumerate(shot.beats):
                    if beat.action not in registry.list_actions():
                        unknown_actions.append(
                            f"Act {act_idx + 1}/Shot {shot_idx + 1}/Beat {beat_idx + 1}: '{beat.action}'"
                        )

        return unknown_actions


# Global action registry instance
_action_registry = ActionRegistry()


def get_action_registry() -> ActionRegistry:
    """Get the global action registry instance."""
    return _action_registry


def register_action(name: str, handler: Callable) -> None:
    """Register an action with the global registry."""
    _action_registry.register(name, handler)


def get_action(name: str) -> Callable:
    """Get an action from the global registry."""
    return _action_registry.get(name)
