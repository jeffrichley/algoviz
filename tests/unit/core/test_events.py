"""Tests for the VizEvent system."""

import pytest

from agloviz.core.events import PayloadKey, VizEvent, validate_event_payload


@pytest.mark.unit
class TestVizEvent:
    """Test VizEvent model."""

    def test_create_basic_event(self):
        """Test creating a basic VizEvent."""
        event = VizEvent(type="enqueue", payload={"node": (0, 0)}, step_index=0)

        assert event.type == "enqueue"
        assert event.payload == {"node": (0, 0)}
        assert event.step_index == 0
        assert event.metadata == {}

    def test_create_event_with_metadata(self):
        """Test creating VizEvent with metadata."""
        event = VizEvent(
            type="dequeue",
            payload={"node": (1, 1), "parent": (0, 0)},
            step_index=1,
            metadata={"complexity": 5},
        )

        assert event.type == "dequeue"
        assert event.payload == {"node": (1, 1), "parent": (0, 0)}
        assert event.step_index == 1
        assert event.metadata == {"complexity": 5}

    def test_event_immutability_through_validation(self):
        """Test that VizEvent validates properly."""
        # Should work with valid data
        event = VizEvent(type="goal_found", payload={"node": (5, 5)}, step_index=10)
        assert event.type == "goal_found"

    def test_required_fields(self):
        """Test that required fields are enforced."""
        # Missing type should fail
        with pytest.raises(ValueError):
            VizEvent(payload={}, step_index=0)

        # Missing step_index should fail
        with pytest.raises(ValueError):
            VizEvent(type="test", payload={})


@pytest.mark.unit
class TestPayloadKey:
    """Test PayloadKey enum."""

    def test_payload_keys_exist(self):
        """Test that all expected payload keys exist."""
        assert PayloadKey.NODE == "node"
        assert PayloadKey.POS == "pos"
        assert PayloadKey.WEIGHT == "weight"
        assert PayloadKey.PARENT == "parent"

    def test_payload_keys_are_strings(self):
        """Test that payload keys work as strings."""
        payload = {PayloadKey.NODE: (0, 0)}
        assert "node" in payload
        assert payload["node"] == (0, 0)


@pytest.mark.unit
class TestValidateEventPayload:
    """Test payload validation function."""

    def test_valid_node_payload(self):
        """Test validation passes for valid node payload."""
        payload = {"node": (0, 0)}
        errors = validate_event_payload("enqueue", payload)
        assert errors == []

    def test_valid_complex_payload(self):
        """Test validation passes for complex valid payload."""
        payload = {"node": (1, 2), "parent": (0, 1), "weight": 2.5}
        errors = validate_event_payload("enqueue", payload)
        assert errors == []

    def test_invalid_node_format(self):
        """Test validation fails for invalid node format."""
        payload = {"node": "invalid"}
        errors = validate_event_payload("enqueue", payload)
        assert len(errors) > 0
        assert "must be a tuple/list of length 2" in errors[0]

    def test_invalid_node_coordinates(self):
        """Test validation fails for non-integer coordinates."""
        payload = {"node": (1.5, 2.5)}
        errors = validate_event_payload("enqueue", payload)
        assert len(errors) > 0
        assert "coordinates must be integers" in errors[0]

    def test_invalid_parent_format(self):
        """Test validation fails for invalid parent format."""
        payload = {"parent": [1]}  # Too short
        errors = validate_event_payload("enqueue", payload)
        assert len(errors) > 0
        assert "must be a tuple/list of length 2" in errors[0]

    def test_invalid_weight_type(self):
        """Test validation fails for invalid weight type."""
        payload = {"weight": "heavy"}
        errors = validate_event_payload("enqueue", payload)
        assert len(errors) > 0
        assert "must be a number" in errors[0]

    def test_negative_weight(self):
        """Test validation fails for negative weight."""
        payload = {"weight": -1.0}
        errors = validate_event_payload("enqueue", payload)
        assert len(errors) > 0
        assert "must be non-negative" in errors[0]

    def test_multiple_errors(self):
        """Test validation returns multiple errors."""
        payload = {"node": "invalid", "weight": -1.0}
        errors = validate_event_payload("enqueue", payload)
        assert len(errors) == 2
