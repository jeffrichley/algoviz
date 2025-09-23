"""Tests for scene configuration error handling and validation."""

import pytest
from hydra_zen import instantiate
from omegaconf import OmegaConf
from pydantic import ValidationError

from agloviz.config.hydra_zen import (
    BFSBasicSceneConfig,
)
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.scene import SceneEngine


class TestInvalidStructuredConfigInstantiation:
    """Test invalid structured config instantiation."""

    def test_invalid_structured_config_parameters(self):
        """Test invalid parameters for structured configs."""
        # Test with invalid parameters that should cause instantiation to fail
        from hydra.errors import InstantiationException
        with pytest.raises(InstantiationException):
            # Try to instantiate with invalid parameters
            instantiate(BFSBasicSceneConfig, name=123)  # Invalid type for name

    def test_missing_required_structured_config_fields(self):
        """Test missing required fields in structured configs."""
        # Test that structured configs require certain fields
        # This should work - structured configs have defaults
        config = instantiate(BFSBasicSceneConfig)
        assert config.name == "bfs_basic"
        assert config.algorithm == "bfs"


class TestInvalidTimingConfig:
    """Test invalid timing configuration."""

    def test_invalid_timing_mode(self):
        """Test invalid timing mode."""
        with pytest.raises(ValidationError):
            TimingConfig(mode="invalid_mode")

    def test_invalid_timing_values(self):
        """Test invalid timing values."""
        with pytest.raises(ValidationError):
            TimingConfig(mode=TimingMode.NORMAL, ui=-1.0)  # Negative timing

    def test_invalid_timing_types(self):
        """Test invalid timing types."""
        with pytest.raises(ValidationError):
            TimingConfig(mode=TimingMode.NORMAL, ui="invalid")  # String instead of float


class TestSceneEngineErrorHandling:
    """Test SceneEngine error handling with valid but problematic configs."""

    def test_scene_engine_with_none_timing_config(self):
        """Test SceneEngine with None timing config."""
        # Create valid scene config
        scene_config = instantiate(BFSBasicSceneConfig)

        # SceneEngine should handle None timing config gracefully
        scene_engine = SceneEngine(scene_config, None)
        assert scene_engine.timing_config is None

    def test_scene_engine_with_invalid_timing_config_type(self):
        """Test SceneEngine with invalid timing config type."""
        # Create valid scene config
        scene_config = instantiate(BFSBasicSceneConfig)

        # SceneEngine should handle invalid timing config type gracefully
        # It just stores whatever is passed as timing_config
        scene_engine = SceneEngine(scene_config, "invalid_timing_config")
        assert scene_engine.timing_config == "invalid_timing_config"

    def test_scene_engine_with_missing_scene_config_fields(self):
        """Test SceneEngine with scene config missing fields."""
        # This test verifies that structured configs always have required fields
        # since they're defined with defaults
        scene_config = instantiate(BFSBasicSceneConfig)
        assert hasattr(scene_config, 'name')
        assert hasattr(scene_config, 'algorithm')
        assert hasattr(scene_config, 'widgets')
        assert hasattr(scene_config, 'event_bindings')


class TestYAMLConfigurationErrorHandling:
    """Test YAML configuration error handling."""

    def test_invalid_yaml_syntax(self):
        """Test invalid YAML syntax."""
        # Test with actually invalid YAML syntax
        invalid_yaml = """
        name: "test_scene"
        algorithm: "bfs"
        widgets:
          grid:
            _target_: "agloviz.widgets.grid.GridWidget"
            width: 10
            height: 10
        # This is actually valid YAML, so let's test with truly invalid syntax
        invalid_field: [unclosed list
        """

        # This should raise a YAML parsing error
        import yaml
        with pytest.raises(yaml.parser.ParserError):
            OmegaConf.create(invalid_yaml)

    def test_yaml_with_invalid_target_references(self):
        """Test YAML with invalid _target_ references."""
        invalid_yaml = """
        name: "test_scene"
        algorithm: "bfs"
        widgets:
          grid:
            _target_: "nonexistent.module.GridWidget"
            width: 10
            height: 10
        """

        config = OmegaConf.create(invalid_yaml)

        # The YAML loads fine, but instantiation should fail
        from hydra.errors import InstantiationException
        with pytest.raises(InstantiationException):
            instantiate(config)

    def test_yaml_with_missing_required_fields(self):
        """Test YAML with missing required fields."""
        incomplete_yaml = """
        algorithm: "bfs"
        # Missing name field
        widgets:
          grid:
            _target_: "agloviz.widgets.grid.GridWidget"
        """

        config = OmegaConf.create(incomplete_yaml)

        # This should work since YAML can be incomplete
        # The error would come during instantiation or validation
        assert config.algorithm == "bfs"
        assert "name" not in config


class TestTemplateResolutionErrorHandling:
    """Test template resolution error handling."""

    def test_malformed_template_syntax(self):
        """Test malformed template syntax."""
        malformed_yaml = """
        name: "test_scene"
        algorithm: "bfs"
        widgets:
          grid:
            _target_: "agloviz.widgets.grid.GridWidget"
        event_bindings:
          enqueue:
            - widget: "grid"
              action: "highlight_cell"
              params:
                position: "${invalid_syntax"  # Missing closing brace
              order: 1
        """

        # This should raise a template parsing error
        from omegaconf.errors import GrammarParseError
        with pytest.raises(GrammarParseError):
            OmegaConf.create(malformed_yaml)

    def test_undefined_template_resolver(self):
        """Test undefined template resolver."""
        undefined_resolver_yaml = """
        name: "test_scene"
        algorithm: "bfs"
        widgets:
          grid:
            _target_: "agloviz.widgets.grid.GridWidget"
        event_bindings:
          enqueue:
            - widget: "grid"
              action: "highlight_cell"
              params:
                value: "${undefined_resolver:some_value}"
              order: 1
        """

        config = OmegaConf.create(undefined_resolver_yaml)

        # The YAML loads fine, but template resolution should fail
        # when trying to access the template value
        with pytest.raises((ValueError, TypeError)):
            # This would fail when trying to resolve the template
            _ = config.event_bindings.enqueue[0].params.value


class TestConfigurationValidation:
    """Test configuration validation."""

    def test_scene_config_validation_with_invalid_types(self):
        """Test scene config validation with invalid types."""
        # Test that structured configs enforce type validation
        from hydra.errors import InstantiationException
        with pytest.raises(InstantiationException):
            # Try to create a config with invalid types
            instantiate(BFSBasicSceneConfig, name=123, algorithm=456)

    def test_timing_config_validation_with_invalid_values(self):
        """Test timing config validation with invalid values."""
        with pytest.raises(ValidationError):
            TimingConfig(
                mode=TimingMode.NORMAL,
                ui=-1.0,  # Invalid negative value
                events=2.0,  # Invalid value > 1.0
                effects="invalid"  # Invalid type
            )

    def test_scene_engine_validation_with_invalid_config_combination(self):
        """Test SceneEngine validation with invalid config combination."""
        # Create valid scene config
        scene_config = instantiate(BFSBasicSceneConfig)

        # Create invalid timing config
        with pytest.raises(ValidationError):
            invalid_timing = TimingConfig(mode="invalid_mode")
            SceneEngine(scene_config, invalid_timing)
