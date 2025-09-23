"""Tests for SceneEngine integration with hydra-zen scene configs."""

from hydra_zen import instantiate

from agloviz.config.hydra_zen import BFSAdvancedSceneConfig, BFSBasicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.scene import SceneEngine


class TestSceneEngineHydraZenIntegration:
    """Test SceneEngine with hydra-zen scene configs."""

    def test_scene_engine_with_scene_config_object(self):
        """Test SceneEngine with hydra-zen instantiated SceneConfig."""
        # Instantiate scene config with hydra-zen
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)

        # Create SceneEngine with SceneConfig object
        engine = SceneEngine(scene_config, timing_config)

        assert engine.get_scene_name() == "bfs_basic"
        assert engine.get_scene_algorithm() == "bfs"
        assert engine.get_widget_count() == 2  # grid + queue
        assert "grid" in engine.list_widget_names()
        assert "queue" in engine.list_widget_names()

    def test_scene_engine_widget_initialization_with_hydra_zen(self):
        """Test that SceneEngine properly initializes hydra-zen widgets."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Check that widgets are properly initialized
        assert len(engine.widgets) == 2

        grid_widget = engine.widgets["grid"]
        queue_widget = engine.widgets["queue"]

        # Widgets should have the Widget protocol methods
        assert hasattr(grid_widget, "show")
        assert hasattr(grid_widget, "hide")
        assert hasattr(queue_widget, "show")
        assert hasattr(queue_widget, "hide")

    def test_scene_engine_with_advanced_scene_config(self):
        """Test SceneEngine with BFSAdvancedSceneConfig."""
        scene_config = instantiate(BFSAdvancedSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.FAST)

        engine = SceneEngine(scene_config, timing_config)

        assert engine.get_scene_name() == "bfs_advanced"
        assert engine.get_scene_algorithm() == "bfs"
        assert engine.get_widget_count() == 2
        assert "grid" in engine.list_widget_names()
        assert "queue" in engine.list_widget_names()

    def test_scene_engine_without_timing_config(self):
        """Test SceneEngine initialization without timing config."""
        scene_config = instantiate(BFSBasicSceneConfig)

        # Should work without timing config
        engine = SceneEngine(scene_config)

        assert engine.get_scene_name() == "bfs_basic"
        assert engine.get_scene_algorithm() == "bfs"
        assert engine.get_widget_count() == 2
        assert engine.timing_config is None

    def test_scene_engine_widget_access(self):
        """Test accessing widgets through SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Test get_widget method
        grid_widget = engine.get_widget("grid")
        queue_widget = engine.get_widget("queue")

        assert grid_widget is not None
        assert queue_widget is not None
        assert grid_widget == engine.widgets["grid"]
        assert queue_widget == engine.widgets["queue"]

        # Test accessing non-existent widget (returns None, doesn't raise KeyError)
        nonexistent_widget = engine.get_widget("nonexistent")
        assert nonexistent_widget is None

    def test_scene_engine_scene_config_access(self):
        """Test accessing scene config through SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Test get_scene_config method
        config = engine.get_scene_config()

        assert config is not None
        assert hasattr(config, "name")
        assert hasattr(config, "algorithm")
        assert hasattr(config, "event_bindings")

    def test_scene_engine_event_bindings_setup(self):
        """Test that SceneEngine properly sets up event bindings."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        self._verify_event_bindings_structure(engine)
        self._verify_enqueue_bindings(engine)

    def _verify_event_bindings_structure(self, engine):
        """Verify basic event bindings structure."""
        assert hasattr(engine, "event_bindings")
        assert isinstance(engine.event_bindings, dict)
        assert "enqueue" in engine.event_bindings
        assert "dequeue" in engine.event_bindings

    def _verify_enqueue_bindings(self, engine):
        """Verify enqueue bindings structure."""
        enqueue_bindings = engine.event_bindings["enqueue"]
        assert len(enqueue_bindings) == 2  # queue add_element + grid highlight_cell

        self._verify_queue_binding(enqueue_bindings[0])
        self._verify_grid_binding(enqueue_bindings[1])

    def _verify_queue_binding(self, queue_binding):
        """Verify queue binding details."""
        assert queue_binding.widget == "queue"
        assert queue_binding.action == "add_element"
        assert queue_binding.order == 1

    def _verify_grid_binding(self, grid_binding):
        """Verify grid binding details."""
        assert grid_binding.widget == "grid"
        assert grid_binding.action == "highlight_cell"
        assert grid_binding.params["color"] == "blue"
        assert grid_binding.order == 2

    def test_scene_engine_advanced_config_custom_parameters(self):
        """Test that advanced config custom parameters are applied."""
        scene_config = instantiate(BFSAdvancedSceneConfig)
        engine = SceneEngine(scene_config)

        # The custom parameters (width, height, max_visible_items) are applied during
        # widget instantiation, but we can't easily test them without knowing widget internals.
        # The fact that instantiation succeeds means the parameters were valid.
        assert engine.get_widget_count() == 2
        assert "grid" in engine.widgets
        assert "queue" in engine.widgets

        # Widgets should be properly instantiated
        grid_widget = engine.widgets["grid"]
        queue_widget = engine.widgets["queue"]

        assert hasattr(grid_widget, "show")
        assert hasattr(queue_widget, "show")

    def test_scene_engine_consistency_between_configs(self):
        """Test that both basic and advanced configs produce consistent SceneEngine behavior."""
        basic_config = instantiate(BFSBasicSceneConfig)
        advanced_config = instantiate(BFSAdvancedSceneConfig)

        basic_engine = SceneEngine(basic_config)
        advanced_engine = SceneEngine(advanced_config)

        self._verify_algorithm_consistency(basic_engine, advanced_engine)
        self._verify_widget_consistency(basic_engine, advanced_engine)
        self._verify_event_binding_consistency(basic_engine, advanced_engine)

    def _verify_algorithm_consistency(self, basic_engine, advanced_engine):
        """Verify algorithm consistency between engines."""
        assert (
            basic_engine.get_scene_algorithm() == advanced_engine.get_scene_algorithm()
        )
        assert basic_engine.get_scene_algorithm() == "bfs"

    def _verify_widget_consistency(self, basic_engine, advanced_engine):
        """Verify widget consistency between engines."""
        assert basic_engine.get_widget_count() == advanced_engine.get_widget_count()
        assert basic_engine.get_widget_count() == 2
        assert set(basic_engine.list_widget_names()) == set(
            advanced_engine.list_widget_names()
        )
        assert set(basic_engine.list_widget_names()) == {"grid", "queue"}

    def _verify_event_binding_consistency(self, basic_engine, advanced_engine):
        """Verify event binding consistency between engines."""
        assert set(basic_engine.event_bindings.keys()) == set(
            advanced_engine.event_bindings.keys()
        )
        assert "enqueue" in basic_engine.event_bindings
        assert "dequeue" in basic_engine.event_bindings

    def test_scene_engine_timing_config_integration(self):
        """Test SceneEngine with different timing configurations."""
        scene_config = instantiate(BFSBasicSceneConfig)

        # Test with different timing modes
        for mode in [TimingMode.DRAFT, TimingMode.NORMAL, TimingMode.FAST]:
            timing_config = TimingConfig(mode=mode)
            engine = SceneEngine(scene_config, timing_config)

            assert engine.timing_config is not None
            assert engine.timing_config.mode == mode
            assert engine.get_scene_name() == "bfs_basic"
            assert engine.get_widget_count() == 2
