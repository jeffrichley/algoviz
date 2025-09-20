"""Configuration manager for ALGOViz.

This module provides the ConfigManager class that handles loading, merging,
validating, and dumping configurations with proper precedence rules.
"""

import os
from pathlib import Path
from typing import Any

import yaml
from omegaconf import DictConfig, OmegaConf
from pydantic import ValidationError
from rich.console import Console

from agloviz.core.errors import ConfigError, FileContext

from .models import VideoConfig

console = Console()


class ConfigManager:
    """Manages configuration loading, merging, validation, and dumping."""

    def __init__(self):
        self.console = Console()

    def load_from_yaml(self, *yaml_paths: str) -> DictConfig:
        """Load and merge multiple YAML files with proper precedence.

        Args:
            *yaml_paths: Paths to YAML files to load and merge

        Returns:
            Merged OmegaConf configuration

        Raises:
            ConfigError: If files cannot be loaded or parsed
        """
        merged_config = OmegaConf.create({})

        for yaml_path in yaml_paths:
            try:
                path = Path(yaml_path)
                if not path.exists():
                    raise ConfigError(
                        issue=f"Configuration file not found: {yaml_path}",
                        context=FileContext(yaml_path),
                        remedy="Verify the file path exists and is accessible",
                    )

                with open(path) as f:
                    file_config = OmegaConf.load(f)

                # Deep merge with later files taking precedence
                merged_config = OmegaConf.merge(merged_config, file_config)

            except yaml.YAMLError as e:
                raise ConfigError(
                    issue=f"Invalid YAML syntax: {e}",
                    context=FileContext(yaml_path),
                    remedy="Check YAML syntax, indentation, and special characters",
                ) from e
            except Exception as e:
                raise ConfigError(
                    issue=f"Failed to load configuration: {e}",
                    context=FileContext(yaml_path),
                    remedy="Verify file permissions and format",
                ) from e

        return merged_config

    def apply_cli_overrides(self, config: DictConfig, **overrides: Any) -> DictConfig:
        """Apply CLI overrides to configuration with dot notation support.

        Args:
            config: Base configuration to override
            **overrides: CLI override values (supports dot notation keys)

        Returns:
            Configuration with CLI overrides applied
        """
        # Convert flat dot-notation keys to nested structure
        override_config = OmegaConf.create({})

        for key, value in overrides.items():
            # Handle dot notation (e.g., "render.quality" -> {"render": {"quality": value}})
            if '.' in key:
                nested_keys = key.split('.')
                current = override_config
                for nested_key in nested_keys[:-1]:
                    if nested_key not in current:
                        current[nested_key] = {}
                    current = current[nested_key]
                current[nested_keys[-1]] = value
            else:
                override_config[key] = value

        # Merge CLI overrides with highest precedence
        return OmegaConf.merge(config, override_config)

    def apply_env_vars(self, config: DictConfig, prefix: str = "AGLOVIZ_") -> DictConfig:
        """Apply environment variable overrides.

        Args:
            config: Base configuration
            prefix: Environment variable prefix (default: "AGLOVIZ_")

        Returns:
            Configuration with environment overrides applied
        """
        env_config = OmegaConf.create({})

        for env_key, env_value in os.environ.items():
            if env_key.startswith(prefix):
                # Convert AGLOVIZ_RENDER_QUALITY to render.quality
                config_key = env_key[len(prefix):].lower().replace('_', '.')

                # Try to parse the value as the appropriate type
                parsed_value = self._parse_env_value(env_value)

                # Set nested value using dot notation
                keys = config_key.split('.')
                current = env_config
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[keys[-1]] = parsed_value

        return OmegaConf.merge(config, env_config)

    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        # Try boolean first
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def validate(self, config: DictConfig) -> VideoConfig:
        """Validate configuration and return typed VideoConfig instance.

        Args:
            config: Configuration to validate

        Returns:
            Validated VideoConfig instance

        Raises:
            ConfigError: If validation fails
        """
        try:
            # Convert OmegaConf to dict for Pydantic validation
            config_dict = OmegaConf.to_container(config, resolve=True)

            # Create VideoConfig instance with validation
            video_config = VideoConfig(**config_dict)

            # Additional cross-field validation
            self._validate_cross_field_constraints(video_config)

            return video_config

        except ValidationError as e:
            # Format Pydantic validation errors with suggestions
            error_messages = []
            suggestions = []

            for error_detail in e.errors():
                field_path = '.'.join(str(loc) for loc in error_detail['loc'])
                error_msg = error_detail['msg']
                error_messages.append(f"  • {field_path}: {error_msg}")

                # Generate suggestions for enum errors
                if 'enum' in error_msg.lower() and 'input should be' in error_msg.lower():
                    import re
                    enum_match = re.search(r"Input should be (.+)", error_msg)
                    if enum_match:
                        suggestions.append(f"Valid options for {field_path}: {enum_match.group(1)}")

            formatted_errors = '\n'.join(error_messages)
            raise ConfigError(
                issue=f"Configuration validation failed:\n{formatted_errors}",
                remedy="Fix the validation errors listed above",
                suggestions=suggestions,
            ) from e
        except Exception as e:
            raise ConfigError(
                issue=f"Unexpected validation error: {e}",
                remedy="Check configuration format and try again",
            ) from e

    def _validate_cross_field_constraints(self, config: VideoConfig) -> None:
        """Perform additional cross-field validation."""
                # Validate start and goal are different
        if (config.scenario and
            config.scenario.start == config.scenario.goal):
            raise ConfigError(
                issue="Start and goal positions must be different",
                remedy="Set different coordinates for start and goal positions",
            )

        # Validate voiceover settings
        if config.voiceover.enabled and config.voiceover.speed <= 0:
            raise ConfigError(
                issue="Voiceover speed must be positive",
                remedy="Set voiceover.speed to a value between 0.1 and 3.0",
            )

        # Validate grid file exists if scenario is provided (do this last)
        if config.scenario and config.scenario.grid_file:
            grid_path = Path(config.scenario.grid_file)
            if not grid_path.exists():
                raise ConfigError(
                    issue=f"Grid file not found: {config.scenario.grid_file}",
                    context=FileContext(config.scenario.grid_file),
                    remedy="Create the grid file or update the grid_file path in your scenario",
                )

    def dump(self, config: VideoConfig, output_path: str) -> None:
        """Dump merged configuration to YAML file for reproducibility.

        Args:
            config: VideoConfig to dump
            output_path: Path to write YAML file
        """
        try:
            # Convert Pydantic model back to dict with mode='python' to handle enums
            config_dict = config.model_dump(mode='python')

            # Create output directory if needed
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Write YAML with nice formatting
            with open(output_file, 'w') as f:
                yaml.dump(
                    config_dict,
                    f,
                    default_flow_style=False,
                    sort_keys=True,
                    indent=2
                )

            console.print(f"✅ Configuration dumped to: [bold blue]{output_path}[/bold blue]")

        except Exception as e:
            raise ConfigError(
                issue=f"Failed to dump configuration: {e}",
                remedy="Check output directory permissions and disk space",
            ) from e

    def load_and_validate(
        self,
        yaml_paths: list[str] | None = None,
        cli_overrides: dict[str, Any] | None = None,
        use_env: bool = True,
    ) -> VideoConfig:
        """Complete configuration loading pipeline.

        Args:
            yaml_paths: List of YAML files to load and merge
            cli_overrides: Dictionary of CLI override values
            use_env: Whether to apply environment variable overrides

        Returns:
            Validated VideoConfig instance
        """
        # Start with empty config if no YAML files provided
        if yaml_paths:
            config = self.load_from_yaml(*yaml_paths)
        else:
            config = OmegaConf.create({})

        # Apply environment variable overrides
        if use_env:
            config = self.apply_env_vars(config)

        # Apply CLI overrides (highest precedence)
        if cli_overrides:
            config = self.apply_cli_overrides(config, **cli_overrides)

        # Validate and return typed configuration
        return self.validate(config)

    def create_sample_configs(self, output_dir: str = "config/samples") -> None:
        """Create sample configuration files for users.

        Args:
            output_dir: Directory to create sample files in
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Sample scenario config
        scenario_config = {
            "scenario": {
                "name": "demo_maze",
                "grid_file": "grids/demo.yaml",
                "start": [0, 0],
                "goal": [9, 9],
                "obstacles": [],
                "weighted": False
            }
        }

        # Sample timing config
        timing_config = {
            "timing": {
                "mode": "normal",
                "ui": 1.0,
                "events": 0.8,
                "effects": 0.5,
                "waits": 0.5
            }
        }

        # Sample theme config
        theme_config = {
            "theme": {
                "name": "custom",
                "colors": {
                    "visited": "#4CAF50",
                    "frontier": "#2196F3",
                    "goal": "#FF9800",
                    "path": "#E91E63",
                    "obstacle": "#424242",
                    "grid": "#E0E0E0"
                }
            }
        }

        # Sample voiceover config
        voiceover_config = {
            "voiceover": {
                "enabled": False,
                "backend": "coqui",
                "lang": "en",
                "voice": "en_US",
                "speed": 1.0
            }
        }

        # Write sample files
        sample_configs = {
            "scenario.yaml": scenario_config,
            "timing.yaml": timing_config,
            "theme.yaml": theme_config,
            "voiceover.yaml": voiceover_config,
        }

        for filename, config in sample_configs.items():
            file_path = output_path / filename
            with open(file_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

        console.print(f"✅ Sample configurations created in: [bold blue]{output_dir}[/bold blue]")
