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

    def test_grid_widget_has_pure_visual_methods(self):
        """Test GridWidget has pure visual methods."""
        grid = GridWidget()
        assert hasattr(grid, "highlight_cell")
        assert hasattr(grid, "flash_cell")
        assert hasattr(grid, "set_cell_label")
        assert hasattr(grid, "get_cell_positions")

    def test_grid_widget_lacks_event_processing_methods(self):
        """Test GridWidget lacks event processing methods."""
        grid = GridWidget()
        assert not hasattr(grid, "update")
        assert not hasattr(grid, "_mark_frontier")
        assert not hasattr(grid, "_mark_visited")
        assert not hasattr(grid, "_flash_goal")

    def test_queue_widget_has_pure_visual_methods(self):
        """Test QueueWidget has pure visual methods."""
        queue = QueueWidget()
        assert hasattr(queue, "add_element")
        assert hasattr(queue, "remove_element")

    def test_queue_widget_lacks_event_processing_methods(self):
        """Test QueueWidget lacks event processing methods."""
        queue = QueueWidget()
        assert not hasattr(queue, "update")
        assert not hasattr(queue, "_highlight_enqueue")
        assert not hasattr(queue, "_highlight_dequeue")

    def test_grid_widget_architecture_principles(self):
        """Test GridWidget follows architecture principles."""
        grid = GridWidget()
        assert hasattr(grid, "highlight_cell")
        assert hasattr(grid, "flash_cell")
        assert not hasattr(grid, "update")


class TestWidgetAdapters:
    """Test widget adapters handle event processing."""

    def test_grid_adapter_handles_events(self):
        """Test GridWidgetAdapter processes events correctly."""
        adapter = GridWidgetAdapter()
        events = adapter.get_supported_events()
        assert "enqueue" in events
        assert "dequeue" in events
        assert "goal_found" in events

    def test_queue_adapter_handles_events(self):
        """Test QueueWidgetAdapter processes events correctly."""
        adapter = QueueWidgetAdapter()
        events = adapter.get_supported_events()
        assert "enqueue" in events
        assert "dequeue" in events

    def test_adapter_architecture_principles(self):
        """Test adapter follows architecture principles."""
        adapter = GridWidgetAdapter()
        events = adapter.get_supported_events()
        assert "enqueue" in events
        assert "goal_found" in events
        assert hasattr(adapter, "update")
        assert callable(adapter.update)


class TestAdapterRegistry:
    """Test widget adapter registry."""

    def test_adapter_registry_has_default_adapters(self):
        """Test adapter registry has default adapters registered."""
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
        assert hasattr(widget, "show")
        assert hasattr(widget, "hide")
        assert callable(widget.show)
        assert callable(widget.hide)
        assert not hasattr(widget, "update")

    def test_queue_widget_protocol_compliance(self):
        """Test QueueWidget implements pure visual Widget protocol."""
        widget = QueueWidget()
        assert hasattr(widget, "show")
        assert hasattr(widget, "hide")
        assert callable(widget.show)
        assert callable(widget.hide)
        assert not hasattr(widget, "update")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
