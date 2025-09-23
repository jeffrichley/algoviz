"""Test the system orchestrator and manager system using Registry Pattern."""

from agloviz.core.managers import SystemOrchestrator, SystemRegistry


class TestSystemOrchestrator:
    """Test the system orchestrator with Registry Pattern."""

    def test_system_registry_singleton(self):
        """Test that SystemRegistry provides singleton behavior."""
        orchestrator1 = SystemRegistry.get_orchestrator()
        orchestrator2 = SystemRegistry.get_orchestrator()

        assert orchestrator1 is orchestrator2
        assert isinstance(orchestrator1, SystemOrchestrator)

    def test_system_initialization_via_registry(self):
        """Test complete system initialization via registry."""
        # Reset registry for clean test
        SystemRegistry.reset()

        # Get orchestrator via registry (auto-initializes)
        orchestrator = SystemRegistry.get_orchestrator()

        # Verify system is initialized
        assert orchestrator.is_initialized()
        assert SystemRegistry.is_initialized()

    def test_system_components_initialization(self):
        """Test that all system components are properly initialized."""
        # Reset registry for clean test
        SystemRegistry.reset()
        orchestrator = SystemRegistry.get_orchestrator()

        # Verify all components are initialized
        status = orchestrator.get_status()
        assert status["system_initialized"] is True
        assert status["resolvers_registered"] is True
        assert status["builders_initialized"] is True
        assert status["store_initialized"] is True

    def test_system_initialization_order(self):
        """Test that system components are initialized in correct order."""
        # Reset registry for clean test
        SystemRegistry.reset()
        orchestrator = SystemRegistry.get_orchestrator()

        # Verify initialization order
        status = orchestrator.get_status()
        order = status["initialization_order"]
        assert "resolver" in order
        assert "store" in order
        assert "builder" in order
        assert order.index("resolver") < order.index("store")
        assert order.index("store") < order.index("builder")

    def test_yaml_config_loading_via_registry(self):
        """Test that YAML configs are loaded via registry."""
        # Reset registry for clean test
        SystemRegistry.reset()

        # Get orchestrator via registry
        orchestrator = SystemRegistry.get_orchestrator()

        # Get all YAML configs
        yaml_configs = orchestrator.get_all_yaml_configs()

        # Should have loaded some configs
        assert len(yaml_configs) > 0

        # Test getting specific config
        bfs_config = orchestrator.get_yaml_config("bfs_pathfinding")
        if bfs_config:  # Only test if file exists
            assert bfs_config.name == "bfs_pathfinding"

    def test_individual_managers_via_registry(self):
        """Test access to individual managers via registry."""
        # Reset registry for clean test
        SystemRegistry.reset()

        # Get orchestrator via registry
        orchestrator = SystemRegistry.get_orchestrator()

        # Test resolver manager
        resolver_manager = orchestrator.get_resolver_manager()
        assert resolver_manager.is_registered()

        # Test builder manager
        builder_manager = orchestrator.get_builder_manager()
        assert builder_manager.is_initialized()

        # Test store manager
        store_manager = orchestrator.get_store_manager()
        assert store_manager._initialized

    def test_registry_reset(self):
        """Test registry reset functionality."""
        # Get orchestrator via registry
        orchestrator1 = SystemRegistry.get_orchestrator()
        assert orchestrator1.is_initialized()

        # Reset registry
        SystemRegistry.reset()
        assert not SystemRegistry.is_initialized()

        # Get new orchestrator (should be different instance)
        orchestrator2 = SystemRegistry.get_orchestrator()
        assert orchestrator2 is not orchestrator1
        assert orchestrator2.is_initialized()
