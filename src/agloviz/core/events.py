"""VizEvent system for ALGOViz.

This module provides the core event system that bridges algorithm logic
with the visualization layer through standardized VizEvent objects.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PayloadKey(str, Enum):
    """Standardized payload keys for VizEvents."""
    NODE = "node"           # tuple[int,int] - Grid position or node identifier
    POS = "pos"             # tuple[int,int] - Alternative to node for position
    WEIGHT = "weight"       # float - Edge weight or node cost
    PARENT = "parent"       # tuple[int,int] - Parent node in search tree


class VizEvent(BaseModel):
    """A visualization event emitted by algorithm adapters.
    
    VizEvents are the standardized way algorithms communicate their state
    changes to the visualization system.
    """
    type: str = Field(..., description="Event type (e.g., 'enqueue', 'visit', 'relax')")
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured metadata (node, pos, weight)"
    )
    step_index: int = Field(..., description="Monotonically increasing step counter")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata (complexity, counters)"
    )


def validate_event_payload(event_type: str, payload: dict[str, Any]) -> list[str]:
    """Validate payload against standardized keys for event type.
    
    Args:
        event_type: The type of event being validated
        payload: The payload dictionary to validate
        
    Returns:
        List of validation errors, empty if valid
    """
    errors = []

    # Common validations for graph algorithms
    if PayloadKey.NODE in payload:
        node = payload[PayloadKey.NODE]
        if not isinstance(node, (tuple, list)) or len(node) != 2:
            errors.append(f"'{PayloadKey.NODE}' must be a tuple/list of length 2")
        elif not all(isinstance(x, int) for x in node):
            errors.append(f"'{PayloadKey.NODE}' coordinates must be integers")

    if PayloadKey.PARENT in payload:
        parent = payload[PayloadKey.PARENT]
        if not isinstance(parent, (tuple, list)) or len(parent) != 2:
            errors.append(f"'{PayloadKey.PARENT}' must be a tuple/list of length 2")
        elif not all(isinstance(x, int) for x in parent):
            errors.append(f"'{PayloadKey.PARENT}' coordinates must be integers")

    if PayloadKey.WEIGHT in payload:
        weight = payload[PayloadKey.WEIGHT]
        if not isinstance(weight, (int, float)):
            errors.append(f"'{PayloadKey.WEIGHT}' must be a number")
        elif weight < 0:
            errors.append(f"'{PayloadKey.WEIGHT}' must be non-negative")

    return errors
