"""Tests for basic SceneEngine functionality."""

from hydra_zen import instantiate

from agloviz.config.hydra_zen import (
    BFSAdvancedSceneConfig,
    BFSBasicSceneConfig,
    BFSDynamicSceneConfig,
)
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.scene import SceneEngine


def create_scene_engine(scene_config, timing_mode=TimingMode.NORMAL):
    """Helper function to create SceneEngine with timing config."""
    timing_config = TimingConfig(mode=timing_mode)
    return SceneEngine(scene_config, timing_config)


class TestSceneEngineBasicConfigs:
    """Test SceneEngine initialization with basic scene config types."""

    def test_scene_engine_with_bfs_basic_scene_config(self):
        """Test SceneEngine with BFSBasicSceneConfig."""
        scene_config = instantiate(BFSBasicSceneConfig)
        scene_engine = create_scene_engine(scene_config)
        assert scene_engine.get_scene_name() == "bfs_basic"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2

    def test_scene_engine_with_bfs_advanced_scene_config(self):
        """Test SceneEngine with BFSAdvancedSceneConfig."""
        scene_config = instantiate(BFSAdvancedSceneConfig)
        scene_engine = create_scene_engine(scene_config)
        assert scene_engine.get_scene_name() == "bfs_advanced"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2

    def test_scene_engine_with_bfs_dynamic_scene_config(self):
        """Test SceneEngine with BFSDynamicSceneConfig."""
        scene_config = instantiate(BFSDynamicSceneConfig)
        scene_engine = create_scene_engine(scene_config)
        assert scene_engine.get_scene_name() == "bfs_dynamic"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2
