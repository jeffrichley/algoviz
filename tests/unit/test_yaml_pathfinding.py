"""YAML pathfinding test."""

from omegaconf import OmegaConf


def test_yaml_references_hydra_zen_config():
    """Test YAML files that reference hydra-zen structured configs."""
    yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")
    assert yaml_config.name == "bfs_pathfinding"
    assert yaml_config.algorithm == "bfs"
    assert "widgets" in yaml_config
    assert "event_bindings" in yaml_config
    assert yaml_config.widgets.grid._target_ == "agloviz.widgets.grid.GridWidget"
    assert yaml_config.widgets.queue._target_ == "agloviz.widgets.queue.QueueWidget"
