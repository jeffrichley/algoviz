"""System facade providing simple interface to complex subsystem."""

import logging
from typing import Any

from .builder_manager import BuilderManager
from .resolver_manager import ResolverManager
from .system_mediator import SystemMediator

logger = logging.getLogger(__name__)


class SystemFacade:
    """Facade that provides simple interface to complex subsystem."""

    def __init__(self):
        self._resolver_manager = ResolverManager()
        self._builder_manager = BuilderManager()
        self._mediator = SystemMediator()
        self._initialized = False

    def initialize_system(self, force: bool = False) -> None:
        """Initialize the complete system.

        Args:
            force: If True, re-initialize even if already initialized

        Raises:
            RuntimeError: If initialization fails
        """
        if self._initialized and not force:
            logger.debug("System already initialized, skipping")
            return

        try:
            logger.info("Initializing ALGOViz system...")

            # Register managers with mediator
            self._mediator.register_manager("resolver", self._resolver_manager, [])
            self._mediator.register_manager(
                "store", self._get_store_manager(), ["resolver"]
            )
            self._mediator.register_manager("builder", self._builder_manager, ["store"])

            # Initialize all managers in dependency order
            self._mediator.initialize_all(force=force)

            self._initialized = True
            logger.info("ALGOViz system initialization completed successfully")

        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize system: {e}") from e

    def _get_store_manager(self):
        """Get the store manager instance."""
        from agloviz.config.store_manager import StoreManager

        return StoreManager

    def get_resolver_manager(self) -> ResolverManager:
        """Get the resolver manager."""
        return self._resolver_manager

    def get_builder_manager(self) -> BuilderManager:
        """Get the builder manager."""
        return self._builder_manager

    def get_store_manager(self):
        """Get the store manager."""
        return self._get_store_manager()

    def get_yaml_config(self, name: str) -> Any | None:
        """Get a YAML config by name."""
        return self._builder_manager.get_yaml_config(name)

    def get_all_yaml_configs(self) -> dict[str, Any]:
        """Get all YAML configs."""
        return self._builder_manager.get_all_yaml_configs()

    def is_initialized(self) -> bool:
        """Check if system is initialized."""
        return self._initialized

    def reset_for_testing(self) -> None:
        """Reset system state for testing."""
        self._mediator.reset_for_testing()
        self._initialized = False
        logger.debug("System state reset for testing")

    def get_initialization_status(self) -> dict[str, Any]:
        """Get status of all system components."""
        return {
            "system_initialized": self._initialized,
            "resolvers_registered": self._resolver_manager.is_registered(),
            "builders_initialized": self._builder_manager.is_initialized(),
            "store_initialized": self._get_store_manager()._initialized,
            "initialization_order": self._mediator.get_initialization_order(),
        }
