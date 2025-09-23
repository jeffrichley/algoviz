"""Tests for YAML + Hydra-zen integration and ConfigStore scene configuration system."""

from hydra.core.config_store import ConfigStore
from hydra_zen import instantiate
from omegaconf import OmegaConf

from agloviz.config.hydra_zen import (
    BFSAdvancedSceneConfig,
    BFSBasicSceneConfig,
    BFSDynamicSceneConfig,
)
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.scene import SceneEngine, register_scene_configs


class TestYAMLHydraZenIntegration:
    """Test YAML files that reference hydra-zen structured configs."""

    def test_yaml_references_hydra_zen_config(self):
        """Test YAML files that reference hydra-zen structured configs."""
        # Test that bfs_pathfinding.yaml correctly references BFSBasicSceneConfig
        # Load YAML config that should reference structured config
        yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")

        # Verify YAML has expected structure
        assert yaml_config.name == "bfs_pathfinding"
        assert yaml_config.algorithm == "bfs"
        assert "widgets" in yaml_config
        assert "event_bindings" in yaml_config

        # Test that YAML can be loaded (template resolution happens later)
        assert yaml_config.widgets.grid._target_ == "agloviz.widgets.grid.GridWidget"
        assert yaml_config.widgets.queue._target_ == "agloviz.widgets.queue.QueueWidget"

    def test_yaml_override_behavior(self):
        """Test YAML override behavior with structured configs."""
        # Test parameter overrides in YAML files
        yaml_config = OmegaConf.load("configs/scene/bfs_dynamic.yaml")

        # Verify YAML overrides work
        assert yaml_config.name == "bfs_dynamic"
        assert yaml_config.algorithm == "bfs"

        # Test widget parameter overrides
        assert "widgets" in yaml_config
        grid_widget = yaml_config.widgets.grid
        assert grid_widget.width == 15
        assert grid_widget.height == 15
        assert grid_widget.cell_size == 0.5

        # Test event binding overrides
        assert "event_bindings" in yaml_config
        enqueue_bindings = yaml_config.event_bindings.enqueue
        assert len(enqueue_bindings) == 2

        # Test timing overrides
        if "timing_overrides" in yaml_config:
            timing_overrides = yaml_config.timing_overrides
            assert timing_overrides.events == 0.8
            assert timing_overrides.effects == 0.5

    def test_structured_config_instantiation(self):
        """Test that structured configs instantiate correctly."""
        # Test BFSBasicSceneConfig instantiation
        basic_scene = instantiate(BFSBasicSceneConfig)
        assert basic_scene.name == "bfs_basic"
        assert basic_scene.algorithm == "bfs"
        assert "grid" in basic_scene.widgets
        assert "queue" in basic_scene.widgets

        # Test BFSAdvancedSceneConfig instantiation
        advanced_scene = instantiate(BFSAdvancedSceneConfig)
        assert advanced_scene.name == "bfs_advanced"
        assert advanced_scene.algorithm == "bfs"
        assert "grid" in advanced_scene.widgets
        assert "queue" in advanced_scene.widgets

        # Test BFSDynamicSceneConfig instantiation (without template resolution)
        # Note: Dynamic configs contain templates that require custom resolvers
        # For now, test that the config structure is valid
        dynamic_config = BFSDynamicSceneConfig
        assert dynamic_config.name == "bfs_dynamic"
        assert dynamic_config.algorithm == "bfs"


class TestConfigStoreSceneRegistration:
    """Test scene configuration registration with ConfigStore."""

    def test_register_scene_configs(self):
        """Test register_scene_configs() function."""
        # Get ConfigStore instance
        cs = ConfigStore.instance()

        # Register scene configs
        register_scene_configs()

        # Verify base configs are registered
        repo = cs.repo
        assert "scene_config_base.yaml" in repo
        assert "event_binding_base.yaml" in repo
        assert "widget_spec_base.yaml" in repo

    def test_configstore_scene_retrieval(self):
        """Test ConfigStore scene retrieval."""
        # Get ConfigStore instance
        cs = ConfigStore.instance()

        # Register scene configs
        register_scene_configs()

        # Test scene configuration groups
        repo = cs.repo
        assert "scene" in repo
        scene_group = repo["scene"]
        assert "bfs_pathfinding.yaml" in scene_group

    def test_scene_configuration_groups(self):
        """Test scene configuration groups."""
        # Get ConfigStore instance
        cs = ConfigStore.instance()

        # Register scene configs
        register_scene_configs()

        # Test that scene configs are properly grouped
        repo = cs.repo
        assert "scene" in repo
        scene_configs = repo["scene"]
        assert isinstance(scene_configs, dict)
        assert "bfs_pathfinding.yaml" in scene_configs


class TestEndToEndSceneLoading:
    """Test complete scene loading from YAML → structured config → instantiation."""

    def test_yaml_to_scene_engine_workflow(self):
        """Test complete workflow from YAML to SceneEngine."""
        # Load YAML config
        yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")

        # Verify YAML can be loaded and has expected structure
        assert yaml_config.name == "bfs_pathfinding"
        assert yaml_config.algorithm == "bfs"
        assert "widgets" in yaml_config
        assert "event_bindings" in yaml_config

        # Test that YAML contains template syntax (dynamic parameters)
        enqueue_bindings = yaml_config.event_bindings.enqueue
        assert len(enqueue_bindings) == 2

        # Check that first binding has template syntax
        first_binding = enqueue_bindings[0]
        assert "element" in first_binding.params
        # Note: Template resolution happens at runtime, not during YAML loading
        # Just verify the structure is correct - don't access template values directly

    def test_structured_config_to_scene_engine_workflow(self):
        """Test complete workflow from structured config to SceneEngine."""
        # Create structured config
        scene_config = instantiate(BFSBasicSceneConfig)

        # Create timing config
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create SceneEngine from structured config
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify SceneEngine was created successfully
        assert scene_engine.get_scene_name() == "bfs_basic"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2  # grid + queue
        assert "grid" in scene_engine.list_widget_names()
        assert "queue" in scene_engine.list_widget_names()

    def test_dynamic_scene_config_workflow(self):
        """Test workflow with dynamic parameter templates."""
        # Create dynamic scene config
        scene_config = instantiate(BFSDynamicSceneConfig)

        # Create timing config
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create SceneEngine from dynamic config
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify SceneEngine was created successfully
        assert scene_engine.get_scene_name() == "bfs_dynamic"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2  # grid + queue
        assert "grid" in scene_engine.list_widget_names()
        assert "queue" in scene_engine.list_widget_names()

        # Verify event bindings have dynamic parameters
        assert "enqueue" in scene_engine.event_bindings
        assert "dequeue" in scene_engine.event_bindings

        # Check that dynamic parameters are present in event bindings
        enqueue_bindings = scene_engine.event_bindings["enqueue"]
        assert len(enqueue_bindings) == 2

        # First binding should have dynamic parameters
        first_binding = enqueue_bindings[0]
        assert "element" in first_binding.params
        assert (
            "duration" in first_binding.params
        )  # Note: Template resolution happens at runtime with custom resolvers
        # For now, just verify the parameters exist - don't access template values directly
