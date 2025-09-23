"""Tests for event parameter resolution with dynamic event data."""

from omegaconf import OmegaConf

from agloviz.core.resolvers import ResolverContext, _resolve_event_path


class TestEventParameterResolution:
    """Test dynamic parameter resolution with event data."""

    def test_resolve_simple_event_path(self):
        """Test resolving simple event data paths."""
        event_data = {"node": "A", "position": [1, 2], "color": "red"}

        # Test simple path resolution
        assert _resolve_event_path("node", event_data) == "A"
        assert _resolve_event_path("position", event_data) == [1, 2]
        assert _resolve_event_path("color", event_data) == "red"

    def test_resolve_nested_event_path(self):
        """Test resolving nested event data paths."""
        event_data = {
            "node": {
                "position": [3, 4],
                "color": "blue",
                "metadata": {"weight": 5, "visited": True},
            }
        }

        # Test nested path resolution
        assert _resolve_event_path("node.position", event_data) == [3, 4]
        assert _resolve_event_path("node.color", event_data) == "blue"
        assert _resolve_event_path("node.metadata.weight", event_data) == 5
        assert _resolve_event_path("node.metadata.visited", event_data) is True

    def test_resolve_missing_event_path(self):
        """Test resolving missing event data paths."""
        event_data = {"node": "A", "position": [1, 2]}

        # Test missing path resolution
        assert _resolve_event_path("missing", event_data) is None
        assert _resolve_event_path("node.missing", event_data) is None
        assert _resolve_event_path("node.position.missing", event_data) is None

    def test_resolve_event_path_with_context(self):
        """Test resolving event paths using ResolverContext."""
        event_data = {"node": {"position": [5, 6], "color": "green"}}

        context = ResolverContext(event=event_data)

        with context:
            assert _resolve_event_path("node.position") == [5, 6]
            assert _resolve_event_path("node.color") == "green"

    def test_resolve_event_path_without_context(self):
        """Test resolving event paths without context."""
        # Should return template pattern when no context and no event_data provided
        assert _resolve_event_path("node") == "${event_data:node}"
        assert _resolve_event_path("position") == "${event_data:position}"

    def test_resolve_complex_event_data(self):
        """Test resolving complex event data structures."""
        event_data = self._create_complex_event_data()
        self._test_complex_paths(event_data)

    def _create_complex_event_data(self):
        """Create complex event data for testing."""
        return {
            "algorithm": "bfs",
            "step": 3,
            "current_node": {
                "id": "node_5",
                "position": [2, 3],
                "neighbors": ["node_1", "node_7", "node_9"],
                "properties": {"distance": 3, "parent": "node_2", "visited": True},
            },
            "queue": ["node_7", "node_9", "node_12"],
            "path": [["node_0", "node_2", "node_5"]],
        }

    def _test_complex_paths(self, event_data):
        """Test various complex paths."""
        self._test_basic_paths(event_data)
        self._test_node_paths(event_data)
        self._test_properties_paths(event_data)
        self._test_collection_paths(event_data)

    def _test_basic_paths(self, event_data):
        """Test basic path resolution."""
        assert _resolve_event_path("algorithm", event_data) == "bfs"
        assert _resolve_event_path("step", event_data) == 3

    def _test_node_paths(self, event_data):
        """Test current node path resolution."""
        assert _resolve_event_path("current_node.id", event_data) == "node_5"
        assert _resolve_event_path("current_node.position", event_data) == [2, 3]
        assert _resolve_event_path("current_node.neighbors", event_data) == [
            "node_1",
            "node_7",
            "node_9",
        ]

    def _test_properties_paths(self, event_data):
        """Test properties path resolution."""
        assert _resolve_event_path("current_node.properties.distance", event_data) == 3
        assert (
            _resolve_event_path("current_node.properties.parent", event_data)
            == "node_2"
        )
        assert (
            _resolve_event_path("current_node.properties.visited", event_data) is True
        )

    def _test_collection_paths(self, event_data):
        """Test collection path resolution."""
        assert _resolve_event_path("queue", event_data) == [
            "node_7",
            "node_9",
            "node_12",
        ]
        assert _resolve_event_path("path", event_data) == [
            ["node_0", "node_2", "node_5"]
        ]

    def test_resolve_event_path_with_omega_conf_templates(self):
        """Test resolving event paths with OmegaConf template syntax."""
        event_data = {"node": {"position": [7, 8], "color": "purple"}}

        # Test with OmegaConf template resolution
        template = "${event_data:node.position}"
        OmegaConf.create({"position": template})

        # This would be resolved by OmegaConf with the resolver
        # For now, test the direct resolver function
        assert _resolve_event_path("node.position", event_data) == [7, 8]
        assert _resolve_event_path("node.color", event_data) == "purple"

    def test_resolve_event_path_error_handling(self):
        """Test error handling for invalid event data."""
        # Test with None event data - should return template pattern
        assert _resolve_event_path("node", None) == "${event_data:node}"

        # Test with empty event data - should return template pattern
        assert _resolve_event_path("node", {}) == "${event_data:node}"

        # Test with non-dict event data
        assert _resolve_event_path("node", "not_a_dict") is None

        # Test with invalid path
        event_data = {"node": "A"}
        assert _resolve_event_path("", event_data) is None
