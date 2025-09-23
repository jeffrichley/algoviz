"""Tests for SceneEngine with YAML configurations."""

from hydra_zen import instantiate
from omegaconf import OmegaConf

from agloviz.config.hydra_zen import BFSBasicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.scene import SceneEngine


def create_scene_engine(scene_config, timing_mode=TimingMode.NORMAL):
    """Helper function to create SceneEngine with timing config."""
    timing_config = TimingConfig(mode=timing_mode)
    return SceneEngine(scene_config, timing_config)


class TestSceneEngineYamlConfigs:
    """Test SceneEngine initialization with YAML configs."""

    def test_scene_engine_with_yaml_configs(self):
        """Test SceneEngine with YAML-loaded configs converted to Pydantic models."""
        yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")
        scene_overrides = {
            k: v for k, v in yaml_config.items() if k != "timing_overrides"
        }
        scene_config = instantiate(BFSBasicSceneConfig, **scene_overrides)
        scene_engine = create_scene_engine(scene_config)
        assert scene_engine.get_scene_name() == "bfs_pathfinding"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2
