#!/usr/bin/env python3
"""Standalone script to understand hydra-zen store behavior.

This script demonstrates how hydra-zen stores work, including:
- Basic store creation and registration
- Overwrite behavior
- Multiple store creation patterns
- Store isolation and cleanup

Run this to understand the proper patterns before implementing in our codebase.
"""

import sys
from pathlib import Path

# Add our src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from hydra_zen import store, builds, instantiate
from hydra.core.config_store import ConfigStore
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TestConfig:
    """Simple test configuration."""
    name: str
    value: int = 42


def test_basic_store_creation():
    """Test 1: Basic store creation and registration."""
    print("=== Test 1: Basic Store Creation ===")
    
    # Create a store
    test_store = store(group="test1")
    
    # Create a config builder
    TestConfigBuilder = builds(TestConfig, name="test_config", value=100)
    
    # Register the config
    test_store(TestConfigBuilder, name="my_config")
    
    # Instantiate from store
    config = instantiate(TestConfigBuilder)
    print(f"✅ Created config: {config}")
    
    # Check what's in the global store
    cs = ConfigStore.instance()
    if "test1" in cs.repo:
        print(f"✅ Store 'test1' exists with {len(cs.repo['test1'])} configs")
    else:
        print("❌ Store 'test1' not found")


def test_overwrite_behavior():
    """Test 2: Overwrite behavior patterns."""
    print("\n=== Test 2: Overwrite Behavior ===")
    
    # Test 2a: Store without overwrite_ok
    print("\n--- Test 2a: Store without overwrite_ok ---")
    try:
        store1 = store(group="test2a")
        config1 = builds(TestConfig, name="config1")
        store1(config1, name="test")
        print("✅ First registration successful")
        
        # Try to register again
        store1(config1, name="test")
        print("❌ Second registration should have failed!")
    except ValueError as e:
        print(f"✅ Second registration failed as expected: {e}")
    
    # Test 2b: Store with overwrite_ok=True
    print("\n--- Test 2b: Store with overwrite_ok=True ---")
    try:
        store2 = store(group="test2b", overwrite_ok=True)
        config2 = builds(TestConfig, name="config2")
        store2(config2, name="test")
        print("✅ First registration successful")
        
        # Try to register again
        store2(config2, name="test")
        print("✅ Second registration successful (overwrite_ok=True)")
    except ValueError as e:
        print(f"❌ Second registration failed: {e}")
    
    # Test 2c: Individual registration with overwrite_ok
    print("\n--- Test 2c: Individual registration with overwrite_ok ---")
    try:
        store3 = store(group="test2c")
        config3 = builds(TestConfig, name="config3")
        store3(config3, name="test")
        print("✅ First registration successful")
        
        # Try to register again with overwrite_ok=True
        store3(config3, name="test", overwrite_ok=True)
        print("✅ Second registration successful (individual overwrite_ok=True)")
    except ValueError as e:
        print(f"❌ Second registration failed: {e}")


def test_store_isolation():
    """Test 3: Store isolation and cleanup."""
    print("\n=== Test 3: Store Isolation ===")
    
    # Test 3a: Different groups are isolated
    print("\n--- Test 3a: Different groups are isolated ---")
    store_a = store(group="group_a")
    store_b = store(group="group_b")
    
    config_a = builds(TestConfig, name="config_a")
    config_b = builds(TestConfig, name="config_b")
    
    store_a(config_a, name="same_name")
    store_b(config_b, name="same_name")  # Same name, different group
    print("✅ Same name in different groups works")
    
    # Test 3b: Check global store state
    print("\n--- Test 3b: Global store state ---")
    cs = ConfigStore.instance()
    print(f"Global store has {len(cs.repo)} groups:")
    for group_name in cs.repo.keys():
        group = cs.repo[group_name]
        if hasattr(group, '__len__'):
            print(f"  - {group_name}: {len(group)} configs")
        else:
            print(f"  - {group_name}: {type(group)} (no len)")


def test_store_cleanup_attempts():
    """Test 4: Attempts to clean up stores."""
    print("\n=== Test 4: Store Cleanup Attempts ===")
    
    # Test 4a: Try to clear a group
    print("\n--- Test 4a: Try to clear a group ---")
    cs = ConfigStore.instance()
    if "test1" in cs.repo:
        group = cs.repo["test1"]
        if hasattr(group, '__len__'):
            print(f"Before: test1 has {len(group)} configs")
        else:
            print(f"Before: test1 has {type(group)}")
        del cs.repo["test1"]
        print("✅ Deleted test1 group")
        
        # Try to recreate
        store_cleanup = store(group="test1", overwrite_ok=True)
        config_cleanup = builds(TestConfig, name="cleanup_test")
        store_cleanup(config_cleanup, name="cleanup")
        print("✅ Recreated test1 group")
    else:
        print("❌ test1 group not found")


def test_multiple_store_creation_patterns():
    """Test 5: Different patterns for creating multiple stores."""
    print("\n=== Test 5: Multiple Store Creation Patterns ===")
    
    # Pattern 1: Create stores individually
    print("\n--- Pattern 1: Individual store creation ---")
    try:
        store_p1a = store(group="pattern1", overwrite_ok=True)
        store_p1b = store(group="pattern1", overwrite_ok=True)  # Same group
        print("✅ Created two stores for same group")
    except Exception as e:
        print(f"❌ Failed to create two stores for same group: {e}")
    
    # Pattern 2: Create stores with different overwrite settings
    print("\n--- Pattern 2: Different overwrite settings ---")
    try:
        store_p2a = store(group="pattern2")  # No overwrite
        store_p2b = store(group="pattern2", overwrite_ok=True)  # With overwrite
        print("✅ Created stores with different overwrite settings")
    except Exception as e:
        print(f"❌ Failed to create stores with different overwrite settings: {e}")


def test_our_actual_configs():
    """Test 6: Test with our actual configuration classes."""
    print("\n=== Test 6: Our Actual Configurations ===")
    
    try:
        # Import our actual configs
        from agloviz.config.models import ScenarioConfig, ThemeConfig, TimingConfig, TimingMode
        
        # Create a store for our configs
        our_store = store(group="our_test", overwrite_ok=True)
        
        # Create builders for our configs
        ScenarioBuilder = builds(ScenarioConfig, name="test_scenario", obstacles=[(1, 1)])
        ThemeBuilder = builds(ThemeConfig, name="test_theme")
        TimingBuilder = builds(TimingConfig, mode=TimingMode.NORMAL)
        
        # Register them
        our_store(ScenarioBuilder, name="scenario")
        our_store(ThemeBuilder, name="theme")
        our_store(TimingBuilder, name="timing")
        
        print("✅ Registered our actual configs successfully")
        
        # Test instantiation
        scenario = instantiate(ScenarioBuilder)
        theme = instantiate(ThemeBuilder)
        timing = instantiate(TimingBuilder)
        
        print(f"✅ Instantiated scenario: {scenario.name}")
        print(f"✅ Instantiated theme: {theme.name}")
        print(f"✅ Instantiated timing: {timing.mode}")
        
    except Exception as e:
        print(f"❌ Failed to test our actual configs: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests to understand hydra-zen store behavior."""
    print("🧪 Testing Hydra-zen Store Behavior")
    print("=" * 50)
    
    test_basic_store_creation()
    test_overwrite_behavior()
    test_store_isolation()
    test_store_cleanup_attempts()
    test_multiple_store_creation_patterns()
    test_our_actual_configs()
    
    print("\n" + "=" * 50)
    print("🎯 Key Insights:")
    print("1. Stores are global singletons per group")
    print("2. overwrite_ok=True must be set on store() creation")
    print("3. Individual overwrite_ok=True on registrations doesn't work")
    print("4. Different groups are isolated")
    print("5. Store cleanup requires deleting from global ConfigStore")
    print("\n💡 Recommendation: Always use overwrite_ok=True for development/testing")


if __name__ == "__main__":
    main()
