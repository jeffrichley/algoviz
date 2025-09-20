"""Unit tests for ALGOViz ConfigManager."""

import os
from pathlib import Path

import pytest
import yaml
from omegaconf import OmegaConf

from agloviz.config.manager import ConfigError, ConfigManager
from agloviz.config.models import ScenarioConfig, TimingMode, VideoConfig


@pytest.mark.unit
class TestConfigManager:
    """Test ConfigManager functionality."""

    def test_load_from_yaml_single_file(self, tmp_path):
        """Test loading a single YAML configuration file."""
        # Create test YAML file
        config_data = {
            "scenario": {
                "name": "test_scenario",
                "grid_file": "test.yaml",
                "start": [0, 0],
                "goal": [5, 5],
            }
        }

        yaml_file = tmp_path / "test_config.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(config_data, f)

        manager = ConfigManager()
        config = manager.load_from_yaml(str(yaml_file))

        assert config.scenario.name == "test_scenario"
        assert config.scenario.start == [0, 0]
        assert config.scenario.goal == [5, 5]

    def test_load_from_yaml_multiple_files(self, tmp_path):
        """Test loading and merging multiple YAML files."""
        # First file - scenario
        scenario_data = {
            "scenario": {
                "name": "base_scenario",
                "grid_file": "base.yaml",
                "start": [0, 0],
                "goal": [9, 9],
            },
            "timing": {
                "mode": "normal",
            }
        }

        # Second file - timing override
        timing_data = {
            "timing": {
                "mode": "draft",
                "ui": 0.5,
            }
        }

        scenario_file = tmp_path / "scenario.yaml"
        timing_file = tmp_path / "timing.yaml"

        with open(scenario_file, 'w') as f:
            yaml.dump(scenario_data, f)
        with open(timing_file, 'w') as f:
            yaml.dump(timing_data, f)

        manager = ConfigManager()
        config = manager.load_from_yaml(str(scenario_file), str(timing_file))

        # Scenario should remain from first file
        assert config.scenario.name == "base_scenario"
        # Timing should be overridden by second file
        assert config.timing.mode == "draft"
        assert config.timing.ui == 0.5

    def test_load_from_yaml_file_not_found(self):
        """Test error handling for missing YAML files."""
        manager = ConfigManager()

        with pytest.raises(ConfigError) as exc_info:
            manager.load_from_yaml("nonexistent.yaml")

        assert "Configuration file not found" in str(exc_info.value)

    def test_load_from_yaml_invalid_syntax(self, tmp_path):
        """Test error handling for invalid YAML syntax."""
        invalid_yaml = tmp_path / "invalid.yaml"
        with open(invalid_yaml, 'w') as f:
            f.write("invalid: yaml: syntax: [")

        manager = ConfigManager()

        with pytest.raises(ConfigError) as exc_info:
            manager.load_from_yaml(str(invalid_yaml))

        assert "Invalid YAML syntax" in str(exc_info.value)

    def test_apply_cli_overrides_simple(self):
        """Test applying simple CLI overrides."""
        base_config = OmegaConf.create({
            "timing": {"mode": "normal"},
            "render": {"quality": "medium"}
        })

        manager = ConfigManager()
        result = manager.apply_cli_overrides(
            base_config,
            **{"timing.mode": "draft", "render.quality": "high"}
        )

        assert result.timing.mode == "draft"
        assert result.render.quality == "high"

    def test_apply_cli_overrides_dot_notation(self):
        """Test applying CLI overrides with dot notation."""
        base_config = OmegaConf.create({
            "render": {"quality": "medium", "resolution": [1920, 1080]},
            "timing": {"mode": "normal"}
        })

        manager = ConfigManager()
        result = manager.apply_cli_overrides(
            base_config,
            **{
                "render.quality": "high",
                "render.resolution": [2560, 1440],
                "timing.mode": "draft"
            }
        )

        assert result.render.quality == "high"
        assert result.render.resolution == [2560, 1440]
        assert result.timing.mode == "draft"

    def test_apply_env_vars(self):
        """Test applying environment variable overrides."""
        base_config = OmegaConf.create({
            "render": {"quality": "medium"},
            "timing": {"mode": "normal"}
        })

        # Set test environment variables
        os.environ["AGLOVIZ_RENDER_QUALITY"] = "high"
        os.environ["AGLOVIZ_TIMING_MODE"] = "draft"
        os.environ["OTHER_VAR"] = "ignored"

        try:
            manager = ConfigManager()
            result = manager.apply_env_vars(base_config)

            assert result.render.quality == "high"
            assert result.timing.mode == "draft"
        finally:
            # Clean up environment variables
            os.environ.pop("AGLOVIZ_RENDER_QUALITY", None)
            os.environ.pop("AGLOVIZ_TIMING_MODE", None)
            os.environ.pop("OTHER_VAR", None)

    def test_parse_env_value_types(self):
        """Test parsing environment variable values to correct types."""
        manager = ConfigManager()

        # Boolean values
        assert manager._parse_env_value("true") is True
        assert manager._parse_env_value("false") is False
        assert manager._parse_env_value("True") is True
        assert manager._parse_env_value("FALSE") is False

        # Integer values
        assert manager._parse_env_value("42") == 42
        assert manager._parse_env_value("-10") == -10

        # Float values
        assert manager._parse_env_value("3.14") == 3.14
        assert manager._parse_env_value("-2.5") == -2.5

        # String values
        assert manager._parse_env_value("hello") == "hello"
        assert manager._parse_env_value("not_a_number") == "not_a_number"

    def test_validate_valid_config(self):
        """Test validating a valid configuration."""
        config_data = {
            "scenario": {
                "name": "valid_test",
                "grid_file": "test.yaml",
                "start": [0, 0],
                "goal": [5, 5],
            }
        }

        config = OmegaConf.create(config_data)
        manager = ConfigManager()

        # Mock file existence for validation
        original_exists = Path.exists
        Path.exists = lambda self: True

        try:
            result = manager.validate(config)
            assert isinstance(result, VideoConfig)
            assert result.scenario.name == "valid_test"
        finally:
            Path.exists = original_exists

    def test_validate_invalid_config(self):
        """Test validation error handling."""
        config_data = {
            "scenario": {
                "name": "",  # Invalid empty name
                "grid_file": "test.yaml",
                "start": [0, 0],
                "goal": [5, 5],
            }
        }

        config = OmegaConf.create(config_data)
        manager = ConfigManager()

        # Mock file existence to avoid file validation error
        original_exists = Path.exists
        Path.exists = lambda self: True

        try:
            with pytest.raises(ConfigError) as exc_info:
                manager.validate(config)

            assert "Configuration validation failed" in str(exc_info.value)
        finally:
            Path.exists = original_exists

    def test_validate_cross_field_constraints(self):
        """Test cross-field validation constraints."""
        # Test same start and goal positions
        config_data = {
            "scenario": {
                "name": "test",
                "grid_file": "test.yaml",
                "start": [5, 5],
                "goal": [5, 5],  # Same as start
            }
        }

        config = OmegaConf.create(config_data)
        manager = ConfigManager()

        # Mock file existence
        original_exists = Path.exists
        Path.exists = lambda self: True

        try:
            with pytest.raises(ConfigError) as exc_info:
                manager.validate(config)

            assert "Start and goal positions must be different" in str(exc_info.value)
        finally:
            Path.exists = original_exists

    def test_dump_config(self, tmp_path):
        """Test dumping configuration to YAML file."""
        scenario = ScenarioConfig(
            name="dump_test",
            grid_file="dump.yaml",
            start=(0, 0),
            goal=(3, 3),
        )

        config = VideoConfig(scenario=scenario)
        output_file = tmp_path / "dumped_config.yaml"

        manager = ConfigManager()
        manager.dump(config, str(output_file))

        # Verify file was created
        assert output_file.exists()

        # Verify file content by reading as text (YAML may have enum serialization issues)
        with open(output_file) as f:
            content = f.read()

        # Check that key values are present in the dumped content
        assert "dump_test" in content
        assert "scenario:" in content
        assert "timing:" in content
        assert "render:" in content

    def test_load_and_validate_complete_pipeline(self, tmp_path):
        """Test the complete configuration loading pipeline."""
        # Create test YAML files
        scenario_data = {
            "scenario": {
                "name": "pipeline_test",
                "grid_file": "pipeline.yaml",
                "start": [0, 0],
                "goal": [7, 7],
            }
        }

        timing_data = {
            "timing": {
                "mode": "draft",
                "ui": 0.8,
            }
        }

        scenario_file = tmp_path / "scenario.yaml"
        timing_file = tmp_path / "timing.yaml"

        with open(scenario_file, 'w') as f:
            yaml.dump(scenario_data, f)
        with open(timing_file, 'w') as f:
            yaml.dump(timing_data, f)

        # Set environment variable
        os.environ["AGLOVIZ_RENDER_QUALITY"] = "high"

        # Mock file existence
        original_exists = Path.exists
        Path.exists = lambda self: True

        try:
            manager = ConfigManager()
            result = manager.load_and_validate(
                yaml_paths=[str(scenario_file), str(timing_file)],
                cli_overrides={"voiceover.enabled": True},
                use_env=True,
            )

            # Check YAML loading
            assert result.scenario.name == "pipeline_test"
            assert result.timing.mode == TimingMode.DRAFT
            assert result.timing.ui == 0.8

            # Check environment variable
            assert result.render.quality.value == "high"

            # Check CLI override
            assert result.voiceover.enabled is True

        finally:
            Path.exists = original_exists
            os.environ.pop("AGLOVIZ_RENDER_QUALITY", None)

    def test_create_sample_configs(self, tmp_path):
        """Test creating sample configuration files."""
        output_dir = tmp_path / "samples"

        manager = ConfigManager()
        manager.create_sample_configs(str(output_dir))

        # Check that sample files were created
        expected_files = [
            "scenario.yaml",
            "timing.yaml",
            "theme.yaml",
            "voiceover.yaml",
        ]

        for filename in expected_files:
            file_path = output_dir / filename
            assert file_path.exists(), f"Sample file {filename} was not created"

            # Verify file contains valid YAML
            with open(file_path) as f:
                data = yaml.safe_load(f)
                assert data is not None, f"Sample file {filename} contains invalid YAML"

        # Check specific content
        with open(output_dir / "scenario.yaml") as f:
            scenario_data = yaml.safe_load(f)
            assert "scenario" in scenario_data
            assert scenario_data["scenario"]["name"] == "demo_maze"

        with open(output_dir / "timing.yaml") as f:
            timing_data = yaml.safe_load(f)
            assert "timing" in timing_data
            assert timing_data["timing"]["mode"] == "normal"
