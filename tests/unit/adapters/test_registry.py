"""Tests for adapter registry."""

import pytest

from agloviz.adapters.registry import AdapterRegistry
from agloviz.config.models import ScenarioConfig


class MockAdapter1:
    """Mock adapter for testing."""
    name = "mock1"

    def run(self, scenario: ScenarioConfig):
        return []


class MockAdapter2:
    """Another mock adapter for testing."""
    name = "mock2"

    def run(self, scenario: ScenarioConfig):
        return []


@pytest.mark.unit
class TestAdapterRegistry:
    """Test AdapterRegistry functionality."""

    def setup_method(self):
        """Clear registry before each test."""
        AdapterRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        AdapterRegistry.clear()

    def test_register_adapter(self):
        """Test registering an adapter."""
        AdapterRegistry.register(MockAdapter1)

        algorithms = AdapterRegistry.list_algorithms()
        assert "mock1" in algorithms

    def test_register_multiple_adapters(self):
        """Test registering multiple adapters."""
        AdapterRegistry.register(MockAdapter1)
        AdapterRegistry.register(MockAdapter2)

        algorithms = AdapterRegistry.list_algorithms()
        assert "mock1" in algorithms
        assert "mock2" in algorithms
        assert len(algorithms) == 2

    def test_get_adapter(self):
        """Test getting registered adapter."""
        AdapterRegistry.register(MockAdapter1)

        adapter_class = AdapterRegistry.get("mock1")
        assert adapter_class == MockAdapter1

    def test_get_nonexistent_adapter(self):
        """Test getting non-existent adapter raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            AdapterRegistry.get("nonexistent")

        assert "not registered" in str(exc_info.value)

    def test_duplicate_registration(self):
        """Test that duplicate registration raises ValueError."""
        AdapterRegistry.register(MockAdapter1)

        with pytest.raises(ValueError) as exc_info:
            AdapterRegistry.register(MockAdapter1)

        assert "already registered" in str(exc_info.value)

    def test_list_algorithms_sorted(self):
        """Test that list_algorithms returns sorted results."""
        AdapterRegistry.register(MockAdapter2)  # Register second first
        AdapterRegistry.register(MockAdapter1)  # Register first second

        algorithms = AdapterRegistry.list_algorithms()
        assert algorithms == ["mock1", "mock2"]  # Should be sorted

    def test_list_algorithms_empty(self):
        """Test list_algorithms with empty registry."""
        algorithms = AdapterRegistry.list_algorithms()
        assert algorithms == []

    def test_clear_registry(self):
        """Test clearing the registry."""
        AdapterRegistry.register(MockAdapter1)
        AdapterRegistry.register(MockAdapter2)

        assert len(AdapterRegistry.list_algorithms()) == 2

        AdapterRegistry.clear()

        assert len(AdapterRegistry.list_algorithms()) == 0
