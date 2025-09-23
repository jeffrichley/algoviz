"""Tests for SceneEngine widget instantiation."""

import pytest
from hydra_zen import instantiate
from omegaconf import OmegaConf

from agloviz.config.hydra_zen import BFSBasicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.scene import SceneEngine


def create_scene_engine(scene_config, timing_mode=TimingMode.NORMAL):
    """Helper function to create SceneEngine with timing config."""
    timing_config = TimingConfig(mode=timing_mode)
    return SceneEngine(scene_config, timing_config)


class TestWidgetInstantiationStructured:
    """Test widget instantiation from structured configs."""

    def test_widget_instantiation_from_structured_configs(self):
        """Test widget instantiation from structured configs."""
        scene_config = instantiate(BFSBasicSceneConfig)
        scene_engine = create_scene_engine(scene_config)
        assert len(scene_engine.widgets) == 2
        assert "grid" in scene_engine.widgets
        assert "queue" in scene_engine.widgets
        from agloviz.widgets.grid import GridWidget
        from agloviz.widgets.queue import QueueWidget

        assert isinstance(scene_engine.widgets["grid"], GridWidget)
        assert isinstance(scene_engine.widgets["queue"], QueueWidget)

    def test_widget_parameter_passing(self):
        """Test widget parameter passing."""
        scene_config = instantiate(BFSBasicSceneConfig)
        scene_engine = create_scene_engine(scene_config)
        grid_widget = scene_engine.widgets["grid"]
        assert hasattr(grid_widget, "width")
        assert hasattr(grid_widget, "height")
        queue_widget = scene_engine.widgets["queue"]
        assert queue_widget is not None


class TestWidgetInstantiationYaml:
    """Test widget instantiation from YAML configs."""

    def test_widget_instantiation_from_yaml_configs(self):
        """Test widget instantiation from YAML configs."""
        yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")
        scene_overrides = {
            k: v for k, v in yaml_config.items() if k != "timing_overrides"
        }
        scene_config = instantiate(BFSBasicSceneConfig, **scene_overrides)
        scene_engine = create_scene_engine(scene_config)
        assert len(scene_engine.widgets) == 2
        assert "grid" in scene_engine.widgets
        assert "queue" in scene_engine.widgets
        from agloviz.widgets.grid import GridWidget
        from agloviz.widgets.queue import QueueWidget

        assert isinstance(scene_engine.widgets["grid"], GridWidget)
        assert isinstance(scene_engine.widgets["queue"], QueueWidget)


class TestWidgetInstantiationErrors:
    """Test widget instantiation error handling."""

    def test_widget_instantiation_errors(self):
        """Test widget instantiation errors."""
        from hydra.errors import InstantiationException

        with pytest.raises(InstantiationException):
            invalid_config = {
                "name": "test_scene",
                "algorithm": "bfs",
                "widgets": {
                    "grid": {
                        "_target_": "agloviz.widgets.nonexistent.GridWidget",
                        "width": 10,
                        "height": 10,
                    }
                },
                "event_bindings": {},
            }
            instantiate(invalid_config)
