"""Scene config instantiation tests."""

from hydra_zen import instantiate

from agloviz.config.hydra_zen import (
    BFSAdvancedSceneConfig,
    BFSBasicSceneConfig,
    BFSDynamicSceneConfig,
)


class TestSceneConfigInstantiation:
    """Scene config instantiation tests."""

    def test_basic_scene_config_instantiation(self):
        """Test BFSBasicSceneConfig instantiation."""
        basic_scene = instantiate(BFSBasicSceneConfig)
        assert basic_scene.name == "bfs_basic"
        assert basic_scene.algorithm == "bfs"
        assert "grid" in basic_scene.widgets
        assert "queue" in basic_scene.widgets

    def test_advanced_scene_config_instantiation(self):
        """Test BFSAdvancedSceneConfig instantiation."""
        advanced_scene = instantiate(BFSAdvancedSceneConfig)
        assert advanced_scene.name == "bfs_advanced"
        assert advanced_scene.algorithm == "bfs"
        assert "grid" in advanced_scene.widgets
        assert "queue" in advanced_scene.widgets

    def test_dynamic_scene_config_instantiation(self):
        """Test BFSDynamicSceneConfig instantiation."""
        dynamic_config = BFSDynamicSceneConfig
        assert dynamic_config.name == "bfs_dynamic"
        assert dynamic_config.algorithm == "bfs"
