"""Resolver management for ALGOViz system."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ResolverManager:
    """Manages registration and lifecycle of custom resolvers."""

    def __init__(self):
        self._resolvers_registered = False
        self._registered_resolvers: dict[str, Any] = {}
        self._initialization_error: Exception | None = None

    def register_all(self, force: bool = False) -> None:
        """Register all custom resolvers.
        
        Args:
            force: If True, re-register even if already registered
            
        Raises:
            RuntimeError: If registration fails
        """
        if self._resolvers_registered and not force:
            logger.debug("Resolvers already registered, skipping")
            return

        try:
            logger.info("Registering custom resolvers...")

            # Import and register resolvers
            from agloviz.core.resolvers import register_custom_resolvers
            register_custom_resolvers()

            # Track what we've registered
            self._registered_resolvers = {
                'event_data': True,
                'timing_value': True,
                'config_value': True
            }

            self._resolvers_registered = True
            self._initialization_error = None
            logger.info("Resolver registration completed successfully")

        except Exception as e:
            self._initialization_error = e
            logger.error(f"Resolver registration failed: {e}")
            raise RuntimeError(f"Failed to register resolvers: {e}") from e

    def is_registered(self) -> bool:
        """Check if resolvers are registered."""
        return self._resolvers_registered

    def get_registered_resolvers(self) -> dict[str, Any]:
        """Get list of registered resolvers."""
        return self._registered_resolvers.copy()

    def reset_for_testing(self) -> None:
        """Reset resolver state for testing."""
        self._resolvers_registered = False
        self._registered_resolvers = {}
        self._initialization_error = None
        logger.debug("Resolver state reset for testing")

    def get_initialization_error(self) -> Exception | None:
        """Get initialization error if any."""
        return self._initialization_error
