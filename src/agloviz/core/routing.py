"""Event routing system for ALGOViz.

This module provides the routing system that connects VizEvents to widget handlers,
enabling the Director to dispatch events to appropriate visual components.
"""

from typing import TypeAlias

# Type alias for routing maps as specified in design doc
RoutingMap: TypeAlias = dict[str, list[str]]  # event_type -> handler_names


# BFS routing map exactly as specified in design document
BFS_ROUTING: RoutingMap = {
    "enqueue": ["queue.highlight_enqueue", "grid.mark_frontier"],
    "dequeue": ["queue.highlight_dequeue"],
    "goal_found": ["grid.flash_goal", "hud.show_success"]
}


class RoutingRegistry:
    """Registry for event routing maps.
    
    Stores routing maps keyed by algorithm name, as specified in the design document.
    Routing maps are overrideable by Storyboard beat args.
    """
    _routing_maps: dict[str, RoutingMap] = {}

    @classmethod
    def register(cls, algorithm: str, routing_map: RoutingMap) -> None:
        """Register routing map for algorithm.
        
        Args:
            algorithm: Name of the algorithm
            routing_map: Dictionary mapping event types to handler names
            
        Raises:
            ValueError: If algorithm routing is already registered
        """
        if algorithm in cls._routing_maps:
            raise ValueError(f"Routing for algorithm '{algorithm}' is already registered")
        cls._routing_maps[algorithm] = routing_map

    @classmethod
    def get(cls, algorithm: str) -> RoutingMap:
        """Get routing map for algorithm.
        
        Args:
            algorithm: Name of the algorithm
            
        Returns:
            Routing map for the algorithm
            
        Raises:
            KeyError: If no routing map exists for algorithm
        """
        if algorithm not in cls._routing_maps:
            raise KeyError(f"No routing map for algorithm '{algorithm}'")
        return cls._routing_maps[algorithm]

    @classmethod
    def list_algorithms(cls) -> list[str]:
        """List algorithms with routing maps.
        
        Returns:
            Sorted list of algorithm names with routing maps
        """
        return sorted(cls._routing_maps.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all routing maps (for testing)."""
        cls._routing_maps.clear()


def validate_routing_map(routing_map: RoutingMap) -> list[str]:
    """Validate routing map structure and handler names.
    
    Args:
        routing_map: Routing map to validate
        
    Returns:
        List of validation errors, empty if valid
    """
    errors = []

    for event_type, handlers in routing_map.items():
        if not isinstance(event_type, str):
            errors.append(f"Event type must be string, got {type(event_type)}")

        if not isinstance(handlers, list):
            errors.append(f"Handlers for '{event_type}' must be list, got {type(handlers)}")
            continue

        for handler in handlers:
            if not isinstance(handler, str):
                errors.append(f"Handler name must be string, got {type(handler)}")
                continue

            # Validate handler format (widget.action)
            if '.' not in handler:
                errors.append(f"Handler '{handler}' must be in format 'widget.action'")
            else:
                parts = handler.split('.')
                if len(parts) != 2:
                    errors.append(f"Handler '{handler}' must have exactly one dot")
                elif not all(part for part in parts):
                    errors.append(f"Handler '{handler}' has empty widget or action name")

    return errors


def validate_event_coverage(routing_map: RoutingMap, event_types: set[str]) -> list[str]:
    """Validate that all event types have handlers.
    
    Args:
        routing_map: Routing map to check
        event_types: Set of event types that should have handlers
        
    Returns:
        List of uncovered event types
    """
    uncovered = []
    for event_type in event_types:
        if event_type not in routing_map:
            uncovered.append(event_type)
        elif not routing_map[event_type]:
            uncovered.append(f"{event_type} (empty handlers)")

    return uncovered


# Register BFS routing map
RoutingRegistry.register("bfs", BFS_ROUTING)
