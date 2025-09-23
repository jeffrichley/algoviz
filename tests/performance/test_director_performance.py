"""Performance tests for Director v2.0."""

import time

from hydra_zen import instantiate

from agloviz.config.hydra_zen import BFSAdvancedSceneConfig, BFSBasicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.director import Director
from agloviz.core.storyboard import Act, Beat, Shot, Storyboard


class TestDirectorPerformance:
    """Test Director performance benchmarks."""

    def create_large_storyboard(
        self, num_acts: int = 5, num_shots: int = 3, num_beats: int = 2
    ) -> Storyboard:
        """Create a large storyboard for performance testing."""
        acts = []
        for i in range(num_acts):
            shots = []
            for j in range(num_shots):
                beats = []
                for k in range(num_beats):
                    beats.append(
                        Beat(
                            action="show_title",
                            args={"text": f"Act {i}, Shot {j}, Beat {k}"},
                            narration=f"Narration for beat {k}",
                        )
                    )
                shots.append(Shot(beats=beats))
            acts.append(Act(title=f"act_{i}", shots=shots))

        return Storyboard(acts=acts)

    def test_storyboard_execution_performance(self):
        """Test storyboard execution performance."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        storyboard = self.create_large_storyboard(num_acts=3, num_shots=2, num_beats=2)

        director = Director(storyboard, timing_config, scene_config)

        # Measure execution time
        start_time = time.time()
        director.run()
        execution_time = time.time() - start_time

        # Performance assertion (should complete within reasonable time)
        assert execution_time < 5.0  # Should complete within 5 seconds

        # Verify timing records were created
        assert len(director.timing_tracker.records) > 0

    def test_widget_instantiation_performance(self):
        """Test widget instantiation performance."""
        scene_config = instantiate(BFSAdvancedSceneConfig)  # More complex config
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        storyboard = self.create_large_storyboard(num_acts=1, num_shots=1, num_beats=1)

        director = Director(storyboard, timing_config, scene_config)

        # Measure SceneEngine initialization time
        start_time = time.time()
        scene_engine = director.scene_engine
        init_time = time.time() - start_time

        # SceneEngine initialization should be fast
        assert init_time < 1.0  # Should initialize within 1 second

        # Verify SceneEngine was created
        assert scene_engine is not None


class TestConfigurationValidation:
    """Test all configuration combinations work."""

    def test_all_timing_modes(self):
        """Test all timing mode combinations."""
        scene_config = instantiate(BFSBasicSceneConfig)

        timing_modes = [TimingMode.NORMAL, TimingMode.FAST]

        for mode in timing_modes:
            timing_config = TimingConfig(mode=mode)
            storyboard = Storyboard(
                acts=[
                    Act(
                        title="test_act",
                        shots=[
                            Shot(
                                beats=[Beat(action="show_title", args={"text": "Test"})]
                            )
                        ],
                    )
                ]
            )

            director = Director(storyboard, timing_config, scene_config)
            director.run()

            # Verify execution completed
            assert len(director.timing_tracker.records) > 0

    def test_all_scene_config_types(self):
        """Test all available scene config types."""
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        storyboard = Storyboard(
            acts=[
                Act(
                    title="test_act",
                    shots=[
                        Shot(beats=[Beat(action="show_title", args={"text": "Test"})])
                    ],
                )
            ]
        )

        # Test BFS Basic
        bfs_basic_config = instantiate(BFSBasicSceneConfig)
        bfs_basic_director = Director(storyboard, timing_config, bfs_basic_config)
        bfs_basic_director.run()

        # Test BFS Advanced
        bfs_advanced_config = instantiate(BFSAdvancedSceneConfig)
        bfs_advanced_director = Director(storyboard, timing_config, bfs_advanced_config)
        bfs_advanced_director.run()

        # Verify both executed successfully
        assert len(bfs_basic_director.timing_tracker.records) > 0
        assert len(bfs_advanced_director.timing_tracker.records) > 0

    def test_configuration_merging(self):
        """Test configuration merging validation."""
        # Test that Director can handle merged configurations
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create storyboard with merged timing settings
        storyboard = Storyboard(
            acts=[
                Act(
                    title="merged_test",
                    shots=[
                        Shot(
                            beats=[
                                Beat(
                                    action="show_title",
                                    args={"text": "Merged Config Test"},
                                    min_duration=0.5,
                                    max_duration=2.0,
                                )
                            ]
                        )
                    ],
                )
            ]
        )

        director = Director(storyboard, timing_config, scene_config)
        director.run()

        # Verify execution completed with merged settings
        assert len(director.timing_tracker.records) > 0

        # Verify timing was applied correctly
        records = director.timing_tracker.records
        assert len(records) > 0
        # Note: Actual timing validation would require more detailed timing analysis
