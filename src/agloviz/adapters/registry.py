"""Adapter registry for managing algorithm adapters.

This module provides centralized registration and lookup of algorithm adapters,
following the same pattern as other registries in the project.
"""


from agloviz.adapters.protocol import AlgorithmAdapter


class AdapterRegistry:
    """Registry for algorithm adapters.
    
    Provides centralized registration and lookup of adapters,
    following the established registry pattern in the codebase.
    """
    _adapters: dict[str, type[AlgorithmAdapter]] = {}

    @classmethod
    def register(cls, adapter_class: type[AlgorithmAdapter]) -> None:
        """Register an algorithm adapter.
        
        Args:
            adapter_class: The adapter class to register
            
        Raises:
            ValueError: If adapter name is already registered
        """
        if adapter_class.name in cls._adapters:
            raise ValueError(f"Algorithm '{adapter_class.name}' is already registered")
        cls._adapters[adapter_class.name] = adapter_class

    @classmethod
    def get(cls, name: str) -> type[AlgorithmAdapter]:
        """Get adapter class by name.
        
        Args:
            name: Name of the algorithm adapter
            
        Returns:
            The adapter class
            
        Raises:
            KeyError: If algorithm is not registered
        """
        if name not in cls._adapters:
            raise KeyError(f"Algorithm '{name}' not registered")
        return cls._adapters[name]

    @classmethod
    def list_algorithms(cls) -> list[str]:
        """List all registered algorithm names.
        
        Returns:
            Sorted list of algorithm names
        """
        return sorted(cls._adapters.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered adapters (for testing)."""
        cls._adapters.clear()
