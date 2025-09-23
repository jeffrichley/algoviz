"""Tests for hydra-zen scene configuration builders."""

from hydra_zen import instantiate

from agloviz.config.hydra_zen import BFSAdvancedSceneConfig, BFSBasicSceneConfig
from agloviz.config.models import SceneConfig


class TestSceneConfigBuilders:
    """Test scene configuration builders."""

    def test_bfs_basic_scene_instantiation(self):
        """Test BFS basic scene config instantiation."""
        scene = instantiate(BFSBasicSceneConfig)
        assert isinstance(scene, SceneConfig)
        assert scene.name == "bfs_basic"
        assert scene.algorithm == "bfs"
        assert "grid" in scene.widgets
        assert "queue" in scene.widgets
        assert len(scene.widgets) == 2  # grid + queue

    def test_bfs_advanced_scene_instantiation(self):
        """Test BFS advanced scene config instantiation."""
        scene = instantiate(BFSAdvancedSceneConfig)
        assert isinstance(scene, SceneConfig)
        assert scene.name == "bfs_advanced"
        assert scene.algorithm == "bfs"
        assert "grid" in scene.widgets
        assert "queue" in scene.widgets
        assert len(scene.widgets) == 2  # grid + queue

    def test_bfs_basic_scene_widget_configuration(self):
        """Test BFS basic scene widget configuration."""
        scene = instantiate(BFSBasicSceneConfig)

        # Check that widgets are instantiated (not config dicts)
        grid_widget = scene.widgets["grid"]
        assert hasattr(grid_widget, '__class__')
        assert grid_widget.__class__.__name__ == "GridWidget"

        # Check queue widget configuration
        queue_widget = scene.widgets["queue"]
        assert hasattr(queue_widget, '__class__')
        assert queue_widget.__class__.__name__ == "QueueWidget"

    def test_bfs_advanced_scene_widget_configuration(self):
        """Test BFS advanced scene widget configuration with custom parameters."""
        scene = instantiate(BFSAdvancedSceneConfig)

        # Check that widgets are instantiated (not config dicts)
        grid_widget = scene.widgets["grid"]
        assert hasattr(grid_widget, '__class__')
        assert grid_widget.__class__.__name__ == "GridWidget"

        # Check queue widget configuration
        queue_widget = scene.widgets["queue"]
        assert hasattr(queue_widget, '__class__')
        assert queue_widget.__class__.__name__ == "QueueWidget"

        # Note: Custom parameters (width, height, max_visible_items) are applied during instantiation
        # but we can't easily test them without knowing the widget's internal state
        # The fact that instantiation succeeds means the parameters were valid

    def test_bfs_basic_scene_event_bindings(self):
        """Test BFS basic scene event bindings."""
        scene = instantiate(BFSBasicSceneConfig)

        # Check that event bindings exist
        assert hasattr(scene, 'event_bindings')
        assert isinstance(scene.event_bindings, dict)

        # Check enqueue event binding
        assert "enqueue" in scene.event_bindings
        enqueue_bindings = scene.event_bindings["enqueue"]
        assert len(enqueue_bindings) == 2  # queue add_element + grid highlight_cell

        # Check first binding (queue add_element)
        queue_binding = enqueue_bindings[0]
        assert queue_binding["widget"] == "queue"
        assert queue_binding["action"] == "add_element"
        assert queue_binding["order"] == 1

        # Check second binding (grid highlight_cell)
        grid_binding = enqueue_bindings[1]
        assert grid_binding["widget"] == "grid"
        assert grid_binding["action"] == "highlight_cell"
        assert grid_binding["params"]["color"] == "blue"
        assert grid_binding["order"] == 2

    def test_bfs_advanced_scene_event_bindings(self):
        """Test BFS advanced scene event bindings."""
        scene = instantiate(BFSAdvancedSceneConfig)

        # Check that event bindings exist
        assert hasattr(scene, 'event_bindings')
        assert isinstance(scene.event_bindings, dict)

        # Check enqueue event binding (should be same as basic)
        assert "enqueue" in scene.event_bindings
        enqueue_bindings = scene.event_bindings["enqueue"]
        assert len(enqueue_bindings) == 2

        # Check first binding (queue add_element)
        queue_binding = enqueue_bindings[0]
        assert queue_binding["widget"] == "queue"
        assert queue_binding["action"] == "add_element"
        assert queue_binding["order"] == 1

        # Check second binding (grid highlight_cell)
        grid_binding = enqueue_bindings[1]
        assert grid_binding["widget"] == "grid"
        assert grid_binding["action"] == "highlight_cell"
        assert grid_binding["params"]["color"] == "blue"
        assert grid_binding["order"] == 2

    def test_all_scene_configs_have_required_fields(self):
        """Test that all scene configs have required fields."""
        configs = [
            BFSBasicSceneConfig, BFSAdvancedSceneConfig
        ]

        for config in configs:
            scene = instantiate(config)
            assert hasattr(scene, 'name')
            assert hasattr(scene, 'algorithm')
            assert hasattr(scene, 'widgets')
            assert hasattr(scene, 'event_bindings')
            assert len(scene.widgets) > 0
            assert scene.algorithm == "bfs"  # All current configs are BFS

    def test_scene_configs_instantiate_without_errors(self):
        """Test that all scene configs can be instantiated without errors."""
        configs = [
            BFSBasicSceneConfig, BFSAdvancedSceneConfig
        ]

        for config in configs:
            # Should not raise any exceptions
            scene = instantiate(config)
            assert scene is not None
            assert isinstance(scene, SceneConfig)

    def test_scene_configs_different_names(self):
        """Test that scene configs have different names."""
        basic_scene = instantiate(BFSBasicSceneConfig)
        advanced_scene = instantiate(BFSAdvancedSceneConfig)

        assert basic_scene.name != advanced_scene.name
        assert basic_scene.name == "bfs_basic"
        assert advanced_scene.name == "bfs_advanced"

    def test_scene_configs_same_algorithm(self):
        """Test that all scene configs use the same algorithm."""
        basic_scene = instantiate(BFSBasicSceneConfig)
        advanced_scene = instantiate(BFSAdvancedSceneConfig)

        assert basic_scene.algorithm == advanced_scene.algorithm
        assert basic_scene.algorithm == "bfs"
