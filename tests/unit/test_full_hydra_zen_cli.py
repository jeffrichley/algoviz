"""Tests for full hydra-zen CLI implementation."""

import pytest
from io import StringIO
import sys
from unittest.mock import patch
from hydra_zen import instantiate

from agloviz.cli.render_pure_zen import render_algorithm_video
from agloviz.config.hydra_zen import BFSBasicSceneConfig, BFSAdvancedSceneConfig
from agloviz.config.models import ScenarioConfig, ThemeConfig, TimingConfig, TimingMode
from agloviz.rendering.renderer import SimpleRenderer
from agloviz.rendering.config import RenderConfig, RenderQuality, RenderFormat


class TestFullHydraZenCLI:
    """Test complete hydra-zen CLI functionality."""
    
    def test_render_algorithm_video_with_basic_scene(self):
        """Test render_algorithm_video function with basic scene config."""
        # Create test configurations
        scene_config = instantiate(BFSBasicSceneConfig)
        scenario_config = ScenarioConfig(name="test", start=(0, 0), goal=(2, 2), grid_size=(3, 3))
        theme_config = ThemeConfig(name="test_theme")
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        render_config = RenderConfig(quality=RenderQuality.MEDIUM, resolution=[1280, 720], frame_rate=30, format=RenderFormat.MP4)
        renderer = SimpleRenderer(render_config)
        
        # Mock the renderer to avoid actual video generation
        with patch.object(renderer, 'render_algorithm_video') as mock_render:
            mock_render.return_value = {"duration": 5.0, "resolution": [1280, 720]}
            
            # Test the function directly
            result = render_algorithm_video(
                algorithm="bfs",
                renderer=renderer,
                scenario=scenario_config,
                theme=theme_config,
                timing=timing_config,
                scene=scene_config,
                output_path="test_output.mp4"
            )
            
            # Verify the function was called correctly
            mock_render.assert_called_once_with(
                algorithm="bfs",
                scenario_config=scenario_config,
                scene_config=scene_config,
                theme_config=theme_config,
                timing_config=timing_config,
                output_path="test_output.mp4"
            )
            
            # Verify result
            assert result["duration"] == 5.0
            assert result["resolution"] == [1280, 720]
    
    def test_render_algorithm_video_with_advanced_scene(self):
        """Test render_algorithm_video function with advanced scene config."""
        # Create test configurations
        scene_config = instantiate(BFSAdvancedSceneConfig)
        scenario_config = ScenarioConfig(name="test", start=(0, 0), goal=(2, 2), grid_size=(3, 3))
        theme_config = ThemeConfig(name="test_theme")
        timing_config = TimingConfig(mode=TimingMode.FAST)
        render_config = RenderConfig(quality=RenderQuality.MEDIUM, resolution=[1280, 720], frame_rate=30, format=RenderFormat.MP4)
        renderer = SimpleRenderer(render_config)
        
        # Mock the renderer to avoid actual video generation
        with patch.object(renderer, 'render_algorithm_video') as mock_render:
            mock_render.return_value = {"duration": 3.0, "resolution": [1280, 720]}
            
            # Test the function directly
            result = render_algorithm_video(
                algorithm="bfs",
                renderer=renderer,
                scenario=scenario_config,
                theme=theme_config,
                timing=timing_config,
                scene=scene_config,
                output_path="test_advanced_output.mp4"
            )
            
            # Verify the function was called correctly
            mock_render.assert_called_once_with(
                algorithm="bfs",
                scenario_config=scenario_config,
                scene_config=scene_config,
                theme_config=theme_config,
                timing_config=timing_config,
                output_path="test_advanced_output.mp4"
            )
            
            # Verify result
            assert result["duration"] == 3.0
            assert result["resolution"] == [1280, 720]
    
    def test_scene_config_instantiation_basic(self):
        """Test that basic scene config can be instantiated correctly."""
        scene_config = instantiate(BFSBasicSceneConfig)
        
        assert scene_config.name == "bfs_basic"
        assert scene_config.algorithm == "bfs"
        assert "grid" in scene_config.widgets
        assert "queue" in scene_config.widgets
        assert len(scene_config.widgets) == 2
        assert "enqueue" in scene_config.event_bindings
        assert "dequeue" in scene_config.event_bindings
    
    def test_scene_config_instantiation_advanced(self):
        """Test that advanced scene config can be instantiated correctly."""
        scene_config = instantiate(BFSAdvancedSceneConfig)
        
        assert scene_config.name == "bfs_advanced"
        assert scene_config.algorithm == "bfs"
        assert "grid" in scene_config.widgets
        assert "queue" in scene_config.widgets
        assert len(scene_config.widgets) == 2
        assert "enqueue" in scene_config.event_bindings
        assert "dequeue" in scene_config.event_bindings
    
    def test_scene_config_widget_targets(self):
        """Test that scene configs have proper widget targets."""
        basic_scene = instantiate(BFSBasicSceneConfig)
        advanced_scene = instantiate(BFSAdvancedSceneConfig)
        
        # Both should have proper widget targets
        for scene in [basic_scene, advanced_scene]:
            grid_widget = scene.widgets["grid"]
            queue_widget = scene.widgets["queue"]
            
            assert hasattr(grid_widget, '__class__')
            assert grid_widget.__class__.__name__ == "GridWidget"
            assert hasattr(queue_widget, '__class__')
            assert queue_widget.__class__.__name__ == "QueueWidget"
    
    def test_scene_config_event_bindings_structure(self):
        """Test that scene configs have proper event bindings structure."""
        basic_scene = instantiate(BFSBasicSceneConfig)
        advanced_scene = instantiate(BFSAdvancedSceneConfig)
        
        # Both should have same event binding structure
        for scene in [basic_scene, advanced_scene]:
            assert "enqueue" in scene.event_bindings
            assert "dequeue" in scene.event_bindings
            
            # Check enqueue bindings
            enqueue_bindings = scene.event_bindings["enqueue"]
            assert len(enqueue_bindings) == 2
            
            # First binding should be queue add_element
            queue_binding = enqueue_bindings[0]
            assert queue_binding["widget"] == "queue"
            assert queue_binding["action"] == "add_element"
            assert queue_binding["order"] == 1
            
            # Second binding should be grid highlight_cell
            grid_binding = enqueue_bindings[1]
            assert grid_binding["widget"] == "grid"
            assert grid_binding["action"] == "highlight_cell"
            assert grid_binding["params"]["color"] == "blue"
            assert grid_binding["order"] == 2
    
    def test_scene_config_algorithm_consistency(self):
        """Test that scene configs have consistent algorithm settings."""
        basic_scene = instantiate(BFSBasicSceneConfig)
        advanced_scene = instantiate(BFSAdvancedSceneConfig)
        
        # Both should have same algorithm
        assert basic_scene.algorithm == advanced_scene.algorithm
        assert basic_scene.algorithm == "bfs"
    
    def test_scene_config_different_names(self):
        """Test that scene configs have different names."""
        basic_scene = instantiate(BFSBasicSceneConfig)
        advanced_scene = instantiate(BFSAdvancedSceneConfig)
        
        assert basic_scene.name != advanced_scene.name
        assert basic_scene.name == "bfs_basic"
        assert advanced_scene.name == "bfs_advanced"
    
    def test_render_algorithm_video_with_different_timing_modes(self):
        """Test render_algorithm_video with different timing modes."""
        scene_config = instantiate(BFSBasicSceneConfig)
        scenario_config = ScenarioConfig(name="test", start=(0, 0), goal=(2, 2), grid_size=(3, 3))
        theme_config = ThemeConfig(name="test_theme")
        render_config = RenderConfig(quality=RenderQuality.MEDIUM, resolution=[1280, 720], frame_rate=30, format=RenderFormat.MP4)
        renderer = SimpleRenderer(render_config)
        
        # Test different timing modes
        for mode in [TimingMode.DRAFT, TimingMode.NORMAL, TimingMode.FAST]:
            timing_config = TimingConfig(mode=mode)
            
            with patch.object(renderer, 'render_algorithm_video') as mock_render:
                mock_render.return_value = {"duration": 2.0, "resolution": [1280, 720]}
                
                result = render_algorithm_video(
                    algorithm="bfs",
                    renderer=renderer,
                    scenario=scenario_config,
                    theme=theme_config,
                    timing=timing_config,
                    scene=scene_config,
                    output_path=f"test_{mode.value}_output.mp4"
                )
                
                # Verify the function was called correctly
                mock_render.assert_called_once()
                assert result["duration"] == 2.0
    
    def test_render_algorithm_video_with_different_themes(self):
        """Test render_algorithm_video with different theme configurations."""
        scene_config = instantiate(BFSBasicSceneConfig)
        scenario_config = ScenarioConfig(name="test", start=(0, 0), goal=(2, 2), grid_size=(3, 3))
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        render_config = RenderConfig(quality=RenderQuality.MEDIUM, resolution=[1280, 720], frame_rate=30, format=RenderFormat.MP4)
        renderer = SimpleRenderer(render_config)
        
        # Test different themes
        themes = ["default", "dark", "high_contrast"]
        for theme_name in themes:
            theme_config = ThemeConfig(name=theme_name)
            
            with patch.object(renderer, 'render_algorithm_video') as mock_render:
                mock_render.return_value = {"duration": 2.0, "resolution": [1280, 720]}
                
                result = render_algorithm_video(
                    algorithm="bfs",
                    renderer=renderer,
                    scenario=scenario_config,
                    theme=theme_config,
                    timing=timing_config,
                    scene=scene_config,
                    output_path=f"test_{theme_name}_output.mp4"
                )
                
                # Verify the function was called correctly
                mock_render.assert_called_once()
                assert result["duration"] == 2.0
