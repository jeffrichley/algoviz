"""System orchestrator - coordinates system managers."""

import logging

from .system_facade import SystemFacade

logger = logging.getLogger(__name__)


class SystemOrchestrator:
    """Orchestrates all system managers - regular class managed by SystemRegistry."""

    def __init__(self):
        self._facade = SystemFacade()
        self._system_initialized = False
        logger.debug("SystemOrchestrator created")

    def initialize(self, force: bool = False) -> 'SystemOrchestrator':
        """Initialize the complete ALGOViz system.
        
        Uses the SystemMediator to handle proper dependency resolution
        and initialization order for all managers.
        
        Args:
            force: If True, re-initialize even if already initialized
            
        Returns:
            Self for method chaining
            
        Raises:
            RuntimeError: If initialization fails
        """
        if self._system_initialized and not force:
            logger.debug("System already initialized")
            return self

        try:
            logger.info("Starting ALGOViz system initialization...")
            self._facade.initialize_system(force=force)
            self._system_initialized = True
            logger.info("ALGOViz system initialization completed successfully")
            return self

        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize ALGOViz system: {e}") from e

    def get_facade(self) -> SystemFacade:
        """Get the system facade for accessing individual managers."""
        return self._facade

    def get_resolver_manager(self):
        """Get the resolver manager."""
        return self._facade.get_resolver_manager()

    def get_builder_manager(self):
        """Get the builder manager."""
        return self._facade.get_builder_manager()

    def get_store_manager(self):
        """Get the store manager."""
        return self._facade.get_store_manager()

    def get_yaml_config(self, name: str):
        """Get a YAML config by name."""
        return self._facade.get_yaml_config(name)

    def get_all_yaml_configs(self):
        """Get all YAML configs."""
        return self._facade.get_all_yaml_configs()

    def is_initialized(self) -> bool:
        """Check if system is initialized."""
        return self._system_initialized

    def get_status(self) -> dict:
        """Get comprehensive system status."""
        if not self._system_initialized:
            return {"system_initialized": False}
        return self._facade.get_initialization_status()

    def reset_for_testing(self) -> None:
        """Reset system state for testing."""
        self._facade.reset_for_testing()
        self._system_initialized = False
        logger.debug("System reset for testing")
