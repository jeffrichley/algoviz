"""Tests for scene configuration system integration and SceneEngine functionality."""

import pytest
from hydra_zen import instantiate
from omegaconf import OmegaConf

from agloviz.config.hydra_zen import (
    BFSAdvancedSceneConfig,
    BFSBasicSceneConfig,
    BFSDynamicSceneConfig,
)
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.scene import SceneEngine


class TestSceneEngineInitialization:
    """Test SceneEngine initialization with different scene config types."""

    def test_scene_engine_with_bfs_basic_scene_config(self):
        """Test SceneEngine with BFSBasicSceneConfig."""
        # Create structured config
        scene_config = instantiate(BFSBasicSceneConfig)

        # Create timing config
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create SceneEngine
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify SceneEngine was created successfully
        assert scene_engine.get_scene_name() == "bfs_basic"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2  # grid + queue
        assert "grid" in scene_engine.list_widget_names()
        assert "queue" in scene_engine.list_widget_names()

    def test_scene_engine_with_bfs_advanced_scene_config(self):
        """Test SceneEngine with BFSAdvancedSceneConfig."""
        # Create structured config
        scene_config = instantiate(BFSAdvancedSceneConfig)

        # Create timing config
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create SceneEngine
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify SceneEngine was created successfully
        assert scene_engine.get_scene_name() == "bfs_advanced"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2  # grid + queue
        assert "grid" in scene_engine.list_widget_names()
        assert "queue" in scene_engine.list_widget_names()

    def test_scene_engine_with_bfs_dynamic_scene_config(self):
        """Test SceneEngine with BFSDynamicSceneConfig."""
        # Create structured config
        scene_config = instantiate(BFSDynamicSceneConfig)

        # Create timing config
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create SceneEngine
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify SceneEngine was created successfully
        assert scene_engine.get_scene_name() == "bfs_dynamic"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2  # grid + queue
        assert "grid" in scene_engine.list_widget_names()
        assert "queue" in scene_engine.list_widget_names()

    def test_scene_engine_with_yaml_configs(self):
        """Test SceneEngine with YAML-loaded configs converted to Pydantic models."""
        # Load YAML as overrides for a structured config
        yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")

        # Filter out fields that aren't part of SceneConfig
        scene_overrides = {k: v for k, v in yaml_config.items() if k != "timing_overrides"}

        # Use the YAML as overrides for a structured config
        # This is the proper way: structured config + YAML overrides
        scene_config = instantiate(BFSBasicSceneConfig, **scene_overrides)

        # Create SceneEngine with the converted config
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify SceneEngine works with YAML-derived config
        assert scene_engine.get_scene_name() == "bfs_pathfinding"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2
        assert "grid" in scene_engine.widgets
        assert "queue" in scene_engine.widgets


class TestWidgetInstantiationFromSceneConfigs:
    """Test widget instantiation from scene configurations."""

    def test_widget_instantiation_from_structured_configs(self):
        """Test widget instantiation from structured configs."""
        # Test with BFSBasicSceneConfig
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify widgets were instantiated
        assert len(scene_engine.widgets) == 2
        assert "grid" in scene_engine.widgets
        assert "queue" in scene_engine.widgets

        # Verify widget types
        from agloviz.widgets.grid import GridWidget
        from agloviz.widgets.queue import QueueWidget
        assert isinstance(scene_engine.widgets["grid"], GridWidget)
        assert isinstance(scene_engine.widgets["queue"], QueueWidget)

    def test_widget_instantiation_from_yaml_configs(self):
        """Test widget instantiation from YAML configs."""
        # Load YAML as overrides for a structured config
        yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")

        # Filter out fields that aren't part of SceneConfig
        scene_overrides = {k: v for k, v in yaml_config.items() if k != "timing_overrides"}
        scene_config = instantiate(BFSBasicSceneConfig, **scene_overrides)

        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify widgets were instantiated
        assert len(scene_engine.widgets) == 2
        assert "grid" in scene_engine.widgets
        assert "queue" in scene_engine.widgets

        # Verify widget types
        from agloviz.widgets.grid import GridWidget
        from agloviz.widgets.queue import QueueWidget
        assert isinstance(scene_engine.widgets["grid"], GridWidget)
        assert isinstance(scene_engine.widgets["queue"], QueueWidget)

    def test_widget_parameter_passing(self):
        """Test widget parameter passing."""
        # Test that widget parameters are passed correctly
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify grid widget has correct parameters
        grid_widget = scene_engine.widgets["grid"]
        assert hasattr(grid_widget, 'width')
        assert hasattr(grid_widget, 'height')

        # Verify queue widget exists (don't assume specific attributes)
        queue_widget = scene_engine.widgets["queue"]
        assert queue_widget is not None

    def test_widget_instantiation_errors(self):
        """Test widget instantiation errors."""
        # Test with invalid widget target in structured config
        # This should be caught at the structured config level, not SceneEngine level
        from hydra.errors import InstantiationException
        with pytest.raises(InstantiationException):
            # Try to create a config with invalid widget target
            invalid_config = {
                "name": "test_scene",
                "algorithm": "bfs",
                "widgets": {
                    "grid": {
                        "_target_": "agloviz.widgets.nonexistent.GridWidget",
                        "width": 10,
                        "height": 10
                    }
                },
                "event_bindings": {}
            }
            instantiate(invalid_config)


class TestEventBindingSetup:
    """Test event binding setup from scene configurations."""

    def test_event_binding_setup_from_structured_configs(self):
        """Test event binding setup from structured configs."""
        # Test with BFSBasicSceneConfig
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify event bindings were set up
        assert "enqueue" in scene_engine.event_bindings
        assert "dequeue" in scene_engine.event_bindings

        # Verify event binding structure
        enqueue_bindings = scene_engine.event_bindings["enqueue"]
        assert len(enqueue_bindings) == 2

        dequeue_bindings = scene_engine.event_bindings["dequeue"]
        assert len(dequeue_bindings) == 1

    def test_event_binding_setup_from_yaml_configs(self):
        """Test event binding setup from YAML configs converted to Pydantic models."""
        # Load YAML as overrides for a structured config
        yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")

        # Filter out fields that aren't part of SceneConfig
        scene_overrides = {k: v for k, v in yaml_config.items() if k != "timing_overrides"}
        scene_config = instantiate(BFSBasicSceneConfig, **scene_overrides)

        # Create SceneEngine and verify event bindings are set up
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify event bindings were set up correctly
        assert "enqueue" in scene_engine.event_bindings
        assert "dequeue" in scene_engine.event_bindings

        # Verify event binding structure
        enqueue_bindings = scene_engine.event_bindings["enqueue"]
        assert len(enqueue_bindings) == 2

        dequeue_bindings = scene_engine.event_bindings["dequeue"]
        assert len(dequeue_bindings) == 1

    def test_event_binding_ordering(self):
        """Test event binding ordering."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify event bindings are ordered correctly
        enqueue_bindings = scene_engine.event_bindings["enqueue"]
        assert enqueue_bindings[0].order == 1
        assert enqueue_bindings[1].order == 2

    def test_event_binding_parameter_resolution(self):
        """Test event binding parameter resolution."""
        # Note: Template resolution with custom resolvers is tested in the
        # TestSceneEngineInternalOmegaConfConversion class where resolvers are properly registered
        # This test just verifies that event bindings exist and have the expected structure
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify event bindings exist
        assert "enqueue" in scene_engine.event_bindings
        assert "dequeue" in scene_engine.event_bindings

        # Verify event binding structure
        enqueue_bindings = scene_engine.event_bindings["enqueue"]
        assert len(enqueue_bindings) == 2

        dequeue_bindings = scene_engine.event_bindings["dequeue"]
        assert len(dequeue_bindings) == 1


class TestSceneConfigurationAccess:
    """Test scene configuration access methods."""

    def test_scene_configuration_access_methods(self):
        """Test scene configuration access methods."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Test access methods
        assert scene_engine.get_scene_name() == "bfs_basic"
        assert scene_engine.get_scene_algorithm() == "bfs"
        assert scene_engine.get_widget_count() == 2
        assert scene_engine.list_widget_names() == ["grid", "queue"]

    def test_scene_configuration_with_different_timing_modes(self):
        """Test scene configuration with different timing modes."""
        scene_config = instantiate(BFSBasicSceneConfig)

        # Test with different timing modes
        for mode in [TimingMode.DRAFT, TimingMode.NORMAL, TimingMode.FAST]:
            timing_config = TimingConfig(mode=mode)
            scene_engine = SceneEngine(scene_config, timing_config)

            # Verify SceneEngine was created successfully
            assert scene_engine.get_scene_name() == "bfs_basic"
            assert scene_engine.timing_config.mode == mode

    def test_scene_configuration_without_timing_config(self):
        """Test scene configuration without timing config."""
        scene_config = instantiate(BFSBasicSceneConfig)

        # Create SceneEngine without timing config
        scene_engine = SceneEngine(scene_config, None)

        # Verify SceneEngine was created successfully
        assert scene_engine.get_scene_name() == "bfs_basic"
        assert scene_engine.timing_config is None


class TestSceneEngineInternalOmegaConfConversion:
    """Test SceneEngine's internal Pydantic to OmegaConf conversion."""

    def test_scene_engine_converts_pydantic_to_omegaconf(self):
        """Test that SceneEngine converts Pydantic models to OmegaConf internally."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify that SceneEngine has created an internal OmegaConf config
        assert hasattr(scene_engine, 'scene_config')
        assert scene_engine.scene_config is not None

        # Verify the OmegaConf config has the expected structure
        assert scene_engine.scene_config.name == "bfs_basic"
        assert scene_engine.scene_config.algorithm == "bfs"
        assert "event_bindings" in scene_engine.scene_config

    def test_scene_engine_omegaconf_excludes_widgets(self):
        """Test that SceneEngine's internal OmegaConf excludes widgets."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Verify that widgets are excluded from the internal OmegaConf config
        # (widgets are already instantiated and stored separately)
        assert "widgets" not in scene_engine.scene_config
        assert len(scene_engine.widgets) == 2  # But widgets exist in the widgets dict

    def test_scene_engine_template_resolution_with_internal_omegaconf(self):
        """Test that SceneEngine can resolve templates using its internal OmegaConf config."""
        from agloviz.core.resolvers import register_custom_resolvers

        # Register custom resolvers
        register_custom_resolvers()

        # Create a scene config with template parameters
        scene_config = instantiate(BFSDynamicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)

        # Create a test event
        test_event = {
            "node": {"id": "test_node", "position": [1, 2]},
            "step": 5
        }

        # Test parameter resolution using SceneEngine's internal OmegaConf
        test_params = {
            "element": "${event_data:node.id}",
            "position": "${event_data:node.position}",
            "step": "${event_data:step}"
        }

        # Use SceneEngine's internal resolution method
        resolved_params = scene_engine._resolve_parameters(test_params, test_event)

        # Verify resolution worked
        assert resolved_params["element"] == "test_node"
        assert resolved_params["position"] == [1, 2]
        assert resolved_params["step"] == 5
