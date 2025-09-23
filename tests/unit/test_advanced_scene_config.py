"""Advanced scene config test."""

from hydra_zen import instantiate

from agloviz.config.hydra_zen import BFSAdvancedSceneConfig


def test_advanced_scene_config_instantiation():
    """Test BFSAdvancedSceneConfig instantiation."""
    advanced_scene = instantiate(BFSAdvancedSceneConfig)
    assert advanced_scene.name == "bfs_advanced"
    assert advanced_scene.algorithm == "bfs"
    assert "grid" in advanced_scene.widgets
    assert "queue" in advanced_scene.widgets
