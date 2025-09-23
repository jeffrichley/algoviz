"""Centralized store management following Google's engineering principles.

This module provides explicit, testable store initialization with clear
state management and defensive programming practices.
"""

import logging
from typing import Any

from hydra_zen import ZenStore

logger = logging.getLogger(__name__)


class StoreManager:
    """Centralized store manager with explicit state tracking.

    Follows Google's principles:
    - Explicit initialization (no magic)
    - Clear error messages
    - Testable and mockable
    - Thread-safe operations
    - Uses single ZenStore instance for efficiency
    """

    _initialized: bool = False
    _zen_store: ZenStore | None = None
    _registered_groups: dict[str, Any] = {}
    _initialization_error: Exception | None = None

    @classmethod
    def setup_store(cls, force: bool = False) -> None:
        """Initialize the store with explicit state management.

        Args:
            force: If True, reinitialize even if already initialized

        Raises:
            RuntimeError: If initialization fails
        """
        if cls._initialized and not force:
            logger.debug("Store already initialized, skipping")
            return

        try:
            logger.info("Initializing hydra-zen store...")

            # Create and hold onto a ZenStore instance with overwrite_ok=True
            cls._zen_store = ZenStore(overwrite_ok=True)
            logger.debug(f"Created ZenStore instance: {id(cls._zen_store)}")

            # Register all configs using our held ZenStore
            cls._register_all_configs()

            # Track what we've registered
            cls._registered_groups = {
                "renderer": True,
                "scenario": True,
                "theme": True,
                "timing": True,
                "scene": True,
                "director": True,
            }

            cls._initialized = True
            cls._initialization_error = None
            logger.info("Store initialization completed successfully")

        except Exception as e:
            cls._initialization_error = e
            logger.error(f"Store initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize store: {e}") from e

    @classmethod
    def _register_all_configs(cls) -> None:
        """Register all configurations using our held ZenStore instance."""
        if cls._zen_store is None:
            raise RuntimeError("ZenStore not initialized")

        # Import here to avoid circular imports
        from .hydra_zen import (
            BFSAdvancedSceneConfig,
            # Scene configs
            BFSBasicSceneConfig,
            DarkThemeConfig,
            # Theme configs
            DefaultThemeConfig,
            # Director configs
            DirectorConfigZen,
            # Renderer configs
            DraftRenderer,
            # Timing configs
            DraftTimingConfig,
            FastTimingConfig,
            HDRenderer,
            HighContrastThemeConfig,
            MazeLargeConfig,
            # Scenario configs
            MazeSmallConfig,
            MediumRenderer,
            NormalTimingConfig,
            WeightedGraphConfig,
        )

        # Register all configs through our held ZenStore
        # Renderer configurations
        cls._zen_store(DraftRenderer, name="draft", group="renderer")
        cls._zen_store(MediumRenderer, name="medium", group="renderer")
        cls._zen_store(HDRenderer, name="hd", group="renderer")

        # Scenario configurations
        cls._zen_store(MazeSmallConfig, name="maze_small", group="scenario")
        cls._zen_store(MazeLargeConfig, name="maze_large", group="scenario")
        cls._zen_store(WeightedGraphConfig, name="weighted_graph", group="scenario")

        # Theme configurations
        cls._zen_store(DefaultThemeConfig, name="default", group="theme")
        cls._zen_store(DarkThemeConfig, name="dark", group="theme")
        cls._zen_store(HighContrastThemeConfig, name="high_contrast", group="theme")

        # Timing configurations
        cls._zen_store(DraftTimingConfig, name="draft", group="timing")
        cls._zen_store(NormalTimingConfig, name="normal", group="timing")
        cls._zen_store(FastTimingConfig, name="fast", group="timing")

        # Scene configurations
        cls._zen_store(BFSBasicSceneConfig, name="bfs_basic", group="scene")
        cls._zen_store(BFSAdvancedSceneConfig, name="bfs_advanced", group="scene")

        # Director configurations
        cls._zen_store(DirectorConfigZen, name="base", group="director")

        # Add to Hydra store
        cls._zen_store.add_to_hydra_store()

        logger.debug(
            "All configurations registered through ZenStore and added to Hydra store"
        )

    @classmethod
    def reset_for_testing(cls) -> None:
        """Reset store state for testing.

        Google's approach: Simple state reset, rely on overwrite_ok=True for actual cleanup.
        """
        # Just reset our tracking state
        cls._initialized = False
        cls._zen_store = None
        cls._registered_groups = {}
        cls._initialization_error = None
        logger.debug("Store state reset for testing")

    @classmethod
    def setup_store_for_testing(cls) -> None:
        """Setup store specifically for testing with clean state.

        Google's approach: Just setup the store, rely on overwrite_ok=True.
        """
        cls.setup_store(force=True)

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if store is initialized.

        Returns:
            True if store is initialized and ready to use
        """
        return cls._initialized and cls._initialization_error is None

    @classmethod
    def get_initialization_error(cls) -> Exception | None:
        """Get the last initialization error.

        Returns:
            The last initialization error, or None if no error
        """
        return cls._initialization_error

    @classmethod
    def get_registered_groups(cls) -> dict[str, Any]:
        """Get list of registered groups (for debugging).

        Returns:
            Dictionary of registered group names
        """
        return cls._registered_groups.copy()

    @classmethod
    def get_zen_store(cls) -> ZenStore | None:
        """Get the ZenStore instance.

        Returns:
            The ZenStore instance, or None if not initialized
        """
        return cls._zen_store
