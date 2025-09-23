"""Basic scene config test."""

from hydra_zen import instantiate

from agloviz.config.hydra_zen import BFSBasicSceneConfig


def test_basic_scene_config_instantiation():
    """Test BFSBasicSceneConfig instantiation."""
    basic_scene = instantiate(BFSBasicSceneConfig)
    assert basic_scene.name == "bfs_basic"
    assert basic_scene.algorithm == "bfs"
    assert "grid" in basic_scene.widgets
    assert "queue" in basic_scene.widgets
