#!/usr/bin/env python3
"""Test the best approach for our store management."""

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


def test_best_approach():
    """Test the best approach for our use case."""
    print("=== Testing Best Approach ===")
    
    # Clear any existing state
    cs = ConfigStore.instance()
    for group_name in ["renderer", "scenario", "theme", "timing", "scene"]:
        if group_name in cs.repo:
            del cs.repo[group_name]
            print(f"✅ Cleared {group_name} group")
    
    # Approach 1: Create one ZenStore and hold onto it
    print("\n--- Approach 1: Hold onto ZenStore ---")
    zen_store = ZenStore(overwrite_ok=True)
    print(f"Created ZenStore: {id(zen_store)}")
    
    # Register all configs through the same instance
    config = builds(TestConfig, name="test", value=100)
    
    # Renderer configs
    zen_store(config, name="draft", group="renderer")
    zen_store(config, name="medium", group="renderer")
    zen_store(config, name="hd", group="renderer")
    print("✅ Registered renderer configs")
    
    # Scenario configs
    zen_store(config, name="maze_small", group="scenario")
    zen_store(config, name="maze_large", group="scenario")
    print("✅ Registered scenario configs")
    
    # Test overwriting
    print("\n--- Testing Overwriting ---")
    try:
        new_config = builds(TestConfig, name="new_test", value=999)
        zen_store(new_config, name="draft", group="renderer")  # Overwrite
        print("✅ Overwrite successful")
    except Exception as e:
        print(f"❌ Overwrite failed: {e}")
    
    # Test re-initialization
    print("\n--- Testing Re-initialization ---")
    try:
        # Clear and re-register
        for group_name in ["renderer", "scenario"]:
            if group_name in cs.repo:
                del cs.repo[group_name]
        
        # Re-register with same ZenStore
        zen_store(config, name="draft", group="renderer")
        zen_store(config, name="maze_small", group="scenario")
        print("✅ Re-initialization successful")
    except Exception as e:
        print(f"❌ Re-initialization failed: {e}")
    
    # Check final state
    print("\n--- Final State ---")
    for group_name in ["renderer", "scenario"]:
        if group_name in cs.repo:
            group = cs.repo[group_name]
            print(f"✅ {group_name}: {len(group)} configs")
        else:
            print(f"❌ {group_name}: not found")


def test_store_manager_with_zenstore():
    """Test how our StoreManager should work with ZenStore."""
    print("\n=== StoreManager with ZenStore ===")
    
    class ZenStoreManager:
        """Store manager that holds onto a ZenStore instance."""
        
        _initialized = False
        _zen_store = None
        
        @classmethod
        def setup_store(cls, force=False):
            """Setup store using a held ZenStore instance."""
            if cls._initialized and not force:
                print("Store already initialized, skipping")
                return
            
            # Create and hold ZenStore
            cls._zen_store = ZenStore(overwrite_ok=True)
            print(f"✅ Created ZenStore: {id(cls._zen_store)}")
            
            # Register all configs
            cls._register_all_configs()
            
            cls._initialized = True
            print("✅ Store setup completed")
        
        @classmethod
        def _register_all_configs(cls):
            """Register all configurations using our held ZenStore."""
            config = builds(TestConfig, name="test", value=100)
            
            # Register all configs through the same ZenStore
            cls._zen_store(config, name="draft", group="renderer")
            cls._zen_store(config, name="medium", group="renderer")
            cls._zen_store(config, name="hd", group="renderer")
            
            cls._zen_store(config, name="maze_small", group="scenario")
            cls._zen_store(config, name="maze_large", group="scenario")
            
            cls._zen_store(config, name="default", group="theme")
            cls._zen_store(config, name="dark", group="theme")
            
            cls._zen_store(config, name="draft", group="timing")
            cls._zen_store(config, name="normal", group="timing")
            cls._zen_store(config, name="fast", group="timing")
            
            cls._zen_store(config, name="bfs_basic", group="scene")
            cls._zen_store(config, name="bfs_advanced", group="scene")
            
            print("✅ Registered all configs through held ZenStore")
        
        @classmethod
        def is_initialized(cls):
            return cls._initialized
        
        @classmethod
        def get_zen_store(cls):
            return cls._zen_store
    
    # Test the manager
    manager = ZenStoreManager()
    manager.setup_store()
    print(f"Manager initialized: {manager.is_initialized()}")
    print(f"ZenStore ID: {id(manager.get_zen_store())}")
    
    # Test re-initialization
    manager.setup_store(force=True)
    print(f"Manager re-initialized: {manager.is_initialized()}")
    print(f"ZenStore ID after re-init: {id(manager.get_zen_store())}")
    print(f"Same ZenStore instance? {id(manager.get_zen_store()) == id(manager.get_zen_store())}")


if __name__ == "__main__":
    test_best_approach()
    test_store_manager_with_zenstore()
    
    print("\n🎯 Best Approach:")
    print("1. Create ONE ZenStore(overwrite_ok=True) instance")
    print("2. Hold onto it in our StoreManager")
    print("3. Use the same instance for all registrations")
    print("4. This allows proper overwriting and re-initialization")
    print("5. Much more efficient than creating new instances each time")
