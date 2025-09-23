"""Factory for creating SystemOrchestrator instances via Hydra-zen using Registry Pattern."""

from hydra_zen import builds

from ..core.managers import SystemRegistry


# Factory function for Hydra-zen injection using Registry Pattern
def create_orchestrator():
    """Factory that returns the singleton SystemOrchestrator instance via registry.
    
    This factory uses the SystemRegistry to ensure proper singleton behavior
    and initialization order. The registry handles creating and initializing
    the orchestrator with all dependencies properly resolved.
    
    Returns:
        SystemOrchestrator: The singleton orchestrator instance (fully initialized)
    """
    return SystemRegistry.get_orchestrator()


# Alternative factory for direct creation (for testing)
def create_orchestrator_direct():
    """Factory that creates a new SystemOrchestrator instance directly.
    
    This bypasses the registry and creates a fresh instance.
    Useful for testing or when you need multiple instances.
    
    Returns:
        SystemOrchestrator: A new orchestrator instance (not initialized)
    """
    from ..core.managers import SystemOrchestrator
    return SystemOrchestrator()


# Hydra-zen builds for the factories
OrchestratorFactory = builds(create_orchestrator)
DirectOrchestratorFactory = builds(create_orchestrator_direct)
