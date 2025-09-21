"""Unit tests for QueueWidget.

Tests queue widget functionality with mock Manim scenes and VizEvent handling
following project testing standards.
"""

import pytest
from unittest.mock import Mock, MagicMock, call, patch
from collections import deque

from agloviz.core.events import VizEvent, PayloadKey

# Mock Manim classes for QueueWidget testing
class MockRectangle:
    def __init__(self, width=1.0, height=1.0):
        self.width = width
        self.height = height
        self._center = [0, 0, 0]
        self._fill_color = None
        self._fill_opacity = 0
        self._stroke_color = None
        self._stroke_width = 1
        self.animate = Mock()
    
    def set_stroke(self, color, width=1):
        self._stroke_color = color
        self._stroke_width = width
        return self
    
    def set_fill(self, color, opacity=1):
        self._fill_color = color
        self._fill_opacity = opacity
        return self
    
    def move_to(self, position):
        self._center = position
        return self
    
    def get_center(self):
        return self._center
    
    def get_left(self):
        return [self._center[0] - self.width/2, self._center[1], self._center[2]]
    
    def get_right(self):
        return [self._center[0] + self.width/2, self._center[1], self._center[2]]
    
    def next_to(self, other, direction, buff=0.25):
        return self

class MockText:
    def __init__(self, text, font_size=24):
        self.text = text
        self.font_size = font_size
        self._center = [0, 0, 0]
        self.animate = Mock()
    
    def move_to(self, position):
        self._center = position
        return self
    
    def get_center(self):
        return self._center
    
    def to_edge(self, edge):
        return self

class MockVGroup:
    def __init__(self, *items):
        self.items = list(items)
        self._center = [0, 0, 0]
        self.animate = Mock()
    
    def get_center(self):
        return self._center
    
    def move_to(self, position):
        self._center = position
        return self

class MockFadeIn:
    def __init__(self, mobject):
        self.mobject = mobject

class MockFadeOut:
    def __init__(self, mobject, shift=None):
        self.mobject = mobject
        self.shift = shift

class MockSuccession:
    def __init__(self, *animations):
        self.animations = animations

# Patch Manim imports in the queue module
with patch.dict('sys.modules', {
    'manim': Mock(
        Rectangle=MockRectangle,
        Text=MockText,
        VGroup=MockVGroup,
        FadeIn=MockFadeIn,
        FadeOut=MockFadeOut,
        Succession=MockSuccession,
        WHITE='white',
        BLACK='black',
        BLUE='blue',
        YELLOW='yellow',
        LEFT=[1, 0, 0],
        RIGHT=[1, 0, 0],
        UP=[0, 1, 0],
        DOWN=[0, -1, 0]
    )
}):
    from agloviz.widgets.queue import QueueWidget


@pytest.mark.unit
class TestQueueWidget:
    """Test suite for QueueWidget functionality."""
    
    def test_show_creates_queue_structure(self):
        """Test that show() creates proper queue structure."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        widget.show(mock_scene, max_items=5, run_time=1.0)
        
        # Verify queue configuration
        assert widget.max_visible_items == 5
        
        # Verify scene.play was called for FadeIn
        mock_scene.play.assert_called_once()
        
        # Verify queue_group was created
        assert widget.queue_group is not None
        
        # Verify empty queue state
        assert len(widget.queue_items) == 0
        assert len(widget.queue_data) == 0
    
    def test_show_with_default_parameters(self):
        """Test show() with default parameters."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        widget.show(mock_scene)
        
        # Should use default max_items
        assert widget.max_visible_items == 8
    
    def test_update_handles_enqueue_event(self):
        """Test that update() handles enqueue events correctly."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        # Setup queue first
        widget.show(mock_scene, max_items=5)
        mock_scene.reset_mock()
        
        # Create enqueue event
        event = VizEvent(
            type="enqueue",
            payload={PayloadKey.NODE: (2, 3)},
            step_index=1
        )
        
        widget.update(mock_scene, event, run_time=0.5)
        
        # Verify item was added to queue
        assert len(widget.queue_items) == 1
        assert len(widget.queue_data) == 1
        assert widget.queue_data[0] == (2, 3)
        
        # Verify scene operations were called
        mock_scene.add.assert_called_once()
        mock_scene.play.assert_called_once()
    
    def test_update_handles_dequeue_event(self):
        """Test that update() handles dequeue events correctly."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        # Setup queue and add an item first
        widget.show(mock_scene, max_items=5)
        
        # Add item to queue
        enqueue_event = VizEvent(
            type="enqueue",
            payload={PayloadKey.NODE: (1, 1)},
            step_index=1
        )
        widget.update(mock_scene, enqueue_event, run_time=0.5)
        
        # Reset mock to focus on dequeue
        mock_scene.reset_mock()
        
        # Create dequeue event
        dequeue_event = VizEvent(
            type="dequeue",
            payload={PayloadKey.NODE: (1, 1)},
            step_index=2
        )
        
        widget.update(mock_scene, dequeue_event, run_time=0.5)
        
        # Verify item was removed from queue
        assert len(widget.queue_items) == 0
        assert len(widget.queue_data) == 0
        
        # Verify scene.play was called for dequeue animation
        mock_scene.play.assert_called_once()
    
    def test_update_handles_dequeue_from_empty_queue(self):
        """Test that dequeue from empty queue is handled gracefully."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        # Setup empty queue
        widget.show(mock_scene, max_items=5)
        mock_scene.reset_mock()
        
        # Create dequeue event
        event = VizEvent(
            type="dequeue",
            payload={PayloadKey.NODE: (1, 1)},
            step_index=1
        )
        
        widget.update(mock_scene, event, run_time=0.5)
        
        # Should not crash, should not call scene.play
        mock_scene.play.assert_not_called()
        
        # Queue should remain empty
        assert len(widget.queue_items) == 0
        assert len(widget.queue_data) == 0
    
    def test_update_ignores_unknown_event_types(self):
        """Test that update() ignores unknown event types."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        # Setup queue
        widget.show(mock_scene, max_items=5)
        mock_scene.reset_mock()
        
        # Create unknown event
        event = VizEvent(
            type="unknown_event",
            payload={PayloadKey.NODE: (1, 1)},
            step_index=5
        )
        
        widget.update(mock_scene, event, run_time=0.5)
        
        # Should not call scene operations for unknown events
        mock_scene.add.assert_not_called()
        mock_scene.play.assert_not_called()
    
    def test_update_handles_missing_node_payload(self):
        """Test that update() handles events without node payload gracefully."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        # Setup queue
        widget.show(mock_scene, max_items=5)
        mock_scene.reset_mock()
        
        # Create event without node payload
        event = VizEvent(
            type="enqueue",
            payload={},  # No node payload
            step_index=1
        )
        
        widget.update(mock_scene, event, run_time=0.5)
        
        # Should not crash, should not modify queue
        assert len(widget.queue_items) == 0
        assert len(widget.queue_data) == 0
        mock_scene.add.assert_not_called()
        mock_scene.play.assert_not_called()
    
    def test_multiple_enqueue_operations(self):
        """Test multiple enqueue operations maintain correct order."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        # Setup queue
        widget.show(mock_scene, max_items=5)
        
        # Add multiple items
        nodes = [(0, 0), (1, 1), (2, 2)]
        for i, node in enumerate(nodes):
            event = VizEvent(
                type="enqueue",
                payload={PayloadKey.NODE: node},
                step_index=i + 1
            )
            widget.update(mock_scene, event, run_time=0.5)
        
        # Verify queue order
        assert len(widget.queue_items) == 3
        assert len(widget.queue_data) == 3
        assert list(widget.queue_data) == nodes
    
    def test_queue_overflow_handling(self):
        """Test that queue overflow is handled correctly."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        # Setup queue with small max_items
        widget.show(mock_scene, max_items=2)
        
        # Add items beyond capacity
        nodes = [(0, 0), (1, 1), (2, 2), (3, 3)]
        for i, node in enumerate(nodes):
            event = VizEvent(
                type="enqueue",
                payload={PayloadKey.NODE: node},
                step_index=i + 1
            )
            widget.update(mock_scene, event, run_time=0.5)
        
        # Should maintain max_items limit
        assert len(widget.queue_items) <= widget.max_visible_items
        assert len(widget.queue_data) <= widget.max_visible_items
    
    def test_hide_cleans_up_state(self):
        """Test that hide() properly cleans up widget state."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        # Setup queue and add items
        widget.show(mock_scene, max_items=5)
        
        event = VizEvent(
            type="enqueue",
            payload={PayloadKey.NODE: (1, 1)},
            step_index=1
        )
        widget.update(mock_scene, event, run_time=0.5)
        
        # Verify state is initialized
        assert widget.queue_group is not None
        assert len(widget.queue_items) == 1
        assert len(widget.queue_data) == 1
        
        # Hide widget
        widget.hide(mock_scene)
        
        # Verify cleanup
        assert widget.queue_group is None
        assert len(widget.queue_items) == 0
        assert len(widget.queue_data) == 0
    
    def test_hide_handles_no_queue_gracefully(self):
        """Test that hide() handles case where no queue exists."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        # Call hide without showing first
        widget.hide(mock_scene)
        
        # Should not crash
        assert widget.queue_group is None
        assert len(widget.queue_items) == 0
        assert len(widget.queue_data) == 0
    
    def test_get_queue_position_calculation(self):
        """Test that queue position calculation works correctly."""
        widget = QueueWidget()
        mock_scene = Mock()
        
        # Setup queue
        widget.show(mock_scene, max_items=5)
        
        # Test position calculations
        pos0 = widget._get_queue_position(0)
        pos1 = widget._get_queue_position(1)
        
        # Positions should be different
        assert pos0 != pos1
        
        # X positions should increase with index
        assert pos1[0] > pos0[0]
    
    def test_widget_protocol_compliance(self):
        """Test that QueueWidget implements the Widget protocol."""
        widget = QueueWidget()
        
        # Verify protocol methods exist
        assert hasattr(widget, 'show')
        assert hasattr(widget, 'update')
        assert hasattr(widget, 'hide')
        assert callable(widget.show)
        assert callable(widget.update)
        assert callable(widget.hide)
