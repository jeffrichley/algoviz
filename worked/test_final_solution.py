#!/usr/bin/env python3
"""Final solution demonstration for hydra-zen store management."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from hydra_zen import store, builds, ZenStore
from hydra.core.config_store import ConfigStore
from dataclasses import dataclass


@dataclass
class TestConfig:
    name: str
    value: int = 42


def demonstrate_correct_approach():
    """Demonstrate the correct approach for our use case."""
    print("=== Correct Approach for Our Use Case ===")
    
    # Clear any existing state
    cs = ConfigStore.instance()
    for group_name in ["renderer", "scenario", "theme", "timing", "scene"]:
        if group_name in cs.repo:
            del cs.repo[group_name]
            print(f"✅ Cleared {group_name} group")
    
    # Create a ZenStore with overwrite_ok=True
    zen_store = ZenStore(overwrite_ok=True)
    print(f"✅ Created ZenStore with overwrite_ok=True")
    
    # Register all our configs
    print("\n--- Registering Configs ---")
    
    # Renderer configs
    renderer_config = builds(TestConfig, name="renderer", value=1)
    zen_store(renderer_config, name="draft", group="renderer")
    zen_store(renderer_config, name="medium", group="renderer")
    zen_store(renderer_config, name="hd", group="renderer")
    print("✅ Registered renderer configs")
    
    # Scenario configs
    scenario_config = builds(TestConfig, name="scenario", value=2)
    zen_store(scenario_config, name="maze_small", group="scenario")
    zen_store(scenario_config, name="maze_large", group="scenario")
    print("✅ Registered scenario configs")
    
    # Theme configs
    theme_config = builds(TestConfig, name="theme", value=3)
    zen_store(theme_config, name="default", group="theme")
    zen_store(theme_config, name="dark", group="theme")
    print("✅ Registered theme configs")
    
    # Timing configs
    timing_config = builds(TestConfig, name="timing", value=4)
    zen_store(timing_config, name="draft", group="timing")
    zen_store(timing_config, name="normal", group="timing")
    zen_store(timing_config, name="fast", group="timing")
    print("✅ Registered timing configs")
    
    # Scene configs
    scene_config = builds(TestConfig, name="scene", value=5)
    zen_store(scene_config, name="bfs_basic", group="scene")
    zen_store(scene_config, name="bfs_advanced", group="scene")
    print("✅ Registered scene configs")
    
    # Test overwriting
    print("\n--- Testing Overwriting ---")
    try:
        # Try to overwrite a config
        new_renderer_config = builds(TestConfig, name="new_renderer", value=999)
        zen_store(new_renderer_config, name="draft", group="renderer")
        print("✅ Successfully overwrote renderer config")
    except Exception as e:
        print(f"❌ Overwrite failed: {e}")
    
    # Check final state
    print("\n--- Final Store State ---")
    for group_name in ["renderer", "scenario", "theme", "timing", "scene"]:
        if group_name in cs.repo:
            group = cs.repo[group_name]
            print(f"✅ {group_name}: {len(group)} configs")
        else:
            print(f"❌ {group_name}: not found")


def demonstrate_store_manager_pattern():
    """Demonstrate how our StoreManager should work."""
    print("\n=== StoreManager Pattern ===")
    
    class SimpleStoreManager:
        """Simplified store manager using the correct approach."""
        
        _initialized = False
        _zen_store = None
        
        @classmethod
        def setup_store(cls, force=False):
            """Setup store using ZenStore with overwrite_ok=True."""
            if cls._initialized and not force:
                print("Store already initialized, skipping")
                return
            
            # Create ZenStore with overwrite_ok=True
            cls._zen_store = ZenStore(overwrite_ok=True)
            print("✅ Created ZenStore with overwrite_ok=True")
            
            # Register all configs
            cls._register_all_configs()
            
            cls._initialized = True
            print("✅ Store setup completed")
        
        @classmethod
        def _register_all_configs(cls):
            """Register all configurations."""
            # This would call our actual register_all_configs function
            # but using the zen_store instead of individual stores
            pass
        
        @classmethod
        def is_initialized(cls):
            return cls._initialized
    
    # Test the pattern
    manager = SimpleStoreManager()
    manager.setup_store()
    print(f"Manager initialized: {manager.is_initialized()}")
    
    # Test re-initialization
    manager.setup_store(force=True)
    print(f"Manager re-initialized: {manager.is_initialized()}")


if __name__ == "__main__":
    demonstrate_correct_approach()
    demonstrate_store_manager_pattern()
    
    print("\n🎯 Final Solution:")
    print("1. Use ZenStore(overwrite_ok=True) instead of store(overwrite_ok=True)")
    print("2. Register all configs through the same ZenStore instance")
    print("3. This allows proper overwriting and re-initialization")
    print("4. Our StoreManager should create one ZenStore and use it for all registrations")
