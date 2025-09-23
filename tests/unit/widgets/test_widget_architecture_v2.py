"""Tests for Widget Architecture v2.0 - Pure Visual Widgets + WidgetAdapters.

Tests the new architecture where widgets are pure visual and adapters handle events.
"""


import pytest

from agloviz.widgets.adapters import (
    GridWidgetAdapter,
    QueueWidgetAdapter,
    adapter_registry,
)
from agloviz.widgets.grid import GridWidget
from agloviz.widgets.queue import QueueWidget


class TestPureVisualWidgets:
    """Test that widgets are pure visual with no event processing."""

    def test_grid_widget_is_pure_visual(self):
        """Test GridWidget has only pure visual methods."""
        grid = GridWidget()

        # Should have pure visual methods
        assert hasattr(grid, 'highlight_cell')
        assert hasattr(grid, 'flash_cell')
        assert hasattr(grid, 'set_cell_label')
        assert hasattr(grid, 'get_cell_positions')

        # Should NOT have event processing methods
        assert not hasattr(grid, 'update')
        assert not hasattr(grid, '_mark_frontier')
        assert not hasattr(grid, '_mark_visited')
        assert not hasattr(grid, '_flash_goal')

    def test_queue_widget_is_pure_visual(self):
        """Test QueueWidget has only pure visual methods."""
        queue = QueueWidget()

        # Should have pure visual methods
        assert hasattr(queue, 'add_element')
        assert hasattr(queue, 'remove_element')

        # Should NOT have event processing methods
        assert not hasattr(queue, 'update')
        assert not hasattr(queue, '_highlight_enqueue')
        assert not hasattr(queue, '_highlight_dequeue')

    def test_grid_widget_architecture_principles(self):
        """Test GridWidget follows architecture principles."""
        grid = GridWidget()

        # Should be pure visual widget
        assert hasattr(grid, 'highlight_cell')
        assert hasattr(grid, 'flash_cell')

        # Should NOT process events directly
        assert not hasattr(grid, 'update')



class TestWidgetAdapters:
    """Test widget adapters handle event processing."""

    def test_grid_adapter_handles_events(self):
        """Test GridWidgetAdapter processes events correctly."""
        adapter = GridWidgetAdapter()

        # Should know supported events
        events = adapter.get_supported_events()
        assert "enqueue" in events
        assert "dequeue" in events
        assert "goal_found" in events

    def test_queue_adapter_handles_events(self):
        """Test QueueWidgetAdapter processes events correctly."""
        adapter = QueueWidgetAdapter()

        # Should know supported events
        events = adapter.get_supported_events()
        assert "enqueue" in events
        assert "dequeue" in events

    def test_adapter_architecture_principles(self):
        """Test adapter follows architecture principles."""
        adapter = GridWidgetAdapter()

        # Should know supported events
        events = adapter.get_supported_events()
        assert "enqueue" in events
        assert "goal_found" in events

        # Should have update method for event processing
        assert hasattr(adapter, 'update')
        assert callable(adapter.update)



class TestAdapterRegistry:
    """Test widget adapter registry."""

    def test_adapter_registry_has_default_adapters(self):
        """Test adapter registry has default adapters registered."""
        # Should have grid and queue adapters
        grid_adapter = adapter_registry.get_adapter("grid")
        queue_adapter = adapter_registry.get_adapter("queue")

        assert isinstance(grid_adapter, GridWidgetAdapter)
        assert isinstance(queue_adapter, QueueWidgetAdapter)

    def test_adapter_registry_reports_supported_events(self):
        """Test adapter registry reports supported events."""
        grid_events = adapter_registry.get_supported_events("grid")
        queue_events = adapter_registry.get_supported_events("queue")

        assert "enqueue" in grid_events
        assert "goal_found" in grid_events
        assert "enqueue" in queue_events
        assert "dequeue" in queue_events


class TestWidgetProtocolCompliance:
    """Test widgets comply with the new pure visual Widget protocol."""

    def test_grid_widget_protocol_compliance(self):
        """Test GridWidget implements pure visual Widget protocol."""
        widget = GridWidget()

        # Should have Widget protocol methods
        assert hasattr(widget, 'show')
        assert hasattr(widget, 'hide')
        assert callable(widget.show)
        assert callable(widget.hide)

        # Should NOT have update method (that's in adapter)
        assert not hasattr(widget, 'update')

    def test_queue_widget_protocol_compliance(self):
        """Test QueueWidget implements pure visual Widget protocol."""
        widget = QueueWidget()

        # Should have Widget protocol methods
        assert hasattr(widget, 'show')
        assert hasattr(widget, 'hide')
        assert callable(widget.show)
        assert callable(widget.hide)

        # Should NOT have update method (that's in adapter)
        assert not hasattr(widget, 'update')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
