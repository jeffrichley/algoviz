"""System mediator for coordinating manager initialization."""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ManagerInfo:
    """Information about a registered manager."""
    name: str
    manager: Any
    dependencies: list[str]
    initialized: bool = False


class SystemMediator:
    """Mediates communication and initialization between managers."""

    def __init__(self):
        self._managers: dict[str, ManagerInfo] = {}
        self._initialization_order: list[str] = []
        self._initialization_complete = False

    def register_manager(self, name: str, manager: Any, dependencies: list[str] = None) -> None:
        """Register a manager with its dependencies.
        
        Args:
            name: Unique name for the manager
            manager: The manager instance
            dependencies: List of manager names this manager depends on
        """
        if dependencies is None:
            dependencies = []

        manager_info = ManagerInfo(
            name=name,
            manager=manager,
            dependencies=dependencies
        )

        self._managers[name] = manager_info
        logger.debug(f"Registered manager: {name} with dependencies: {dependencies}")

    def initialize_all(self, force: bool = False) -> None:
        """Initialize all managers in dependency order.
        
        Args:
            force: If True, re-initialize even if already initialized
            
        Raises:
            RuntimeError: If initialization fails
        """
        if self._initialization_complete and not force:
            logger.debug("All managers already initialized, skipping")
            return

        try:
            logger.info("Initializing all managers in dependency order...")

            # Calculate initialization order based on dependencies
            self._calculate_initialization_order()

            # Initialize managers in order
            for manager_name in self._initialization_order:
                self._initialize_manager(manager_name)

            self._initialization_complete = True
            logger.info("All managers initialized successfully")

        except Exception as e:
            logger.error(f"Manager initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize managers: {e}") from e

    def _calculate_initialization_order(self) -> None:
        """Calculate the order to initialize managers based on dependencies."""
        # Use topological sort to determine initialization order
        visited = set()
        temp_visited = set()
        order = []

        def visit(manager_name: str):
            if manager_name in temp_visited:
                raise RuntimeError(f"Circular dependency detected involving: {manager_name}")
            if manager_name in visited:
                return

            temp_visited.add(manager_name)

            # Visit dependencies first
            manager_info = self._managers[manager_name]
            for dep in manager_info.dependencies:
                if dep not in self._managers:
                    raise RuntimeError(f"Manager '{manager_name}' depends on unknown manager: {dep}")
                visit(dep)

            temp_visited.remove(manager_name)
            visited.add(manager_name)
            order.append(manager_name)

        # Visit all managers
        for manager_name in self._managers:
            if manager_name not in visited:
                visit(manager_name)

        self._initialization_order = order
        logger.debug(f"Initialization order: {self._initialization_order}")

    def _initialize_manager(self, manager_name: str) -> None:
        """Initialize a specific manager."""
        manager_info = self._managers[manager_name]

        if manager_info.initialized:
            logger.debug(f"Manager {manager_name} already initialized, skipping")
            return

        try:
            logger.info(f"Initializing manager: {manager_name}")

            # Call the appropriate initialization method based on manager type
            if hasattr(manager_info.manager, 'register_all'):
                manager_info.manager.register_all()
            elif hasattr(manager_info.manager, 'setup_store'):
                manager_info.manager.setup_store()
            elif hasattr(manager_info.manager, 'initialize_builders'):
                manager_info.manager.initialize_builders()
            else:
                logger.warning(f"Manager {manager_name} has no recognized initialization method")

            manager_info.initialized = True
            logger.info(f"Manager {manager_name} initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize manager {manager_name}: {e}")
            raise

    def get_manager(self, name: str) -> Any | None:
        """Get a manager by name."""
        manager_info = self._managers.get(name)
        return manager_info.manager if manager_info else None

    def is_initialized(self) -> bool:
        """Check if all managers are initialized."""
        return self._initialization_complete

    def get_initialization_order(self) -> list[str]:
        """Get the initialization order of managers."""
        return self._initialization_order.copy()

    def reset_for_testing(self) -> None:
        """Reset mediator state for testing."""
        for manager_info in self._managers.values():
            if hasattr(manager_info.manager, 'reset_for_testing'):
                manager_info.manager.reset_for_testing()
            manager_info.initialized = False

        self._initialization_complete = False
        self._initialization_order = []
        logger.debug("Mediator state reset for testing")
