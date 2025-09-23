"""Algorithm adapter protocol and wrapper for ALGOViz.

This module defines the interface that all algorithm adapters must implement
and provides the AdapterWrapper for automatic step indexing.
"""

from collections.abc import Iterator
from typing import Protocol

from agloviz.config.models import ScenarioConfig
from agloviz.core.events import VizEvent


class AlgorithmAdapter(Protocol):
    """Protocol that all algorithm adapters must implement.

    Each algorithm ships with an Adapter that converts algorithm logic
    into a standardized stream of VizEvents.
    """

    name: str

    def run(self, scenario: ScenarioConfig) -> Iterator[VizEvent]:
        """Generate VizEvents for algorithm execution.

        Note: Events yielded WITHOUT step_index - AdapterWrapper assigns them.

        Args:
            scenario: Scenario configuration containing grid, start, goal, etc.

        Yields:
            VizEvent objects representing algorithm state changes
        """
        ...


class AdapterWrapper:
    """Wrapper that automatically assigns step indices to adapter events.

    As specified in SDD Section 8.3, adapters yield raw events without
    step indices, and this wrapper assigns sequential step numbers.
    """

    def __init__(self, adapter: AlgorithmAdapter):
        """Initialize wrapper with an adapter.

        Args:
            adapter: The algorithm adapter to wrap
        """
        self.adapter = adapter

    def run_with_indexing(self, scenario: ScenarioConfig) -> Iterator[VizEvent]:
        """Wrap adapter to automatically assign step indices.

        Args:
            scenario: Scenario configuration to pass to adapter

        Yields:
            VizEvent objects with sequential step_index values
        """
        for i, event in enumerate(self.adapter.run(scenario)):
            # Create new event with step_index assigned
            yield VizEvent(
                type=event.type,
                payload=event.payload,
                step_index=i,
                metadata=event.metadata,
            )
