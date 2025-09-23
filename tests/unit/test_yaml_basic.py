"""Basic YAML integration tests."""

from omegaconf import OmegaConf


class TestYAMLBasic:
    """Basic YAML file tests."""

    def test_yaml_references_hydra_zen_config(self):
        """Test YAML files that reference hydra-zen structured configs."""
        yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")
        assert yaml_config.name == "bfs_pathfinding"
        assert yaml_config.algorithm == "bfs"
        assert "widgets" in yaml_config
        assert "event_bindings" in yaml_config
        assert yaml_config.widgets.grid._target_ == "agloviz.widgets.grid.GridWidget"
        assert yaml_config.widgets.queue._target_ == "agloviz.widgets.queue.QueueWidget"

    def test_yaml_override_behavior(self):
        """Test YAML override behavior with structured configs."""
        yaml_config = OmegaConf.load("configs/scene/bfs_dynamic.yaml")
        assert yaml_config.name == "bfs_dynamic"
        assert yaml_config.algorithm == "bfs"
        assert "widgets" in yaml_config
        grid_widget = yaml_config.widgets.grid
        assert grid_widget.width == 15
        assert grid_widget.height == 15
        assert grid_widget.cell_size == 0.5
