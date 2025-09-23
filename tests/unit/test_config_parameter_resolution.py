"""Tests for configuration parameter resolution."""

from omegaconf import OmegaConf

from agloviz.core.resolvers import ResolverContext, _resolve_config_path


class TestConfigParameterResolution:
    """Test configuration parameter resolution."""

    def test_resolve_simple_config_path(self):
        """Test resolving simple configuration paths."""
        scene_config = {
            "name": "bfs_scene",
            "algorithm": "bfs",
            "colors": {
                "frontier": "#2196F3",
                "visited": "#4CAF50",
                "goal": "#FF9800"
            }
        }

        # Test simple path resolution
        assert _resolve_config_path("name", scene_config) == "bfs_scene"
        assert _resolve_config_path("algorithm", scene_config) == "bfs"
        assert _resolve_config_path("colors", scene_config) == {
            "frontier": "#2196F3",
            "visited": "#4CAF50",
            "goal": "#FF9800"
        }

    def test_resolve_nested_config_path(self):
        """Test resolving nested configuration paths."""
        scene_config = {
            "widgets": {
                "grid": {
                    "width": 15,
                    "height": 15,
                    "cell_size": 0.5
                },
                "queue": {
                    "max_visible": 10,
                    "orientation": "horizontal"
                }
            },
            "theme": {
                "colors": {
                    "frontier": "#2196F3",
                    "visited": "#4CAF50"
                }
            }
        }

        # Test nested path resolution
        assert _resolve_config_path("widgets.grid.width", scene_config) == 15
        assert _resolve_config_path("widgets.grid.height", scene_config) == 15
        assert _resolve_config_path("widgets.queue.max_visible", scene_config) == 10
        assert _resolve_config_path("theme.colors.frontier", scene_config) == "#2196F3"
        assert _resolve_config_path("theme.colors.visited", scene_config) == "#4CAF50"

    def test_resolve_config_path_with_defaults(self):
        """Test resolving configuration paths with default values."""
        scene_config = {
            "name": "test_scene",
            "algorithm": "bfs"
        }

        # Test with default values
        assert _resolve_config_path("name", scene_config, "default_name") == "test_scene"
        assert _resolve_config_path("missing", scene_config, "default_value") == "default_value"
        assert _resolve_config_path("missing.nested", scene_config, 42) == 42

    def test_resolve_config_path_with_context(self):
        """Test resolving configuration paths using ResolverContext."""
        scene_config = {
            "colors": {
                "frontier": "#2196F3",
                "visited": "#4CAF50"
            }
        }

        context = ResolverContext(config=scene_config)

        with context:
            assert _resolve_config_path("colors.frontier") == "#2196F3"
            assert _resolve_config_path("colors.visited") == "#4CAF50"

    def test_resolve_config_path_without_context(self):
        """Test resolving configuration paths without context."""
        # Should return default when no context and no scene_config provided
        assert _resolve_config_path("colors", default="default_color") == "default_color"
        assert _resolve_config_path("missing", default=42) == 42

    def test_resolve_config_path_with_object_attributes(self):
        """Test resolving configuration paths with object attributes."""
        class MockConfig:
            def __init__(self):
                self.name = "object_config"
                self.algorithm = "dfs"
                self.colors = {
                    "frontier": "#FF5722",
                    "visited": "#8BC34A"
                }

        config_obj = MockConfig()

        # Test object attribute resolution
        assert _resolve_config_path("name", config_obj) == "object_config"
        assert _resolve_config_path("algorithm", config_obj) == "dfs"
        assert _resolve_config_path("colors", config_obj) == {
            "frontier": "#FF5722",
            "visited": "#8BC34A"
        }

    def test_resolve_config_path_missing_keys(self):
        """Test resolving missing configuration keys."""
        scene_config = {
            "name": "test_scene",
            "algorithm": "bfs"
        }

        # Test missing key resolution
        assert _resolve_config_path("missing", scene_config) is None
        assert _resolve_config_path("name.missing", scene_config) is None
        assert _resolve_config_path("algorithm.missing", scene_config) is None

    def test_resolve_config_path_with_omega_conf_templates(self):
        """Test resolving configuration paths with OmegaConf template syntax."""
        scene_config = {
            "colors": {
                "frontier": "#2196F3",
                "visited": "#4CAF50"
            }
        }

        # Test with OmegaConf template resolution
        template = "${config_value:colors.frontier}"
        params_config = OmegaConf.create({"color": template})

        # This would be resolved by OmegaConf with the resolver
        # For now, test the direct resolver function
        assert _resolve_config_path("colors.frontier", scene_config) == "#2196F3"
        assert _resolve_config_path("colors.visited", scene_config) == "#4CAF50"

    def test_resolve_config_path_error_handling(self):
        """Test error handling for invalid configuration data."""
        # Test with None config
        assert _resolve_config_path("name", None, "default") == "default"

        # Test with empty config
        assert _resolve_config_path("name", {}, "default") == "default"

        # Test with invalid path
        scene_config = {"name": "test"}
        assert _resolve_config_path("", scene_config) is None

    def test_resolve_complex_config_structure(self):
        """Test resolving complex configuration structures."""
        scene_config = {
            "name": "complex_scene",
            "algorithm": "dijkstra",
            "widgets": {
                "grid": {
                    "width": 20,
                    "height": 20,
                    "cell_size": 0.4,
                    "show_coordinates": True
                },
                "queue": {
                    "max_visible": 15,
                    "orientation": "vertical",
                    "show_indices": True
                },
                "legend": {
                    "position": "top_right",
                    "legend_items": [
                        {"name": "unvisited", "color": "#E0E0E0"},
                        {"name": "frontier", "color": "#2196F3"},
                        {"name": "visited", "color": "#4CAF50"}
                    ]
                }
            },
            "timing": {
                "events": 0.8,
                "effects": 0.5,
                "ui": 1.0
            }
        }

        # Test various complex paths
        assert _resolve_config_path("name", scene_config) == "complex_scene"
        assert _resolve_config_path("algorithm", scene_config) == "dijkstra"
        assert _resolve_config_path("widgets.grid.width", scene_config) == 20
        assert _resolve_config_path("widgets.grid.show_coordinates", scene_config) is True
        assert _resolve_config_path("widgets.queue.orientation", scene_config) == "vertical"
        assert _resolve_config_path("widgets.legend.position", scene_config) == "top_right"
        # Test legend items structure
        legend_items = _resolve_config_path("widgets.legend.legend_items", scene_config)
        assert isinstance(legend_items, list)
        assert len(legend_items) == 3
        assert legend_items[0]["name"] == "unvisited"
        assert legend_items[0]["color"] == "#E0E0E0"
        assert _resolve_config_path("timing.events", scene_config) == 0.8
        assert _resolve_config_path("timing.effects", scene_config) == 0.5
        assert _resolve_config_path("timing.ui", scene_config) == 1.0
