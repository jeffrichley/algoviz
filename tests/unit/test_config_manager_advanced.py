"""Advanced tests for ConfigManager CLI override functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from omegaconf import OmegaConf

from agloviz.config.manager import ConfigManager


@pytest.mark.unit
class TestConfigManagerAdvanced:
    """Test advanced ConfigManager functionality."""

    def test_apply_cli_overrides_simple_keys(self):
        """Test CLI overrides with simple (non-nested) keys."""
        manager = ConfigManager()
        config = OmegaConf.create({
            "existing": "value",
            "number": 42
        })

        # Test simple key-value override
        result = manager.apply_cli_overrides(config, new_key="new_value", another_key=123)

        assert result.existing == "value"  # Existing preserved
        assert result.number == 42  # Existing preserved
        assert result.new_key == "new_value"  # New key added
        assert result.another_key == 123  # New key added

    def test_apply_cli_overrides_override_existing(self):
        """Test CLI overrides that override existing values."""
        manager = ConfigManager()
        config = OmegaConf.create({
            "mode": "normal",
            "count": 10
        })

        # Override existing values
        result = manager.apply_cli_overrides(config, mode="fast", count=20)

        assert result.mode == "fast"  # Overridden
        assert result.count == 20  # Overridden

    def test_apply_cli_overrides_mixed_simple_and_nested(self):
        """Test CLI overrides with both simple and nested keys."""
        manager = ConfigManager()
        config = OmegaConf.create({
            "simple": "value",
            "nested": {
                "inner": "old"
            }
        })

        # Mix of simple and nested overrides
        result = manager.apply_cli_overrides(
            config,
            simple="updated",  # Simple override
            new_simple="added",  # Simple addition
            **{"nested.inner": "new", "nested.new_inner": "added"}  # Nested overrides
        )

        assert result.simple == "updated"
        assert result.new_simple == "added"
        assert result.nested.inner == "new"
        assert result.nested.new_inner == "added"

    def test_environment_variable_overrides(self):
        """Test environment variable override functionality."""
        manager = ConfigManager()
        config = OmegaConf.create({
            "timing": {
                "mode": "normal"
            },
            "render": {
                "quality": "medium"
            }
        })

        # Test environment variable overrides
        with patch.dict(os.environ, {
            "AGLOVIZ_TIMING_MODE": "fast",
            "AGLOVIZ_RENDER_QUALITY": "high",
            "AGLOVIZ_NEW_SETTING": "env_value"
        }):
            result = manager.apply_env_vars(config)

            assert result.timing.mode == "fast"
            assert result.render.quality == "high"
            assert result.new.setting == "env_value"  # Environment vars create nested structure

    def test_environment_variable_custom_prefix(self):
        """Test environment variable overrides with custom prefix."""
        manager = ConfigManager()
        config = OmegaConf.create({"setting": "default"})

        with patch.dict(os.environ, {
            "CUSTOM_SETTING": "custom_value",
            "AGLOVIZ_SETTING": "should_be_ignored"
        }):
            result = manager.apply_env_vars(config, prefix="CUSTOM_")

            assert result.setting == "custom_value"
            # The AGLOVIZ_ prefixed variable should be ignored
            assert not hasattr(result, 'agloviz_setting')

    def test_create_sample_configs_custom_directory(self):
        """Test creating sample configs in a custom directory."""
        manager = ConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir) / "custom_samples"

            # Create samples in custom directory
            manager.create_sample_configs(str(custom_dir))

            # Verify files were created
            assert custom_dir.exists()
            assert (custom_dir / "scenario.yaml").exists()
            assert (custom_dir / "timing.yaml").exists()
            assert (custom_dir / "theme.yaml").exists()
            assert (custom_dir / "voiceover.yaml").exists()

            # Verify content of one file
            scenario_content = (custom_dir / "scenario.yaml").read_text()
            assert "name:" in scenario_content
            assert "grid_file:" in scenario_content
            assert "start:" in scenario_content
            assert "goal:" in scenario_content

    def test_dump_config_with_enums(self):
        """Test dumping configuration that contains enum values."""
        from agloviz.config.models import RenderFormat, RenderQuality, TimingMode

        manager = ConfigManager()

        # Create a config with enum values (include required scenario field)
        config_dict = {
            "scenario": {
                "name": "test_scenario",
                "grid_file": "test.grid",
                "start": (0, 0),
                "goal": (5, 5)
            },
            "render": {
                "quality": RenderQuality.HIGH,
                "format": RenderFormat.MP4
            },
            "timing": {
                "mode": TimingMode.FAST
            }
        }

        # Convert to VideoConfig through validation
        from agloviz.config.models import VideoConfig
        video_config = VideoConfig(**config_dict)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            output_path = f.name

        try:
            # Should not raise an exception
            manager.dump(video_config, output_path)

            # Verify file was created and contains expected content
            dumped_content = Path(output_path).read_text()
            assert "render:" in dumped_content
            assert "timing:" in dumped_content
            # Enum values should be serialized as their string values
            assert "high" in dumped_content.lower()
            assert "mp4" in dumped_content.lower()
            assert "fast" in dumped_content.lower()

        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_load_and_validate_with_env_vars(self):
        """Test complete pipeline with environment variables."""
        manager = ConfigManager()

        # Create a temporary YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
scenario:
  name: "test_scenario"
  grid_file: "test.grid"
  start: [0, 0]
  goal: [5, 5]

timing:
  mode: "normal"
            """)
            yaml_path = f.name

        try:
            # Mock grid file existence
            with patch('pathlib.Path.exists', return_value=True):
                with patch.dict(os.environ, {"AGLOVIZ_TIMING_MODE": "fast"}):
                    result = manager.load_and_validate([yaml_path], use_env=True)

                    # Environment variable should override YAML
                    assert result.timing.mode.value == "fast"  # Enum value
                    assert result.scenario.name == "test_scenario"  # From YAML

        finally:
            Path(yaml_path).unlink(missing_ok=True)

    def test_load_and_validate_with_cli_overrides(self):
        """Test complete pipeline with CLI overrides."""
        manager = ConfigManager()

        # Create a temporary YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
scenario:
  name: "yaml_scenario"
  grid_file: "test.grid"
  start: [0, 0]
  goal: [5, 5]

render:
  quality: "medium"
            """)
            yaml_path = f.name

        try:
            # Mock grid file existence
            with patch('pathlib.Path.exists', return_value=True):
                result = manager.load_and_validate(
                    [yaml_path],
                    cli_overrides={"render.quality": "high", "scenario.name": "cli_scenario"}
                )

                # CLI overrides should take precedence
                assert result.render.quality.value == "high"  # From CLI
                assert result.scenario.name == "cli_scenario"  # From CLI

        finally:
            Path(yaml_path).unlink(missing_ok=True)

    def test_precedence_order_yaml_env_cli(self):
        """Test that CLI > ENV > YAML precedence is maintained."""
        manager = ConfigManager()

        # Create YAML with base values
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
scenario:
  name: "yaml_value"
  grid_file: "test.grid"
  start: [0, 0]
  goal: [5, 5]

timing:
  mode: "normal"

render:
  quality: "draft"
            """)
            yaml_path = f.name

        try:
            with patch('pathlib.Path.exists', return_value=True):
                with patch.dict(os.environ, {
                    "AGLOVIZ_TIMING_MODE": "fast",  # ENV override
                    "AGLOVIZ_RENDER_QUALITY": "medium"  # ENV override
                }):
                    result = manager.load_and_validate(
                        [yaml_path],
                        cli_overrides={"render.quality": "high"},  # CLI override
                        use_env=True
                    )

                    # CLI should win over ENV and YAML
                    assert result.render.quality.value == "high"  # CLI wins
                    # ENV should win over YAML
                    assert result.timing.mode.value == "fast"  # ENV wins over YAML
                    # YAML should be used when no override
                    assert result.scenario.name == "yaml_value"  # YAML used

        finally:
            Path(yaml_path).unlink(missing_ok=True)
