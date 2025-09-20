"""Tests for BFS adapter."""

import pytest

from agloviz.adapters.bfs import BFSAdapter, BFSEventType
from agloviz.adapters.protocol import AdapterWrapper
from agloviz.config.models import ScenarioConfig


@pytest.mark.unit
class TestBFSAdapter:
    """Test BFS adapter implementation."""

    def test_adapter_name(self):
        """Test that adapter has correct name."""
        adapter = BFSAdapter()
        assert adapter.name == "bfs"

    def test_simple_bfs_path(self):
        """Test BFS on simple 3x3 grid."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        adapter = BFSAdapter()
        events = list(adapter.run(config))

        # Should have at least initial enqueue and final goal_found
        assert len(events) > 0
        assert events[0].type == BFSEventType.ENQUEUE
        assert events[0].payload["node"] == (0, 0)

        # Last event should be goal_found
        assert events[-1].type == BFSEventType.GOAL_FOUND
        assert events[-1].payload["node"] == (2, 2)

    def test_bfs_with_wrapper_step_indexing(self):
        """Test BFS with AdapterWrapper for step indexing."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        adapter = BFSAdapter()
        wrapper = AdapterWrapper(adapter)
        events = list(wrapper.run_with_indexing(config))

        # Check that step indices are sequential
        for i, event in enumerate(events):
            assert event.step_index == i

    def test_bfs_deterministic_behavior(self):
        """Test that BFS produces deterministic results."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        adapter = BFSAdapter()

        # Run twice and compare
        events1 = list(adapter.run(config))
        events2 = list(adapter.run(config))

        assert len(events1) == len(events2)

        for e1, e2 in zip(events1, events2, strict=False):
            assert e1.type == e2.type
            assert e1.payload == e2.payload

    def test_bfs_start_equals_goal(self):
        """Test BFS when start equals goal."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(0, 0)  # Same as start
        )

        adapter = BFSAdapter()
        events = list(adapter.run(config))

        # Should have enqueue, dequeue, goal_found
        assert len(events) == 3
        assert events[0].type == BFSEventType.ENQUEUE
        assert events[1].type == BFSEventType.DEQUEUE
        assert events[2].type == BFSEventType.GOAL_FOUND

    def test_bfs_event_types(self):
        """Test that BFS emits correct event types."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(1, 1)
        )

        adapter = BFSAdapter()
        events = list(adapter.run(config))

        # Check event type validity
        valid_types = {BFSEventType.ENQUEUE, BFSEventType.DEQUEUE, BFSEventType.GOAL_FOUND}
        for event in events:
            assert event.type in valid_types

    def test_bfs_payload_structure(self):
        """Test that BFS events have correct payload structure."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(1, 1)
        )

        adapter = BFSAdapter()
        events = list(adapter.run(config))

        # All events should have 'node' in payload
        for event in events:
            assert "node" in event.payload
            node = event.payload["node"]
            assert isinstance(node, tuple)
            assert len(node) == 2
            assert all(isinstance(coord, int) for coord in node)

    def test_bfs_with_obstacles(self):
        """Test BFS behavior with obstacles."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_maze.yaml",
            start=(0, 0),
            goal=(4, 4)
        )

        adapter = BFSAdapter()
        events = list(adapter.run(config))

        # Should still find goal despite obstacles
        assert len(events) > 0
        assert events[0].type == BFSEventType.ENQUEUE
        assert events[-1].type == BFSEventType.GOAL_FOUND

    def test_bfs_unreachable_goal(self):
        """Test BFS behavior with unreachable goal."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_unreachable.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        adapter = BFSAdapter()
        events = list(adapter.run(config))

        # Should not find goal - last event should not be goal_found
        assert len(events) > 0
        assert events[-1].type != BFSEventType.GOAL_FOUND

        # Should have explored all reachable nodes
        goal_found_events = [e for e in events if e.type == BFSEventType.GOAL_FOUND]
        assert len(goal_found_events) == 0


@pytest.mark.unit
class TestBFSEventType:
    """Test BFS event type enum."""

    def test_event_types_exist(self):
        """Test that all expected event types exist."""
        assert BFSEventType.ENQUEUE == "enqueue"
        assert BFSEventType.DEQUEUE == "dequeue"
        assert BFSEventType.GOAL_FOUND == "goal_found"

    def test_event_types_are_strings(self):
        """Test that event types work as strings."""
        event_dict = {BFSEventType.ENQUEUE: "handler"}
        assert "enqueue" in event_dict
        assert event_dict["enqueue"] == "handler"
