"""Integration tests for BFS system."""

import pytest

from agloviz.adapters.registry import AdapterRegistry
from agloviz.config.models import ScenarioConfig
from agloviz.core.routing import RoutingRegistry
from agloviz.core.scenario import ContractTestHarness, ScenarioLoader


@pytest.mark.unit
class TestBFSIntegration:
    """Test complete BFS workflow from config to events."""

    def test_bfs_complete_workflow(
        self, bfs_wrapper_from_registry, simple_scenario_config
    ):
        """Test complete BFS workflow from config to events."""
        # Generate events
        events = list(
            bfs_wrapper_from_registry.run_with_indexing(simple_scenario_config)
        )

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
            name="test", start=(0, 0), goal=(2, 2), grid_size=(3, 3)
        )

        scenario = ScenarioLoader.from_config(config)
        harness = ContractTestHarness()

        violations = harness.verify_scenario(scenario)
        assert not violations, f"Contract violations: {violations}"

    def test_registry_integration(self, registered_bfs_adapter):
        """Test that registries work together."""
        # Check adapter registry
        algorithms = AdapterRegistry.list_algorithms()
        assert "bfs" in algorithms

        # Check routing registry (v2.0 - should be empty, routing handled by scene configs)
        routing_algorithms = RoutingRegistry.list_algorithms()
        assert len(routing_algorithms) == 0  # No hardcoded routing maps in v2.0

        # Routing is now handled dynamically by scene configurations
        # This test validates that the adapter registry still works independently

    def test_deterministic_behavior(
        self, bfs_wrapper_from_registry, small_scenario_config
    ):
        """Test that the system produces deterministic results."""
        # Run twice and compare
        events1 = list(
            bfs_wrapper_from_registry.run_with_indexing(small_scenario_config)
        )
        events2 = list(
            bfs_wrapper_from_registry.run_with_indexing(small_scenario_config)
        )

        assert len(events1) == len(events2)

        for e1, e2 in zip(events1, events2, strict=False):
            assert e1.type == e2.type
            assert e1.payload == e2.payload
            assert e1.step_index == e2.step_index

    def test_complex_scenario(self, bfs_wrapper_from_registry, complex_scenario_config):
        """Test BFS on complex scenario with obstacles."""
        events = list(
            bfs_wrapper_from_registry.run_with_indexing(complex_scenario_config)
        )

        # Should find goal despite obstacles
        assert len(events) > 0
        assert events[-1].type == "goal_found"

        # Should have explored multiple nodes
        enqueue_events = [e for e in events if e.type == "enqueue"]
        assert len(enqueue_events) > 1

    def test_unreachable_goal_handling(
        self, bfs_wrapper_from_registry, unreachable_scenario_config
    ):
        """Test system behavior with unreachable goal."""
        events = list(
            bfs_wrapper_from_registry.run_with_indexing(unreachable_scenario_config)
        )

        # Should not find goal
        goal_found_events = [e for e in events if e.type == "goal_found"]
        assert len(goal_found_events) == 0

        # Should still generate events for reachable nodes
        assert len(events) > 0

    def test_event_payload_validation(
        self, bfs_wrapper_from_registry, small_scenario_config
    ):
        """Test that generated events have valid payloads."""
        from agloviz.core.events import validate_event_payload

        events = list(
            bfs_wrapper_from_registry.run_with_indexing(small_scenario_config)
        )

        # Validate all event payloads
        for event in events:
            errors = validate_event_payload(event.type, event.payload)
            assert not errors, f"Event {event.step_index} has payload errors: {errors}"
