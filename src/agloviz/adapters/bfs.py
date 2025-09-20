"""BFS (Breadth-First Search) adapter for ALGOViz.

This module implements the BFS algorithm adapter that generates VizEvents
for visualization of the breadth-first search algorithm.
"""

from collections import deque
from collections.abc import Iterator
from enum import Enum

from agloviz.config.models import ScenarioConfig
from agloviz.core.events import VizEvent
from agloviz.core.scenario import ScenarioLoader


class BFSEventType(str, Enum):
    """Event types emitted by BFS adapter."""
    ENQUEUE = "enqueue"
    DEQUEUE = "dequeue"
    GOAL_FOUND = "goal_found"


class BFSAdapter:
    """BFS algorithm adapter.
    
    Implements breadth-first search algorithm and emits VizEvents
    for each step of the algorithm execution.
    """
    name = "bfs"

    def run(self, scenario: ScenarioConfig) -> Iterator[VizEvent]:
        """Generate VizEvents for BFS algorithm execution.
        
        Note: Events yielded WITHOUT step_index - AdapterWrapper assigns them.
        
        Args:
            scenario: Scenario configuration containing grid, start, goal, etc.
            
        Yields:
            VizEvent objects representing BFS state changes
        """
        # Convert ScenarioConfig to Scenario protocol
        scenario_runtime = ScenarioLoader.from_config(scenario)

        queue = deque([scenario_runtime.start])
        visited = {scenario_runtime.start}

        # Yield initial enqueue event (step_index will be assigned by AdapterWrapper)
        yield VizEvent(
            type=BFSEventType.ENQUEUE,
            payload={"node": scenario_runtime.start},
            step_index=0  # Will be overridden by AdapterWrapper
        )

        while queue:
            node = queue.popleft()
            yield VizEvent(
                type=BFSEventType.DEQUEUE,
                payload={"node": node},
                step_index=0  # Will be overridden by AdapterWrapper
            )

            if node == scenario_runtime.goal:
                yield VizEvent(
                    type=BFSEventType.GOAL_FOUND,
                    payload={"node": node},
                    step_index=0  # Will be overridden by AdapterWrapper
                )
                break

            # Get neighbors in sorted order for deterministic behavior
            neighbors = sorted(scenario_runtime.neighbors(node))

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    yield VizEvent(
                        type=BFSEventType.ENQUEUE,
                        payload={"node": neighbor},
                        step_index=0  # Will be overridden by AdapterWrapper
                    )
