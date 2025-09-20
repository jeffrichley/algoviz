"""Algorithm adapters for converting algorithm implementations to VizEvents.

This module provides the adapter pattern for converting algorithm implementations
into standardized VizEvent streams that can be consumed by the visualization system.
"""

from .bfs import BFSAdapter
from .protocol import AdapterWrapper, AlgorithmAdapter
from .registry import AdapterRegistry

# Auto-register BFS adapter
AdapterRegistry.register(BFSAdapter)

__all__ = ["AlgorithmAdapter", "AdapterWrapper", "AdapterRegistry", "BFSAdapter"]
