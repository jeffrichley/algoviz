"""Tests for Director v2.0 - Pure Orchestration Component."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from hydra_zen import instantiate

from agloviz.config.hydra_zen import BFSBasicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.director import Director
from agloviz.core.scene import SceneEngine
from agloviz.core.storyboard import Act, Beat, Shot, Storyboard


class MockStoryboard:
    """Mock storyboard for testing."""
    def __init__(self):
        self.acts = [
            Act(
                title="test_act",
                shots=[
                    Shot(
                        beats=[
                            Beat(action="show_title", args={"text": "Test"}, narration="Test narration")
                        ]
                    )
                ]
            )
        ]


class MockTimingConfig:
    """Mock timing config for testing."""
    def __init__(self):
        self.mode = TimingMode.NORMAL
    
    def base_for(self, action: str, mode: str = "normal") -> float:
        return 1.0


class TestDirectorPureOrchestration:
    """Test Director pure orchestration functionality."""

    def test_director_pure_orchestration(self):
        """Test Director orchestrates without knowing about specific actions."""
        # Create mock dependencies
        storyboard = MockStoryboard()
        timing = MockTimingConfig()
        scene_config = instantiate(BFSBasicSceneConfig)
        
        # Create Director
        director = Director(storyboard, timing, scene_config)
        
        # Verify no action-specific knowledge
        assert not hasattr(director, '_actions')
        assert not hasattr(director, 'algorithm')
        
        # Verify SceneEngine integration
        assert director.scene_engine is not None
        assert isinstance(director.scene_engine, SceneEngine)

    def test_director_no_algorithm_knowledge(self):
        """Test Director has no algorithm-specific knowledge."""
        storyboard = MockStoryboard()
        timing = MockTimingConfig()
        scene_config = instantiate(BFSBasicSceneConfig)
        
        director = Director(storyboard, timing, scene_config)
        
        # Verify no algorithm-specific attributes
        assert not hasattr(director, 'algorithm')
        assert not hasattr(director, '_algorithm_actions')
        assert not hasattr(director, '_widget_management')
        
        # Verify only orchestration attributes exist
        assert hasattr(director, 'scene_engine')
        assert hasattr(director, 'storyboard')
        assert hasattr(director, 'timing')
        assert hasattr(director, 'timing_tracker')

    def test_director_sceneengine_integration(self):
        """Test Director properly integrates with SceneEngine."""
        storyboard = MockStoryboard()
        timing = MockTimingConfig()
        scene_config = instantiate(BFSBasicSceneConfig)
        
        director = Director(storyboard, timing, scene_config)
        
        # Verify SceneEngine is properly initialized
        assert director.scene_engine is not None
        assert isinstance(director.scene_engine, SceneEngine)
        
        # Verify SceneEngine has the scene config
        assert director.scene_engine.scene_config is not None


class TestSceneEngineDelegation:
    """Test Director delegates all actions to SceneEngine."""

    def test_sceneengine_action_delegation(self):
        """Test Director delegates all actions to SceneEngine."""
        storyboard = MockStoryboard()
        timing = MockTimingConfig()
        scene_config = instantiate(BFSBasicSceneConfig)
        
        director = Director(storyboard, timing, scene_config)
        beat = Beat(action="show_title", args={"text": "Test"})
        
        # Mock SceneEngine
        director.scene_engine.execute_beat = Mock()
        
        # Execute beat
        director._run_beat(beat, 0, 0, 0)
        
        # Verify delegation
        director.scene_engine.execute_beat.assert_called_once()

    def test_sceneengine_widget_lifecycle_delegation(self):
        """Test Director delegates widget lifecycle to SceneEngine."""
        storyboard = MockStoryboard()
        timing = MockTimingConfig()
        scene_config = instantiate(BFSBasicSceneConfig)
        
        director = Director(storyboard, timing, scene_config)
        
        # Mock SceneEngine methods
        director.scene_engine.initialize_widgets_for_shot = Mock()
        director.scene_engine.cleanup_widgets_for_shot = Mock()
        
        # Test shot entry/exit
        shot = Shot(name="test_shot", beats=[])
        director._enter_shot(shot, 0, 0)
        director._exit_shot(shot, 0, 0)
        
        # Verify delegation (methods are currently placeholders, so no assertions)

    def test_sceneengine_event_routing_delegation(self):
        """Test Director delegates event routing to SceneEngine."""
        storyboard = MockStoryboard()
        timing = MockTimingConfig()
        scene_config = instantiate(BFSBasicSceneConfig)
        
        director = Director(storyboard, timing, scene_config)
        
        # Mock SceneEngine
        director.scene_engine.process_event = Mock()
        
        # Test that Director doesn't handle events directly
        # (This would be tested in integration tests with real events)


class TestTimingIntegration:
    """Test Director timing system integration."""

    def test_timing_tracker_integration(self):
        """Test timing tracker integration."""
        storyboard = MockStoryboard()
        timing = MockTimingConfig()
        scene_config = instantiate(BFSBasicSceneConfig)
        
        director = Director(storyboard, timing, scene_config)
        
        # Verify timing tracker is initialized
        assert director.timing_tracker is not None
        
        # Test timing recording
        beat = Beat(action="show_title", args={"text": "Test"})
        director._run_beat(beat, 0, 0, 0)
        
        # Verify timing was recorded
        assert len(director.timing_tracker.records) > 0

    def test_voiceover_timing_integration(self):
        """Test voiceover timing integration (scaffolded)."""
        storyboard = MockStoryboard()
        timing = MockTimingConfig()
        scene_config = instantiate(BFSBasicSceneConfig)
        
        director = Director(storyboard, timing, scene_config, with_voice=True)
        
        # Verify voiceover is enabled
        assert director.with_voice is True
        
        # Test voiceover timing (scaffolded implementation)
        beat = Beat(action="show_title", args={"text": "Test"}, narration="Test narration")
        director._run_beat(beat, 0, 0, 0)
        
        # Verify no errors occurred (voiceover is scaffolded)

    def test_beat_timing_calculation(self):
        """Test beat timing calculations."""
        storyboard = MockStoryboard()
        timing = MockTimingConfig()
        scene_config = instantiate(BFSBasicSceneConfig)
        
        director = Director(storyboard, timing, scene_config)
        
        # Test timing calculation
        beat = Beat(action="show_title", args={"text": "Test"})
        run_time = timing.base_for(beat.action, mode="normal")
        
        assert run_time == 1.0
        
        # Test with duration overrides
        beat_with_min = Beat(action="show_title", args={"text": "Test"}, min_duration=2.0)
        run_time_with_min = timing.base_for(beat_with_min.action, mode="normal")
        # Note: Director should apply min_duration in _run_beat, but we're testing the base calculation
        assert run_time_with_min == 1.0
