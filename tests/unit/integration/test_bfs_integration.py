"""Integration tests for BFS system."""

import pytest

from agloviz.adapters.bfs import BFSAdapter
from agloviz.adapters.protocol import AdapterWrapper
from agloviz.adapters.registry import AdapterRegistry
from agloviz.config.models import ScenarioConfig
from agloviz.core.routing import RoutingRegistry
from agloviz.core.scenario import ContractTestHarness, ScenarioLoader


@pytest.mark.unit
class TestBFSIntegration:
    """Test complete BFS workflow from config to events."""

    def setup_method(self):
        """Clear registries before each test."""
        AdapterRegistry.clear()
        RoutingRegistry.clear()

        # Re-register components
        AdapterRegistry.register(BFSAdapter)
        from agloviz.core.routing import BFS_ROUTING
        RoutingRegistry.register("bfs", BFS_ROUTING)

    def teardown_method(self):
        """Clear registries after each test."""
        AdapterRegistry.clear()
        RoutingRegistry.clear()

    def test_bfs_complete_workflow(self):
        """Test complete BFS workflow from config to events."""
        # Load scenario from YAML
        scenario_config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(2, 2),
            obstacles=[],
            weighted=False
        )

        # Create BFS adapter with wrapper
        adapter_class = AdapterRegistry.get("bfs")
        adapter = adapter_class()
        wrapper = AdapterWrapper(adapter)

        # Generate events
        events = list(wrapper.run_with_indexing(scenario_config))

        # Validate event sequence
        assert len(events) > 0
        assert events[0].type == "enqueue"
        assert events[0].step_index == 0
        assert events[0].payload["node"] == (0, 0)
        assert events[-1].type == "goal_found"
        assert events[-1].payload["node"] == (2, 2)

        # Check step index monotonicity
        for i, event in enumerate(events):
            assert event.step_index == i

    def test_scenario_contract_compliance(self):
        """Test that scenarios satisfy the runtime contract."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        scenario = ScenarioLoader.from_config(config)
        harness = ContractTestHarness()

        violations = harness.verify_scenario(scenario)
        assert not violations, f"Contract violations: {violations}"

    def test_registry_integration(self):
        """Test that registries work together."""
        # Check adapter registry
        algorithms = AdapterRegistry.list_algorithms()
        assert "bfs" in algorithms

        # Check routing registry
        routing_algorithms = RoutingRegistry.list_algorithms()
        assert "bfs" in routing_algorithms

        # Get routing map
        routing_map = RoutingRegistry.get("bfs")
        assert "enqueue" in routing_map
        assert "dequeue" in routing_map
        assert "goal_found" in routing_map

    def test_deterministic_behavior(self):
        """Test that the system produces deterministic results."""
        scenario_config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(1, 1)
        )

        adapter_class = AdapterRegistry.get("bfs")

        # Run twice and compare
        adapter1 = adapter_class()
        wrapper1 = AdapterWrapper(adapter1)
        events1 = list(wrapper1.run_with_indexing(scenario_config))

        adapter2 = adapter_class()
        wrapper2 = AdapterWrapper(adapter2)
        events2 = list(wrapper2.run_with_indexing(scenario_config))

        assert len(events1) == len(events2)

        for e1, e2 in zip(events1, events2, strict=False):
            assert e1.type == e2.type
            assert e1.payload == e2.payload
            assert e1.step_index == e2.step_index

    def test_complex_scenario(self):
        """Test BFS on complex scenario with obstacles."""
        scenario_config = ScenarioConfig(
            name="maze",
            grid_file="grids/test_maze.yaml",
            start=(0, 0),
            goal=(4, 4)
        )

        adapter_class = AdapterRegistry.get("bfs")
        adapter = adapter_class()
        wrapper = AdapterWrapper(adapter)

        events = list(wrapper.run_with_indexing(scenario_config))

        # Should find goal despite obstacles
        assert len(events) > 0
        assert events[-1].type == "goal_found"

        # Should have explored multiple nodes
        enqueue_events = [e for e in events if e.type == "enqueue"]
        assert len(enqueue_events) > 1

    def test_unreachable_goal_handling(self):
        """Test system behavior with unreachable goal."""
        scenario_config = ScenarioConfig(
            name="unreachable",
            grid_file="grids/test_unreachable.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        adapter_class = AdapterRegistry.get("bfs")
        adapter = adapter_class()
        wrapper = AdapterWrapper(adapter)

        events = list(wrapper.run_with_indexing(scenario_config))

        # Should not find goal
        goal_found_events = [e for e in events if e.type == "goal_found"]
        assert len(goal_found_events) == 0

        # Should still generate events for reachable nodes
        assert len(events) > 0

    def test_event_payload_validation(self):
        """Test that generated events have valid payloads."""
        from agloviz.core.events import validate_event_payload

        scenario_config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(1, 1)
        )

        adapter_class = AdapterRegistry.get("bfs")
        adapter = adapter_class()
        wrapper = AdapterWrapper(adapter)

        events = list(wrapper.run_with_indexing(scenario_config))

        # Validate all event payloads
        for event in events:
            errors = validate_event_payload(event.type, event.payload)
            assert not errors, f"Event {event.step_index} has payload errors: {errors}"
