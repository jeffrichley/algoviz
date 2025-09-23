"""Builder management for ALGOViz system."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class BuilderManager:
    """Manages scene builders and YAML config loading."""

    def __init__(self):
        self._builders_initialized = False
        self._yaml_configs: dict[str, Any] = {}
        self._initialization_error: Exception | None = None

    def initialize_builders(self, force: bool = False) -> None:
        """Initialize all builders and load YAML configs.
        
        Args:
            force: If True, re-initialize even if already initialized
            
        Raises:
            RuntimeError: If initialization fails
        """
        if self._builders_initialized and not force:
            logger.debug("Builders already initialized, skipping")
            return

        try:
            logger.info("Initializing builders and loading YAML configs...")

            # Load YAML configs
            self._load_yaml_configs()

            # Initialize any additional builders
            self._initialize_scene_builders()

            self._builders_initialized = True
            self._initialization_error = None
            logger.info("Builder initialization completed successfully")

        except Exception as e:
            self._initialization_error = e
            logger.error(f"Builder initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize builders: {e}") from e

    def _load_yaml_configs(self) -> None:
        """Load all YAML configuration files."""
        from omegaconf import OmegaConf

        # Define YAML config paths
        yaml_config_paths = [
            "configs/scene/bfs_pathfinding.yaml",
            "configs/scene/bfs_dynamic.yaml",
        ]

        for config_path in yaml_config_paths:
            try:
                if Path(config_path).exists():
                    config = OmegaConf.load(config_path)
                    config_name = Path(config_path).stem
                    self._yaml_configs[config_name] = config
                    logger.debug(f"Loaded YAML config: {config_name}")
                else:
                    logger.warning(f"YAML config not found: {config_path}")
            except Exception as e:
                logger.error(f"Failed to load YAML config {config_path}: {e}")
                raise

    def _initialize_scene_builders(self) -> None:
        """Initialize scene builders."""
        # This is where you'd initialize any custom scene builders
        # For now, we just track that it's done
        logger.debug("Scene builders initialized")

    def get_yaml_config(self, name: str) -> Any | None:
        """Get a YAML config by name."""
        return self._yaml_configs.get(name)

    def get_all_yaml_configs(self) -> dict[str, Any]:
        """Get all loaded YAML configs."""
        return self._yaml_configs.copy()

    def is_initialized(self) -> bool:
        """Check if builders are initialized."""
        return self._builders_initialized

    def reset_for_testing(self) -> None:
        """Reset builder state for testing."""
        self._builders_initialized = False
        self._yaml_configs = {}
        self._initialization_error = None
        logger.debug("Builder state reset for testing")

    def get_initialization_error(self) -> Exception | None:
        """Get initialization error if any."""
        return self._initialization_error
