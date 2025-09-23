"""YAML dynamic test."""

from omegaconf import OmegaConf


def test_yaml_override_behavior():
    """Test YAML override behavior with structured configs."""
    yaml_config = OmegaConf.load("configs/scene/bfs_dynamic.yaml")
    assert yaml_config.name == "bfs_dynamic"
    assert yaml_config.algorithm == "bfs"
    assert "widgets" in yaml_config
    grid_widget = yaml_config.widgets.grid
    assert grid_widget.width == 15
    assert grid_widget.height == 15
    assert grid_widget.cell_size == 0.5
