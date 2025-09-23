"""Tests for adapter protocol and wrapper."""

import pytest

from agloviz.adapters.protocol import AdapterWrapper


@pytest.mark.unit
class TestAlgorithmAdapter:
    """Test AlgorithmAdapter protocol."""

    def test_adapter_protocol_compliance(
        self, mock_adapter_basic, small_scenario_config
    ):
        """Test that mock adapter satisfies protocol."""
        # Should have required attributes
        assert hasattr(mock_adapter_basic, "name")
        assert hasattr(mock_adapter_basic, "run")
        assert mock_adapter_basic.name == "mock"

        # Should be callable
        result = list(mock_adapter_basic.run(small_scenario_config))
        assert len(result) == 3


@pytest.mark.unit
class TestAdapterWrapper:
    """Test AdapterWrapper step indexing."""

    def test_wrapper_assigns_step_indices(
        self, mock_wrapper_basic, small_scenario_config
    ):
        """Test that wrapper assigns sequential step indices."""
        result = list(mock_wrapper_basic.run_with_indexing(small_scenario_config))

        self._verify_step_indices(result)
        self._verify_event_types(result)
        self._verify_event_payloads(result)

    def _verify_step_indices(self, result):
        """Verify step indices are sequential."""
        assert len(result) == 3
        assert result[0].step_index == 0
        assert result[1].step_index == 1
        assert result[2].step_index == 2

    def _verify_event_types(self, result):
        """Verify event types are preserved."""
        assert result[0].type == "enqueue"
        assert result[1].type == "dequeue"
        assert result[2].type == "goal_found"

    def _verify_event_payloads(self, result):
        """Verify event payloads are preserved."""
        assert result[0].payload == {"node": (0, 0)}
        assert result[2].payload == {"node": (1, 1)}

    def test_wrapper_preserves_metadata(
        self, mock_wrapper_with_metadata, small_scenario_config
    ):
        """Test that wrapper preserves event metadata."""
        result = list(
            mock_wrapper_with_metadata.run_with_indexing(small_scenario_config)
        )

        assert len(result) == 1
        assert result[0].step_index == 0
        assert result[0].metadata == {"complexity": 5}

    def test_wrapper_handles_empty_stream(self, small_scenario_config):
        """Test wrapper handles empty event stream."""
        adapter = self._create_empty_mock_adapter()
        wrapper = AdapterWrapper(adapter)
        result = list(wrapper.run_with_indexing(small_scenario_config))
        assert result == []

    def _create_empty_mock_adapter(self):
        """Create mock adapter with empty event stream."""
        from agloviz.core.events import VizEvent

        class MockAdapter:
            """Mock adapter for testing."""

            name = "mock"

            def __init__(self, events: list[VizEvent]):
                self.events = events

            def run(self, scenario):
                """Yield mock events."""
                yield from self.events

        return MockAdapter([])
