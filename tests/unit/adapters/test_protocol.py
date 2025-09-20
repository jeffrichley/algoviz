"""Tests for adapter protocol and wrapper."""

import pytest

from agloviz.adapters.protocol import AdapterWrapper
from agloviz.config.models import ScenarioConfig
from agloviz.core.events import VizEvent


class MockAdapter:
    """Mock adapter for testing."""
    name = "mock"

    def __init__(self, events: list[VizEvent]):
        self.events = events

    def run(self, scenario: ScenarioConfig):
        """Yield mock events."""
        for event in self.events:
            yield event


@pytest.mark.unit
class TestAlgorithmAdapter:
    """Test AlgorithmAdapter protocol."""

    def test_adapter_protocol_compliance(self):
        """Test that mock adapter satisfies protocol."""
        # Create mock events without step_index (as adapters should)
        events = [
            VizEvent(type="enqueue", payload={"node": (0, 0)}, step_index=999),  # Will be overridden
            VizEvent(type="dequeue", payload={"node": (0, 0)}, step_index=999),  # Will be overridden
        ]

        adapter = MockAdapter(events)

        # Should have required attributes
        assert hasattr(adapter, 'name')
        assert hasattr(adapter, 'run')
        assert adapter.name == "mock"

        # Should be callable
        scenario = ScenarioConfig(
            name="test",
            grid_file="test.yaml",
            start=(0, 0),
            goal=(1, 1)
        )

        result = list(adapter.run(scenario))
        assert len(result) == 2


@pytest.mark.unit
class TestAdapterWrapper:
    """Test AdapterWrapper step indexing."""

    def test_wrapper_assigns_step_indices(self):
        """Test that wrapper assigns sequential step indices."""
        # Create events with dummy step_index (should be overridden)
        events = [
            VizEvent(type="enqueue", payload={"node": (0, 0)}, step_index=999),
            VizEvent(type="dequeue", payload={"node": (0, 0)}, step_index=888),
            VizEvent(type="goal_found", payload={"node": (1, 1)}, step_index=777),
        ]

        adapter = MockAdapter(events)
        wrapper = AdapterWrapper(adapter)

        scenario = ScenarioConfig(
            name="test",
            grid_file="test.yaml",
            start=(0, 0),
            goal=(1, 1)
        )

        result = list(wrapper.run_with_indexing(scenario))

        # Check that step indices are sequential starting from 0
        assert len(result) == 3
        assert result[0].step_index == 0
        assert result[1].step_index == 1
        assert result[2].step_index == 2

        # Check that other fields are preserved
        assert result[0].type == "enqueue"
        assert result[1].type == "dequeue"
        assert result[2].type == "goal_found"

        assert result[0].payload == {"node": (0, 0)}
        assert result[2].payload == {"node": (1, 1)}

    def test_wrapper_preserves_metadata(self):
        """Test that wrapper preserves event metadata."""
        events = [
            VizEvent(
                type="enqueue",
                payload={"node": (0, 0)},
                step_index=999,  # Will be overridden
                metadata={"complexity": 5}
            )
        ]

        adapter = MockAdapter(events)
        wrapper = AdapterWrapper(adapter)

        scenario = ScenarioConfig(
            name="test",
            grid_file="test.yaml",
            start=(0, 0),
            goal=(1, 1)
        )

        result = list(wrapper.run_with_indexing(scenario))

        assert len(result) == 1
        assert result[0].step_index == 0
        assert result[0].metadata == {"complexity": 5}

    def test_wrapper_handles_empty_stream(self):
        """Test wrapper handles empty event stream."""
        adapter = MockAdapter([])
        wrapper = AdapterWrapper(adapter)

        scenario = ScenarioConfig(
            name="test",
            grid_file="test.yaml",
            start=(0, 0),
            goal=(1, 1)
        )

        result = list(wrapper.run_with_indexing(scenario))
        assert result == []
