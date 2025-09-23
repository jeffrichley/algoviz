"""Integration tests for Director v2.0 with complete system."""

import pytest
from hydra_zen import instantiate

from agloviz.config.hydra_zen import BFSAdvancedSceneConfig, BFSBasicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.director import Director
from agloviz.core.storyboard import Act, Beat, Shot, Storyboard


class TestCompleteStoryboardExecution:
    """Test complete storyboard execution with hydra-zen integration."""

    def test_complete_storyboard_execution(self) -> None:
        """Test complete storyboard execution with hydra-zen integration."""
        # Create real configuration
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create test storyboard
        storyboard = Storyboard(
            acts=[
                Act(
                    title="introduction",
                    shots=[
                        Shot(
                            beats=[
                                Beat(
                                    action="show_title",
                                    args={"text": "BFS Algorithm"},
                                    narration="Welcome to BFS",
                                )
                            ]
                        )
                    ],
                )
            ]
        )

        # Create Director with hydra-zen
        director = Director(storyboard, timing_config, scene_config)

        # Execute storyboard
        director.run()

        # Verify execution completed
        assert len(director.timing_tracker.records) > 0

    def test_hydra_zen_instantiation(self) -> None:
        """Test Director instantiation through hydra-zen."""
        # Create configurations using hydra-zen
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create storyboard
        storyboard = Storyboard(
            acts=[
                Act(
                    title="test_act",
                    shots=[
                        Shot(
                            name="test_shot",
                            beats=[Beat(action="show_title", args={"text": "Test"})],
                        )
                    ],
                )
            ]
        )

        # Instantiate Director
        director = Director(storyboard, timing_config, scene_config)

        # Verify Director was created successfully
        assert director is not None
        assert director.scene_engine is not None
        assert director.storyboard is not None
        assert director.timing is not None

    def test_multi_algorithm_support(self) -> None:
        """Test Director works with different scene configurations."""
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create test storyboard
        storyboard = Storyboard(
            acts=[
                Act(
                    title="test_act",
                    shots=[
                        Shot(
                            name="test_shot",
                            beats=[Beat(action="show_title", args={"text": "Test"})],
                        )
                    ],
                )
            ]
        )

        # Test with BFS Basic
        bfs_basic_config = instantiate(BFSBasicSceneConfig)
        bfs_director = Director(storyboard, timing_config, bfs_basic_config)
        bfs_director.run()

        # Test with BFS Advanced
        bfs_advanced_config = instantiate(BFSAdvancedSceneConfig)
        bfs_advanced_director = Director(storyboard, timing_config, bfs_advanced_config)
        bfs_advanced_director.run()

        # Verify both executed successfully
        assert len(bfs_director.timing_tracker.records) > 0
        assert len(bfs_advanced_director.timing_tracker.records) > 0


class TestSceneConfigurationIntegration:
    """Test scene configuration integration."""

    def test_bfs_scene_configuration(self) -> None:
        """Test BFS-specific scene configuration."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create storyboard with BFS-specific actions
        storyboard = Storyboard(
            acts=[
                Act(
                    title="bfs_demo",
                    shots=[
                        Shot(
                            name="grid_setup",
                            beats=[
                                Beat(
                                    action="show_title",
                                    args={"text": "BFS Pathfinding"},
                                ),
                                Beat(
                                    action="show_widgets",
                                    args={"widgets": ["grid", "queue"]},
                                ),
                            ],
                        )
                    ],
                )
            ]
        )

        director = Director(storyboard, timing_config, scene_config)
        director.run()

        # Verify execution completed
        assert len(director.timing_tracker.records) > 0

    def test_dynamic_parameter_resolution(self) -> None:
        """Test dynamic parameter resolution through OmegaConf."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create storyboard with parameterized actions
        storyboard = Storyboard(
            acts=[
                Act(
                    title="parameterized_demo",
                    shots=[
                        Shot(
                            name="dynamic_shot",
                            beats=[
                                Beat(
                                    action="show_title",
                                    args={"text": "Dynamic: ${scene.name}"},
                                )
                            ],
                        )
                    ],
                )
            ]
        )

        director = Director(storyboard, timing_config, scene_config)

        # Test that Director can handle parameterized actions
        # (Actual parameter resolution happens in SceneEngine)
        director.run()

        # Verify execution completed
        assert len(director.timing_tracker.records) > 0


class TestErrorHandlingIntegration:
    """Test error handling across components."""

    def test_invalid_scene_configuration(self) -> None:
        """Test handling of invalid scene configuration."""
        # Create invalid scene config (None)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        storyboard = Storyboard(acts=[])

        # This should raise an error during SceneEngine initialization
        with pytest.raises((TypeError, AttributeError)):
            Director(storyboard, timing_config, None)

    def test_missing_action_handlers(self) -> None:
        """Test handling of missing action handlers."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create storyboard with unknown action
        storyboard = Storyboard(
            acts=[
                Act(
                    title="error_act",
                    shots=[
                        Shot(
                            name="error_shot",
                            beats=[
                                Beat(action="unknown_action", args={"param": "value"})
                            ],
                        )
                    ],
                )
            ]
        )

        director = Director(storyboard, timing_config, scene_config)

        # Test that Director handles unknown actions gracefully
        # (SceneEngine should handle the error)
        with pytest.raises(ValueError, match="Unknown action"):
            director.run()

    def test_timing_configuration_errors(self) -> None:
        """Test timing configuration error handling."""
        scene_config = instantiate(BFSBasicSceneConfig)

        # Create storyboard
        storyboard = Storyboard(
            acts=[
                Act(
                    title="test_act",
                    shots=[
                        Shot(
                            name="test_shot",
                            beats=[Beat(action="show_title", args={"text": "Test"})],
                        )
                    ],
                )
            ]
        )

        # Test with invalid timing config - Director should handle None gracefully
        # This test verifies that Director doesn't crash with None timing
        director = Director(storyboard, None, scene_config)
        # Director should still be created (though timing might not work properly)
        assert director is not None
