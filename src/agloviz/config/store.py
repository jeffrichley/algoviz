"""Simple Hydra-zen store setup for ALGOViz.

Just register configs and add to hydra store - that's it!
"""

from hydra_zen import store

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


def register_all_configs():
    """Register all hydra-zen configurations - simple and clean."""

    # Renderer configurations
    renderer_store = store(group="renderer", overwrite_ok=True)
    renderer_store(DraftRenderer, name="draft")
    renderer_store(MediumRenderer, name="medium")
    renderer_store(HDRenderer, name="hd")

    # Scenario configurations
    scenario_store = store(group="scenario", overwrite_ok=True)
    scenario_store(MazeSmallConfig, name="maze_small")
    scenario_store(MazeLargeConfig, name="maze_large")
    scenario_store(WeightedGraphConfig, name="weighted_graph")

    # Theme configurations
    theme_store = store(group="theme", overwrite_ok=True)
    theme_store(DefaultThemeConfig, name="default")
    theme_store(DarkThemeConfig, name="dark")
    theme_store(HighContrastThemeConfig, name="high_contrast")

    # Timing configurations
    timing_store = store(group="timing", overwrite_ok=True)
    timing_store(DraftTimingConfig, name="draft")
    timing_store(NormalTimingConfig, name="normal")
    timing_store(FastTimingConfig, name="fast")

    # Scene configurations
    scene_store = store(group="scene", overwrite_ok=True)
    scene_store(BFSBasicSceneConfig, name="bfs_basic")
    scene_store(BFSAdvancedSceneConfig, name="bfs_advanced")

    # Director configurations
    director_store = store(group="director", overwrite_ok=True)
    director_store(DirectorConfigZen, name="base")


def setup_store():
    """Setup hydra-zen store using the new StoreManager (recommended)."""
    from .store_manager import StoreManager
    StoreManager.setup_store()
    return StoreManager.get_zen_store()


# Legacy function for backward compatibility
def register_all_configs():
    """Legacy function - use StoreManager.setup_store() instead."""
    import warnings
    warnings.warn(
        "register_all_configs() is deprecated. Use StoreManager.setup_store() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    from .store_manager import StoreManager
    StoreManager.setup_store()
