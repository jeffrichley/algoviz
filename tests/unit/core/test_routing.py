"""Tests for event routing system."""

import pytest

from agloviz.core.routing import (
    RoutingRegistry,
    validate_event_coverage,
    validate_routing_map,
)


@pytest.mark.unit
class TestRoutingMap:
    """Test RoutingMap type alias and generic routing structures."""

    def test_generic_routing_structure(self):
        """Test that generic routing maps have expected structure."""
        # Test with a sample routing map (v2.0 style)
        sample_routing = {
            "enqueue": ["queue.add_element", "grid.highlight_element"],
            "dequeue": ["queue.remove_element"],
            "goal_found": ["grid.highlight_element"],
        }

        assert isinstance(sample_routing, dict)

        # Check handler format
        for _event_type, handlers in sample_routing.items():
            assert isinstance(handlers, list)
            for handler in handlers:
                assert isinstance(handler, str)
                assert "." in handler  # Should be widget.action format

    def test_v2_routing_handlers(self):
        """Test v2.0 compliant routing handlers."""
        # Test with generic widget methods (v2.0 style)
        sample_routing = {
            "enqueue": ["queue.add_element", "grid.highlight_element"],
            "dequeue": ["queue.remove_element"],
            "goal_found": ["grid.highlight_element"],
        }

        # Test enqueue handlers - should use generic methods
        assert "queue.add_element" in sample_routing["enqueue"]
        assert "grid.highlight_element" in sample_routing["enqueue"]

        # Test dequeue handlers - should use generic methods
        assert "queue.remove_element" in sample_routing["dequeue"]

        # Test goal_found handlers - should use generic methods
        assert "grid.highlight_element" in sample_routing["goal_found"]


@pytest.mark.unit
class TestRoutingRegistry:
    """Test RoutingRegistry functionality."""

    def setup_method(self):
        """Clear registry before each test."""
        RoutingRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        RoutingRegistry.clear()

    def test_register_routing_map(self):
        """Test registering a routing map."""
        routing_map = {"test_event": ["widget.action"]}
        RoutingRegistry.register("test_algo", routing_map)

        algorithms = RoutingRegistry.list_algorithms()
        assert "test_algo" in algorithms

    def test_get_routing_map(self):
        """Test getting registered routing map."""
        routing_map = {"test_event": ["widget.action"]}
        RoutingRegistry.register("test_algo", routing_map)

        retrieved = RoutingRegistry.get("test_algo")
        assert retrieved == routing_map

    def test_get_nonexistent_routing_map(self):
        """Test getting non-existent routing map raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            RoutingRegistry.get("nonexistent")

        assert "No routing map" in str(exc_info.value)

    def test_duplicate_registration(self):
        """Test that duplicate registration raises ValueError."""
        routing_map = {"test_event": ["widget.action"]}
        RoutingRegistry.register("test_algo", routing_map)

        with pytest.raises(ValueError) as exc_info:
            RoutingRegistry.register("test_algo", routing_map)

        assert "already registered" in str(exc_info.value)

    def test_list_algorithms_sorted(self):
        """Test that list_algorithms returns sorted results."""
        RoutingRegistry.register("zebra", {"event": ["handler"]})
        RoutingRegistry.register("alpha", {"event": ["handler"]})

        algorithms = RoutingRegistry.list_algorithms()
        assert algorithms == ["alpha", "zebra"]

    def test_list_algorithms_empty(self):
        """Test list_algorithms with empty registry."""
        algorithms = RoutingRegistry.list_algorithms()
        assert algorithms == []

    def test_registry_starts_empty(self):
        """Test that registry starts empty (v2.0 - no auto-registration)."""
        # In v2.0 architecture, no algorithms are auto-registered
        # Scene configurations handle routing dynamically
        algorithms = RoutingRegistry.list_algorithms()
        assert algorithms == []


@pytest.mark.unit
class TestValidateRoutingMap:
    """Test routing map validation."""

    def test_valid_routing_map(self):
        """Test validation passes for valid routing map."""
        routing_map = {
            "enqueue": ["queue.highlight", "grid.mark"],
            "dequeue": ["queue.unhighlight"],
        }

        errors = validate_routing_map(routing_map)
        assert errors == []

    def test_invalid_event_type(self):
        """Test validation fails for non-string event type."""
        routing_map = {
            123: ["handler.action"]  # Invalid event type
        }

        errors = validate_routing_map(routing_map)
        assert len(errors) > 0
        assert "Event type must be string" in errors[0]

    def test_invalid_handlers_type(self):
        """Test validation fails for non-list handlers."""
        routing_map = {
            "event": "handler.action"  # Should be list
        }

        errors = validate_routing_map(routing_map)
        assert len(errors) > 0
        assert "must be list" in errors[0]

    def test_invalid_handler_name(self):
        """Test validation fails for non-string handler."""
        routing_map = {
            "event": [123]  # Invalid handler name
        }

        errors = validate_routing_map(routing_map)
        assert len(errors) > 0
        assert "Handler name must be string" in errors[0]

    def test_invalid_handler_format(self):
        """Test validation fails for invalid handler format."""
        routing_map = {
            "event": ["invalid_handler"]  # Missing dot
        }

        errors = validate_routing_map(routing_map)
        assert len(errors) > 0
        assert "must be in format 'widget.action'" in errors[0]

    def test_handler_too_many_dots(self):
        """Test validation fails for handler with too many dots."""
        routing_map = {
            "event": ["widget.sub.action"]  # Too many dots
        }

        errors = validate_routing_map(routing_map)
        assert len(errors) > 0
        assert "must have exactly one dot" in errors[0]

    def test_empty_widget_or_action(self):
        """Test validation fails for empty widget or action name."""
        routing_map = {
            "event1": [".action"],  # Empty widget
            "event2": ["widget."],  # Empty action
        }

        errors = validate_routing_map(routing_map)
        assert len(errors) >= 2
        assert any("empty widget or action" in error for error in errors)

    def test_multiple_errors(self):
        """Test validation returns multiple errors."""
        routing_map = {
            123: "invalid",  # Non-string event type, non-list handlers
            "event": [456],  # Non-string handler
        }

        errors = validate_routing_map(routing_map)
        assert len(errors) >= 2


@pytest.mark.unit
class TestValidateEventCoverage:
    """Test event coverage validation."""

    def test_full_coverage(self):
        """Test validation passes when all events are covered."""
        routing_map = {
            "enqueue": ["handler1"],
            "dequeue": ["handler2"],
            "goal_found": ["handler3"],
        }
        event_types = {"enqueue", "dequeue", "goal_found"}

        uncovered = validate_event_coverage(routing_map, event_types)
        assert uncovered == []

    def test_missing_event_type(self):
        """Test validation fails when event type is missing."""
        routing_map = {
            "enqueue": ["handler1"],
            "dequeue": ["handler2"],
            # Missing goal_found
        }
        event_types = {"enqueue", "dequeue", "goal_found"}

        uncovered = validate_event_coverage(routing_map, event_types)
        assert "goal_found" in uncovered

    def test_empty_handlers(self):
        """Test validation fails when event has empty handlers."""
        routing_map = {
            "enqueue": ["handler1"],
            "dequeue": [],  # Empty handlers
            "goal_found": ["handler3"],
        }
        event_types = {"enqueue", "dequeue", "goal_found"}

        uncovered = validate_event_coverage(routing_map, event_types)
        assert any("dequeue" in item and "empty handlers" in item for item in uncovered)

    def test_extra_event_types_ignored(self):
        """Test that extra event types in routing map are ignored."""
        routing_map = {
            "enqueue": ["handler1"],
            "dequeue": ["handler2"],
            "extra_event": ["handler3"],  # Not in required set
        }
        event_types = {"enqueue", "dequeue"}

        uncovered = validate_event_coverage(routing_map, event_types)
        assert uncovered == []
