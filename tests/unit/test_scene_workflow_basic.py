"""Basic scene workflow tests."""

from hydra_zen import instantiate
from omegaconf import OmegaConf

from agloviz.config.hydra_zen import BFSBasicSceneConfig, BFSDynamicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.scene import SceneEngine


class TestSceneWorkflowBasic:
    """Basic scene workflow tests."""

    def test_yaml_to_scene_engine_workflow(self):
        """Test complete workflow from YAML to SceneEngine."""
        yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")
        assert yaml_config.name == "bfs_pathfinding"
        assert yaml_config.algorithm == "bfs"
        assert "widgets" in yaml_config
        assert "event_bindings" in yaml_config
        enqueue_bindings = yaml_config.event_bindings.enqueue
        assert len(enqueue_bindings) == 2
        first_binding = enqueue_bindings[0]
        assert "element" in first_binding.params

    def test_structured_config_to_scene_engine_workflow(self):
        """Test complete workflow from structured config to SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)
        assert scene_engine.get_scene_name() == "bfs_basic"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2
        assert "grid" in scene_engine.list_widget_names()
        assert "queue" in scene_engine.list_widget_names()

    def test_dynamic_scene_config_workflow(self):
        """Test workflow with dynamic parameter templates."""
        scene_config = instantiate(BFSDynamicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)
        assert scene_engine.get_scene_name() == "bfs_dynamic"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2
        assert "grid" in scene_engine.list_widget_names()
        assert "queue" in scene_engine.list_widget_names()
