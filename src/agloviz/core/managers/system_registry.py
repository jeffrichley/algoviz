"""System registry for managing singleton instances."""

import logging

from agloviz.core.managers.system_orchestrator import SystemOrchestrator

logger = logging.getLogger(__name__)


class SystemRegistry:
    """Registry that manages system instances using the Registry Pattern."""

    _orchestrator: SystemOrchestrator | None = None

    @classmethod
    def get_orchestrator(cls) -> SystemOrchestrator:
        """Get the singleton orchestrator instance.

        Creates and initializes the orchestrator on first access.
        The orchestrator uses the SystemMediator to handle proper
        dependency resolution and initialization order.

        Returns:
            SystemOrchestrator: The singleton orchestrator instance
        """
        if cls._orchestrator is None:
            logger.info("Creating new SystemOrchestrator instance via registry")
            cls._orchestrator = SystemOrchestrator()
            cls._orchestrator.initialize()
        return cls._orchestrator

    @classmethod
    def reset(cls) -> None:
        """Reset registry state.

        This allows starting with a clean state.
        """
        if cls._orchestrator:
            cls._orchestrator.reset_for_testing()
        cls._orchestrator = None
        logger.debug("SystemRegistry reset")

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if orchestrator is initialized.

        Returns:
            bool: True if orchestrator exists and is initialized
        """
        return cls._orchestrator is not None and cls._orchestrator.is_initialized()

    @classmethod
    def get_status(cls) -> dict:
        """Get comprehensive system status.

        Returns:
            dict: Status information about the system
        """
        if cls._orchestrator is None:
            return {"registry_initialized": False, "orchestrator_exists": False}

        status = cls._orchestrator.get_status()
        status["registry_initialized"] = True
        status["orchestrator_exists"] = True
        return status
