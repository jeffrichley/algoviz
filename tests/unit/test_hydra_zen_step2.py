"""Unit tests for STEP 2: Hydra-zen Store Registration.

Tests the hydra-zen store registration system created in src/agloviz/config/store.py
"""

import pytest
from hydra.core.config_store import ConfigStore
from hydra_zen import instantiate

from agloviz.config.store import setup_store


class TestStoreRegistration:
    """Test hydra-zen store registration functionality."""

    def test_setup_store_returns_store_instance(self):
        """Test that setup_store returns a valid store instance."""
        store_instance = setup_store()
        assert store_instance is not None
        assert hasattr(store_instance, 'add_to_hydra_store')

    def test_all_config_groups_registered(self):
        """Test that all expected config groups are registered."""
        setup_store()
        cs = ConfigStore.instance()

        expected_groups = ["renderer", "scenario", "theme", "timing"]
        for group in expected_groups:
            assert group in cs.repo, f"Config group '{group}' not registered"

    def test_renderer_configs_registered(self):
        """Test that all renderer configs are registered."""
        setup_store()
        cs = ConfigStore.instance()

        expected_renderers = ["draft", "medium", "hd"]
        available_renderers = [name.replace(".yaml", "") for name in cs.repo["renderer"].keys()]

        for renderer in expected_renderers:
            assert renderer in available_renderers, f"Renderer '{renderer}' not registered"

    def test_scenario_configs_registered(self):
        """Test that all scenario configs are registered."""
        setup_store()
        cs = ConfigStore.instance()

        expected_scenarios = ["maze_small", "maze_large", "weighted_graph"]
        available_scenarios = [name.replace(".yaml", "") for name in cs.repo["scenario"].keys()]

        for scenario in expected_scenarios:
            assert scenario in available_scenarios, f"Scenario '{scenario}' not registered"

    def test_theme_configs_registered(self):
        """Test that all theme configs are registered."""
        setup_store()
        cs = ConfigStore.instance()

        expected_themes = ["default", "dark", "high_contrast"]
        available_themes = [name.replace(".yaml", "") for name in cs.repo["theme"].keys()]

        for theme in expected_themes:
            assert theme in available_themes, f"Theme '{theme}' not registered"

    def test_timing_configs_registered(self):
        """Test that all timing configs are registered."""
        setup_store()
        cs = ConfigStore.instance()

        expected_timings = ["draft", "normal", "fast"]
        available_timings = [name.replace(".yaml", "") for name in cs.repo["timing"].keys()]

        for timing in expected_timings:
            assert timing in available_timings, f"Timing '{timing}' not registered"


class TestConfigInstantiation:
    """Test that registered configs can be instantiated."""

    def test_renderer_configs_instantiate(self):
        """Test that all renderer configs can be instantiated."""
        setup_store()
        cs = ConfigStore.instance()

        for config_name in cs.repo["renderer"].keys():
            config_node = cs.repo["renderer"][config_name].node
            renderer = instantiate(config_node)

            assert hasattr(renderer, 'config'), f"Renderer from {config_name} missing config"
            assert hasattr(renderer.config, 'resolution'), f"Renderer from {config_name} missing resolution"
            assert hasattr(renderer.config, 'quality'), f"Renderer from {config_name} missing quality"

    def test_scenario_configs_instantiate(self):
        """Test that all scenario configs can be instantiated."""
        setup_store()
        cs = ConfigStore.instance()

        for config_name in cs.repo["scenario"].keys():
            config_node = cs.repo["scenario"][config_name].node
            scenario = instantiate(config_node)

            assert hasattr(scenario, 'name'), f"Scenario from {config_name} missing name"
            assert hasattr(scenario, 'grid_size'), f"Scenario from {config_name} missing grid_size"
            assert hasattr(scenario, 'obstacles'), f"Scenario from {config_name} missing obstacles"

    def test_theme_configs_instantiate(self):
        """Test that all theme configs can be instantiated."""
        setup_store()
        cs = ConfigStore.instance()

        for config_name in cs.repo["theme"].keys():
            config_node = cs.repo["theme"][config_name].node
            theme = instantiate(config_node)

            assert hasattr(theme, 'name'), f"Theme from {config_name} missing name"
            assert hasattr(theme, 'colors'), f"Theme from {config_name} missing colors"

    def test_timing_configs_instantiate(self):
        """Test that all timing configs can be instantiated."""
        setup_store()
        cs = ConfigStore.instance()

        for config_name in cs.repo["timing"].keys():
            config_node = cs.repo["timing"][config_name].node
            timing = instantiate(config_node)

            assert hasattr(timing, 'mode'), f"Timing from {config_name} missing mode"
            assert hasattr(timing, 'ui'), f"Timing from {config_name} missing ui"
            assert hasattr(timing, 'events'), f"Timing from {config_name} missing events"
            assert hasattr(timing, 'effects'), f"Timing from {config_name} missing effects"
            assert hasattr(timing, 'waits'), f"Timing from {config_name} missing waits"


class TestStoreSimplicity:
    """Test that the store system is simple and follows hydra-zen patterns."""

    def test_store_setup_is_simple(self):
        """Test that store setup is simple with minimal code."""
        import inspect

        from agloviz.config import store

        # Check that store module is simple
        source = inspect.getsource(store)

        # Should be simple - no complex managers or global state
        assert "class" not in source or source.count("class") <= 1, "Store should be simple, not complex"
        assert "_store_initialized" not in source, "Should not use global flags"
        assert "singleton" not in source.lower(), "Should not use singleton patterns"

    def test_store_follows_hydra_zen_patterns(self):
        """Test that store follows hydra-zen documentation patterns."""
        import inspect

        from agloviz.config import store

        source = inspect.getsource(store)

        # Should use hydra-zen patterns
        assert "from hydra_zen import store" in source
        assert "store(group=" in source
        assert "StoreManager" in source

    def test_configs_work_with_instantiate(self):
        """Test that configs work with hydra-zen instantiate as expected."""
        setup_store()
        cs = ConfigStore.instance()

        # Test that we can instantiate any config
        renderer_config = cs.repo["renderer"]["medium.yaml"].node
        scenario_config = cs.repo["scenario"]["maze_small.yaml"].node

        renderer = instantiate(renderer_config)
        scenario = instantiate(scenario_config)

        # Should be fully functional objects
        assert renderer.config.quality in ["draft", "medium", "high"]
        assert scenario.name == "maze_small"
        assert scenario.grid_size == (10, 10)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
