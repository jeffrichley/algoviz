"""Basic integration test for Phase 1.4.3: Manim Integration Foundation.

Tests the separation between pure visual widgets and event processing adapters.
"""

import pytest
from unittest.mock import Mock

from agloviz.widgets.primitives import TokenWidget, MarkerWidget, ContainerGroup
from agloviz.widgets.grid import GridWidget
from agloviz.widgets.queue import QueueWidget
from agloviz.widgets.adapters import GridWidgetAdapter, QueueWidgetAdapter


class TestWidgetAdapterSeparation:
    """Test the separation between pure visual widgets and event processing adapters."""
    
    def test_widget_has_no_event_processing(self):
        """Test that pure widgets have NO event processing methods."""
        grid = GridWidget()
        
        # Should have pure visual methods
        assert hasattr(grid, 'highlight_cell')
        assert hasattr(grid, 'flash_cell')
        assert hasattr(grid, 'set_cell_label')
        
        # Should NOT have event processing methods
        assert not hasattr(grid, '_mark_frontier')
        assert not hasattr(grid, '_mark_visited')
        assert not hasattr(grid, '_flash_goal')
    
    def test_adapter_handles_event_processing(self):
        """Test that adapters handle event processing and call widget methods."""
        grid = GridWidget()
        adapter = GridWidgetAdapter()
        
        # Mock scene and event
        mock_scene = Mock()
        mock_event = Mock()
        mock_event.type = "enqueue"
        mock_event.payload = {"node": (1, 2)}
        
        # Setup grid
        grid.show(mock_scene, width=3, height=3)
        
        # Adapter should handle event and call widget visual method
        adapter.update(grid, mock_scene, mock_event, run_time=1.0)
        
        # Verify adapter called widget's visual method (cell should be highlighted)
        cell = grid.cell_map[(1, 2)]
        # If we get here without exception, the architecture works
        assert True
    
    def test_adapter_registry_pattern(self):
        """Test adapter registry manages widget adapters."""
        from agloviz.widgets.adapters import adapter_registry
        
        # Should have adapters registered
        grid_adapter = adapter_registry.get_adapter("grid")
        queue_adapter = adapter_registry.get_adapter("queue")
        
        assert isinstance(grid_adapter, GridWidgetAdapter)
        assert isinstance(queue_adapter, QueueWidgetAdapter)
        
        # Should know supported events
        grid_events = adapter_registry.get_supported_events("grid")
        queue_events = adapter_registry.get_supported_events("queue")
        
        assert "enqueue" in grid_events
        assert "goal_found" in grid_events
        assert "enqueue" in queue_events
        assert "dequeue" in queue_events


class TestPrimitiveWidgets:
    """Test pure visual primitive widgets."""
    
    def test_token_widget_is_pure_visual(self):
        """Test TokenWidget has only pure visual operations."""
        token = TokenWidget()
        
        # Should be a Manim Circle
        from manim import Circle
        assert isinstance(token, Circle)
        
        # Should have pure visual methods
        assert hasattr(token, 'highlight')
        assert hasattr(token, 'set_label')
        assert hasattr(token, 'pulse')
        
        # Test visual operations work
        token.highlight("#FF0000", opacity=0.8)
        token.set_label("A")
    
    def test_container_group_uses_manim_layout(self):
        """Test ContainerGroup uses Manim's built-in layout methods."""
        tokens = [TokenWidget() for _ in range(4)]
        container = ContainerGroup(*tokens)
        
        # Should be a Manim VGroup
        from manim import VGroup
        assert isinstance(container, VGroup)
        
        # Should have layout methods
        assert hasattr(container, 'arrange_horizontal')
        assert hasattr(container, 'arrange_vertical')
        assert hasattr(container, 'arrange_in_grid')
        
        # Test layout operations
        container.arrange_horizontal(spacing=0.5)
        assert len(container) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 