"""Unit tests for ComponentRegistry.

Tests widget registry operations, factory patterns, and error handling
following project testing standards.
"""

import pytest

from agloviz.core.errors import RegistryError
from agloviz.widgets.registry import ComponentRegistry


class MockWidget:
    """Mock widget for testing that implements Widget protocol."""

    def show(self, scene, **kwargs):
        pass

    def update(self, scene, event, run_time):
        pass

    def hide(self, scene):
        pass


@pytest.mark.unit
class TestComponentRegistry:
    """Test suite for ComponentRegistry functionality."""

    def test_register_widget_factory(self):
        """Test registering a widget factory."""
        registry = ComponentRegistry()
        registry.register("test", lambda: MockWidget())
        assert "test" in registry.list_widgets()

    def test_get_widget_creates_fresh_instance(self):
        """Test that get() creates fresh widget instances."""
        registry = ComponentRegistry()
        registry.register("test", lambda: MockWidget())

        widget1 = registry.get("test")
        widget2 = registry.get("test")
        assert widget1 is not widget2  # Fresh instances
        assert isinstance(widget1, MockWidget)
        assert isinstance(widget2, MockWidget)

    def test_collision_detection(self):
        """Test that registering duplicate names raises RegistryError."""
        registry = ComponentRegistry()
        registry.register("test", lambda: MockWidget())

        with pytest.raises(RegistryError) as exc_info:
            registry.register("test", lambda: MockWidget())

        assert "already registered" in str(exc_info.value)

    def test_missing_widget_error_with_suggestions(self):
        """Test that missing widgets provide helpful error messages."""
        registry = ComponentRegistry()
        registry.register("test_grid", lambda: MockWidget())
        registry.register("test_queue", lambda: MockWidget())

        with pytest.raises(RegistryError) as exc_info:
            registry.get("gird")  # Typo in 'grid'

        error = exc_info.value
        assert "not registered" in str(error)
        # Error should have available options in metadata
        available_options = error.metadata["available_options"]
        assert "grid" in available_options  # Hydra-zen widget
        assert "queue" in available_options  # Hydra-zen widget
        assert "test_grid" in available_options  # Legacy widget
        assert "test_queue" in available_options  # Legacy widget

    def test_list_widgets_returns_sorted(self):
        """Test that list_widgets returns sorted widget names."""
        registry = ComponentRegistry()
        registry.register("zebra", lambda: MockWidget())
        registry.register("apple", lambda: MockWidget())
        registry.register("banana", lambda: MockWidget())

        widgets = registry.list_widgets()
        # Should include both legacy and hydra-zen widgets, sorted
        expected_widgets = ["apple", "banana", "grid", "queue", "zebra"]
        assert widgets == expected_widgets

    def test_clear_removes_all_widgets(self):
        """Test that clear() removes all registered widgets."""
        registry = ComponentRegistry()
        registry.register("test1", lambda: MockWidget())
        registry.register("test2", lambda: MockWidget())

        # Should have legacy widgets + hydra-zen widgets
        assert len(registry.list_widgets()) == 4  # test1, test2, grid, queue

        registry.clear()
        # After clear, should only have hydra-zen widgets (ConfigStore not cleared)
        assert len(registry.list_widgets()) == 2  # grid, queue

    def test_empty_registry_behavior(self):
        """Test behavior with empty registry."""
        registry = ComponentRegistry()

        # Should have hydra-zen widgets automatically registered
        widgets = registry.list_widgets()
        assert "grid" in widgets
        assert "queue" in widgets

        with pytest.raises(RegistryError) as exc_info:
            registry.get("nonexistent")

        assert "not registered" in str(exc_info.value)

    def test_widget_factory_error_handling(self):
        """Test handling of factory function errors."""
        registry = ComponentRegistry()

        def failing_factory():
            raise ValueError("Factory failed")

        registry.register("failing", failing_factory)

        with pytest.raises(ValueError, match="Factory failed"):
            registry.get("failing")

    def test_registry_isolation(self):
        """Test that multiple registry instances are isolated."""
        registry1 = ComponentRegistry()
        registry2 = ComponentRegistry()

        registry1.register("test", lambda: MockWidget())

        assert "test" in registry1.list_widgets()
        assert "test" not in registry2.list_widgets()

    def test_widget_protocol_compliance(self):
        """Test that registered widgets implement the Widget protocol."""
        registry = ComponentRegistry()
        registry.register("mock", lambda: MockWidget())

        widget = registry.get("mock")

        # Verify protocol methods exist
        assert hasattr(widget, "show")
        assert hasattr(widget, "update")
        assert hasattr(widget, "hide")
        assert callable(widget.show)
        assert callable(widget.update)
        assert callable(widget.hide)
