"""Unit tests for GridWidget.

Tests grid widget functionality with mock Manim scenes and VizEvent handling
following project testing standards.
"""

import pytest
from unittest.mock import Mock, MagicMock, call, patch

from agloviz.core.events import VizEvent, PayloadKey

# Mock Manim classes to avoid import issues in tests
class MockSquare:
    def __init__(self, side_length=1.0):
        self.side_length = side_length
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
    
    def scale(self, factor):
        return self

class MockVGroup:
    def __init__(self, *items):
        self.items = list(items)

class MockFadeIn:
    def __init__(self, mobject):
        self.mobject = mobject

class MockFadeOut:
    def __init__(self, mobject):
        self.mobject = mobject

class MockSuccession:
    def __init__(self, *animations):
        self.animations = animations

# Patch Manim imports in the grid module
with patch.dict('sys.modules', {
    'manim': Mock(
        Square=MockSquare,
        VGroup=MockVGroup,
        FadeIn=MockFadeIn,
        FadeOut=MockFadeOut,
        Succession=MockSuccession,
        WHITE='white',
        BLACK='black',
        BLUE='blue',
        GRAY='gray',
        GREEN='green'
    )
}):
    from agloviz.widgets.grid import GridWidget


@pytest.mark.unit
class TestGridWidget:
    """Test suite for GridWidget functionality."""
    
    def test_show_creates_grid_structure(self):
        """Test that show() creates proper grid structure."""
        widget = GridWidget()
        mock_scene = Mock()
        
        widget.show(mock_scene, width=3, height=3, run_time=1.0)
        
        # Verify grid dimensions
        assert widget.width == 3
        assert widget.height == 3
        
        # Verify all cells created
        assert len(widget.cell_map) == 9
        
        # Verify cells exist for expected coordinates
        expected_coords = [(0, 0), (1, 1), (2, 2)]
        for coord in expected_coords:
            assert coord in widget.cell_map
        
        # Verify scene.play was called for FadeIn
        mock_scene.play.assert_called_once()
        
        # Verify grid_group was created
        assert widget.grid_group is not None
    
    def test_show_with_default_dimensions(self):
        """Test show() with default grid dimensions."""
        widget = GridWidget()
        mock_scene = Mock()
        
        widget.show(mock_scene)
        
        # Should use default 10x10 grid
        assert widget.width == 10
        assert widget.height == 10
        assert len(widget.cell_map) == 100
    
    def test_update_handles_enqueue_event(self):
        """Test that update() handles enqueue events correctly."""
        widget = GridWidget()
        mock_scene = Mock()
        
        # Setup grid first
        widget.show(mock_scene, width=3, height=3)
        mock_scene.reset_mock()  # Clear setup calls
        
        # Create enqueue event
        event = VizEvent(
            type="enqueue",
            payload={PayloadKey.NODE: (1, 1)},
            step_index=1
        )
        
        widget.update(mock_scene, event, run_time=0.5)
        
        # Verify scene.play was called for animation
        mock_scene.play.assert_called_once()
        
        # Verify the correct cell was accessed
        assert (1, 1) in widget.cell_map
    
    def test_update_handles_dequeue_event(self):
        """Test that update() handles dequeue events correctly."""
        widget = GridWidget()
        mock_scene = Mock()
        
        # Setup grid
        widget.show(mock_scene, width=3, height=3)
        mock_scene.reset_mock()
        
        # Create dequeue event
        event = VizEvent(
            type="dequeue",
            payload={PayloadKey.NODE: (0, 0)},
            step_index=2
        )
        
        widget.update(mock_scene, event, run_time=0.5)
        
        # Verify scene.play was called
        mock_scene.play.assert_called_once()
    
    def test_update_handles_goal_found_event(self):
        """Test that update() handles goal_found events correctly."""
        widget = GridWidget()
        mock_scene = Mock()
        
        # Setup grid
        widget.show(mock_scene, width=3, height=3)
        mock_scene.reset_mock()
        
        # Create goal_found event
        event = VizEvent(
            type="goal_found",
            payload={PayloadKey.NODE: (2, 2)},
            step_index=10
        )
        
        widget.update(mock_scene, event, run_time=1.0)
        
        # Verify scene.play was called for goal flash animation
        mock_scene.play.assert_called_once()
    
    def test_update_ignores_unknown_event_types(self):
        """Test that update() ignores unknown event types."""
        widget = GridWidget()
        mock_scene = Mock()
        
        # Setup grid
        widget.show(mock_scene, width=3, height=3)
        mock_scene.reset_mock()
        
        # Create unknown event
        event = VizEvent(
            type="unknown_event",
            payload={PayloadKey.NODE: (1, 1)},
            step_index=5
        )
        
        widget.update(mock_scene, event, run_time=0.5)
        
        # Should not call scene.play for unknown events
        mock_scene.play.assert_not_called()
    
    def test_update_handles_missing_node_payload(self):
        """Test that update() handles events without node payload gracefully."""
        widget = GridWidget()
        mock_scene = Mock()
        
        # Setup grid
        widget.show(mock_scene, width=3, height=3)
        mock_scene.reset_mock()
        
        # Create event without node payload
        event = VizEvent(
            type="enqueue",
            payload={},  # No node payload
            step_index=1
        )
        
        widget.update(mock_scene, event, run_time=0.5)
        
        # Should not crash, should not call scene.play
        mock_scene.play.assert_not_called()
    
    def test_update_handles_invalid_node_coordinates(self):
        """Test that update() handles invalid node coordinates gracefully."""
        widget = GridWidget()
        mock_scene = Mock()
        
        # Setup 3x3 grid
        widget.show(mock_scene, width=3, height=3)
        mock_scene.reset_mock()
        
        # Create event with out-of-bounds coordinates
        event = VizEvent(
            type="enqueue",
            payload={PayloadKey.NODE: (10, 10)},  # Out of bounds
            step_index=1
        )
        
        widget.update(mock_scene, event, run_time=0.5)
        
        # Should not crash, should not call scene.play
        mock_scene.play.assert_not_called()
    
    def test_hide_cleans_up_state(self):
        """Test that hide() properly cleans up widget state."""
        widget = GridWidget()
        mock_scene = Mock()
        
        # Setup grid
        widget.show(mock_scene, width=5, height=5)
        
        # Verify state is initialized
        assert widget.grid_group is not None
        assert len(widget.cell_map) == 25
        assert widget.width == 5
        assert widget.height == 5
        
        # Hide widget
        widget.hide(mock_scene)
        
        # Verify cleanup
        assert widget.grid_group is None
        assert len(widget.cell_map) == 0
        assert widget.width == 0
        assert widget.height == 0
        
        # Verify FadeOut was called
        mock_scene.play.assert_called()  # Called twice: FadeIn + FadeOut
    
    def test_hide_handles_no_grid_gracefully(self):
        """Test that hide() handles case where no grid exists."""
        widget = GridWidget()
        mock_scene = Mock()
        
        # Call hide without showing first
        widget.hide(mock_scene)
        
        # Should not crash
        assert widget.grid_group is None
        assert len(widget.cell_map) == 0
    
    def test_cell_positioning(self):
        """Test that cells are positioned correctly in the grid."""
        widget = GridWidget()
        mock_scene = Mock()
        
        # Create small grid for easier testing
        widget.show(mock_scene, width=2, height=2)
        
        # Verify all expected cells exist
        expected_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for pos in expected_positions:
            assert pos in widget.cell_map
        
        # Cells should have different positions
        cell_positions = [widget.cell_map[pos].get_center() for pos in expected_positions]
        
        # All positions should be unique (no overlapping cells)
        assert len(set(tuple(pos) for pos in cell_positions)) == len(cell_positions)
    
    def test_widget_protocol_compliance(self):
        """Test that GridWidget implements the Widget protocol."""
        widget = GridWidget()
        
        # Verify protocol methods exist
        assert hasattr(widget, 'show')
        assert hasattr(widget, 'update')
        assert hasattr(widget, 'hide')
        assert callable(widget.show)
        assert callable(widget.update)
        assert callable(widget.hide)
