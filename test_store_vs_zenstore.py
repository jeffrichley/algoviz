#!/usr/bin/env python3
"""Test the relationship between store() and ZenStore."""

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


def test_store_vs_zenstore_relationship():
    """Test the relationship between store() and ZenStore."""
    print("=== Testing store() vs ZenStore Relationship ===")
    
    # Test 1: Check if store() returns a ZenStore
    print("\n--- Test 1: What does store() return? ---")
    store_instance = store(group="test_group")
    print(f"store() returns: {type(store_instance)}")
    print(f"Is it a ZenStore? {isinstance(store_instance, ZenStore)}")
    print(f"Has _overwrite_ok attribute? {hasattr(store_instance, '_overwrite_ok')}")
    if hasattr(store_instance, '_overwrite_ok'):
        print(f"_overwrite_ok value: {store_instance._overwrite_ok}")
    
    # Test 2: Check ZenStore directly
    print("\n--- Test 2: ZenStore directly ---")
    zen_store = ZenStore(overwrite_ok=True)
    print(f"ZenStore type: {type(zen_store)}")
    print(f"Has _overwrite_ok attribute? {hasattr(zen_store, '_overwrite_ok')}")
    if hasattr(zen_store, '_overwrite_ok'):
        print(f"_overwrite_ok value: {zen_store._overwrite_ok}")
    
    # Test 3: Check if they're the same class
    print("\n--- Test 3: Are they the same class? ---")
    print(f"store() class: {store_instance.__class__}")
    print(f"ZenStore class: {zen_store.__class__}")
    print(f"Same class? {store_instance.__class__ == zen_store.__class__}")
    print(f"store() is subclass of ZenStore? {issubclass(store_instance.__class__, ZenStore)}")
    
    # Test 4: Check the store() function source
    print("\n--- Test 4: Check store() function ---")
    import inspect
    try:
        source = inspect.getsource(store)
        print("store() function source:")
        print(source[:200] + "..." if len(source) > 200 else source)
    except Exception as e:
        print(f"Could not get source: {e}")
    
    # Test 5: Check if store() creates a new instance each time
    print("\n--- Test 5: Does store() create new instances? ---")
    store1 = store(group="test1")
    store2 = store(group="test2")
    print(f"store1 id: {id(store1)}")
    print(f"store2 id: {id(store2)}")
    print(f"Different instances? {id(store1) != id(store2)}")
    
    # Test 6: Check if store() for same group returns same instance
    print("\n--- Test 6: Same group, same instance? ---")
    store3 = store(group="test1")
    print(f"store1 id: {id(store1)}")
    print(f"store3 id: {id(store3)}")
    print(f"Same instance for same group? {id(store1) == id(store3)}")


def test_holding_zenstore():
    """Test whether we should hold onto ZenStore instances."""
    print("\n=== Testing Holding ZenStore Instances ===")
    
    # Test 1: Create and hold ZenStore
    print("\n--- Test 1: Hold ZenStore instance ---")
    zen_store = ZenStore(overwrite_ok=True)
    print(f"Created ZenStore: {id(zen_store)}")
    
    # Register some configs
    config1 = builds(TestConfig, name="config1", value=100)
    config2 = builds(TestConfig, name="config2", value=200)
    
    zen_store(config1, name="test1", group="hold_test")
    zen_store(config2, name="test2", group="hold_test")
    print("✅ Registered configs with held ZenStore")
    
    # Test 2: Try to overwrite with same instance
    print("\n--- Test 2: Overwrite with same instance ---")
    try:
        config3 = builds(TestConfig, name="config3", value=300)
        zen_store(config3, name="test1", group="hold_test")  # Overwrite test1
        print("✅ Overwrite successful with same instance")
    except Exception as e:
        print(f"❌ Overwrite failed: {e}")
    
    # Test 3: Create new ZenStore for same group
    print("\n--- Test 3: New ZenStore for same group ---")
    try:
        zen_store2 = ZenStore(overwrite_ok=True)
        config4 = builds(TestConfig, name="config4", value=400)
        zen_store2(config4, name="test1", group="hold_test")  # Overwrite test1
        print("✅ Overwrite successful with new ZenStore")
    except Exception as e:
        print(f"❌ Overwrite failed: {e}")
    
    # Test 4: Check final state
    print("\n--- Test 4: Check final state ---")
    cs = ConfigStore.instance()
    if "hold_test" in cs.repo:
        group = cs.repo["hold_test"]
        print(f"Final configs in hold_test: {len(group)}")
        for name, node in group.items():
            print(f"  - {name}: {node}")
    else:
        print("❌ hold_test group not found")


def test_store_function_behavior():
    """Test the behavior of the store() function."""
    print("\n=== Testing store() Function Behavior ===")
    
    # Test 1: Check if store() accepts overwrite_ok
    print("\n--- Test 1: Does store() accept overwrite_ok? ---")
    try:
        store_with_overwrite = store(group="test", overwrite_ok=True)
        print(f"✅ store() accepted overwrite_ok=True")
        print(f"Result type: {type(store_with_overwrite)}")
        if hasattr(store_with_overwrite, '_overwrite_ok'):
            print(f"_overwrite_ok: {store_with_overwrite._overwrite_ok}")
    except Exception as e:
        print(f"❌ store() rejected overwrite_ok=True: {e}")
    
    # Test 2: Check store() function signature
    print("\n--- Test 2: store() function signature ---")
    import inspect
    sig = inspect.signature(store)
    print(f"store() signature: {sig}")
    
    # Test 3: Check if store() is a factory function
    print("\n--- Test 3: Is store() a factory function? ---")
    print(f"store function: {store}")
    print(f"store type: {type(store)}")
    
    # Test 4: Try to call store() with different arguments
    print("\n--- Test 4: Try different store() calls ---")
    try:
        # Try with just group
        store1 = store(group="test1")
        print(f"✅ store(group='test1'): {type(store1)}")
    except Exception as e:
        print(f"❌ store(group='test1') failed: {e}")
    
    try:
        # Try with overwrite_ok
        store2 = store(overwrite_ok=True)
        print(f"✅ store(overwrite_ok=True): {type(store2)}")
    except Exception as e:
        print(f"❌ store(overwrite_ok=True) failed: {e}")


if __name__ == "__main__":
    test_store_vs_zenstore_relationship()
    test_holding_zenstore()
    test_store_function_behavior()
    
    print("\n🎯 Key Questions:")
    print("1. Does store() use ZenStore under the hood?")
    print("2. Should we hold onto ZenStore instances?")
    print("3. What's the difference between store() and ZenStore?")
