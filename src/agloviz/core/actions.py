"""Action registry system for storyboard actions."""

from typing import Any, Protocol

from agloviz.core.errors import RegistryError


class ActionHandler(Protocol):
    """Protocol for storyboard action handlers."""
    def __call__(self, scene: Any, args: dict[str, Any], run_time: float, context: dict[str, Any]) -> None:
        """Execute the action with given parameters."""
        ...


class ActionRegistry:
    """Registry for storyboard actions."""
    _actions: dict[str, ActionHandler] = {}

    @classmethod
    def register(cls, name: str, handler: ActionHandler) -> None:
        """Register an action handler."""
        if name in cls._actions:
            raise RegistryError(
                category="ActionRegistry",
                context=f"Action '{name}'",
                issue="already registered",
                remedy="Use a different name or unregister first"
            )
        cls._actions[name] = handler

    @classmethod
    def get(cls, name: str) -> ActionHandler:
        """Get action handler by name."""
        if name not in cls._actions:
            available = ", ".join(sorted(cls._actions.keys()))
            raise RegistryError(
                category="ActionRegistry",
                context=f"Action '{name}'",
                issue="not registered",
                remedy=f"Available actions: {available}"
            )
        return cls._actions[name]

    @classmethod
    def list_actions(cls) -> list[str]:
        """List all registered actions."""
        return sorted(cls._actions.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all actions (for testing)."""
        cls._actions.clear()
