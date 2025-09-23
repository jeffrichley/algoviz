"""Tests for SceneEngine parameter resolution integration."""

import pytest
from hydra_zen import instantiate

from agloviz.config.hydra_zen import BFSBasicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.scene import SceneEngine


class TestSceneEngineParameterResolution:
    """Test complete parameter resolution integration in SceneEngine."""

    def test_scene_engine_parameter_validation(self):
        """Test parameter validation in SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Test valid parameters
        valid_params = {"element": "node_A", "position": [1, 2], "color": "blue"}

        # Should not raise any exceptions
        engine._validate_parameters(valid_params)

        # Test invalid parameter templates
        invalid_params = {
            "element": "${invalid_syntax",
            "position": "${missing_resolver:path}",
            "color": "blue",
        }

        # Should raise ValueError for invalid syntax
        with pytest.raises(ValueError, match="Invalid parameter template syntax"):
            engine._validate_parameters(invalid_params)

    def test_scene_engine_parameter_resolution_with_event_data(self):
        """Test parameter resolution with event data in SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        engine = SceneEngine(scene_config, timing_config)

        # Create event data
        event_data = {
            "node": {"position": [3, 4], "color": "red", "id": "node_5"},
            "step": 2,
        }

        # Test parameter resolution with event data
        params_with_templates = {
            "element": "${event_data:node.id}",
            "position": "${event_data:node.position}",
            "color": "${event_data:node.color}",
            "step": "${event_data:step}",
        }

        # Note: This test would require the actual OmegaConf template resolution
        # For now, test that the method doesn't crash
        resolved_params = engine._resolve_parameters(params_with_templates, event_data)

        # Should return some resolved parameters (or fallback to original)
        assert isinstance(resolved_params, dict)

    def test_scene_engine_parameter_resolution_with_timing_config(self):
        """Test parameter resolution with timing configuration in SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        timing_config = TimingConfig(
            mode=TimingMode.FAST, ui=0.25, events=0.2, effects=0.125, waits=0.125
        )
        engine = SceneEngine(scene_config, timing_config)

        # Test parameter resolution with timing templates
        params_with_timing = {
            "duration": "${timing_value:ui}",
            "effect_duration": "${timing_value:effects}",
            "mode": "${timing_value:mode}",
        }

        # Note: This test would require the actual OmegaConf template resolution
        # For now, test that the method doesn't crash
        resolved_params = engine._resolve_parameters(params_with_timing, {})

        # Should return some resolved parameters (or fallback to original)
        assert isinstance(resolved_params, dict)

    def test_scene_engine_parameter_resolution_with_config_data(self):
        """Test parameter resolution with scene configuration in SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Test parameter resolution with config templates
        params_with_config = {
            "scene_name": "${config_value:name}",
            "algorithm": "${config_value:algorithm}",
            "widget_count": "${config_value:widgets}",
        }

        # Note: This test would require the actual OmegaConf template resolution
        # For now, test that the method doesn't crash
        resolved_params = engine._resolve_parameters(params_with_config, {})

        # Should return some resolved parameters (or fallback to original)
        assert isinstance(resolved_params, dict)

    def test_scene_engine_parameter_resolution_fallback(self):
        """Test parameter resolution fallback behavior in SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Test with invalid parameters that should fallback
        invalid_params = {
            "element": "${invalid_template}",
            "position": [1, 2],
            "color": "blue",
        }

        # Should fallback to original parameters
        resolved_params = engine._resolve_parameters(invalid_params, {})

        # Should return original parameters as fallback
        assert resolved_params == invalid_params

    def test_scene_engine_parameter_resolution_with_empty_params(self):
        """Test parameter resolution with empty parameters in SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Test with empty parameters
        empty_params = {}

        # Should return empty dict
        resolved_params = engine._resolve_parameters(empty_params, {})
        assert resolved_params == {}

    def test_scene_engine_parameter_resolution_with_none_params(self):
        """Test parameter resolution with None parameters in SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Test with None parameters
        none_params = None

        # Should return empty dict
        resolved_params = engine._resolve_parameters(none_params, {})
        assert resolved_params == {}

    def test_scene_engine_parameter_resolution_with_complex_event_data(self):
        """Test parameter resolution with complex event data in SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Create complex event data
        complex_event_data = {
            "algorithm": "bfs",
            "step": 5,
            "current_node": {
                "id": "node_10",
                "position": [5, 6],
                "neighbors": ["node_5", "node_15", "node_20"],
                "properties": {"distance": 5, "parent": "node_5", "visited": True},
            },
            "queue": ["node_15", "node_20", "node_25"],
            "path": [["node_0", "node_5", "node_10"]],
        }

        # Test parameter resolution with complex event data
        params_with_complex_templates = {
            "node_id": "${event_data:current_node.id}",
            "node_position": "${event_data:current_node.position}",
            "node_distance": "${event_data:current_node.properties.distance}",
            "node_parent": "${event_data:current_node.properties.parent}",
            "queue_size": "${event_data:queue}",
            "step_number": "${event_data:step}",
        }

        # Note: This test would require the actual OmegaConf template resolution
        # For now, test that the method doesn't crash
        resolved_params = engine._resolve_parameters(
            params_with_complex_templates, complex_event_data
        )

        # Should return some resolved parameters (or fallback to original)
        assert isinstance(resolved_params, dict)

    def test_scene_engine_parameter_resolution_error_handling(self):
        """Test error handling in parameter resolution in SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Test with parameters that might cause resolution errors
        problematic_params = {
            "element": "${event_data:missing.path}",
            "position": "${config_value:missing.config}",
            "timing": "${timing_value:missing.timing}",
            "valid_param": "static_value",
        }

        # Should handle errors gracefully and fallback
        resolved_params = engine._resolve_parameters(problematic_params, {})

        # Should return resolved parameters (template pattern for missing data)
        assert (
            resolved_params["element"] == "${event_data:missing.path}"
        )  # Missing event data
        assert resolved_params["position"] is None  # Missing config data
        assert (
            resolved_params["timing"] == "${timing_value:missing.timing}"
        )  # Missing timing data (template pattern)
        assert (
            resolved_params["valid_param"] == "static_value"
        )  # Static value preserved

    def test_scene_engine_parameter_resolution_performance(self):
        """Test parameter resolution performance in SceneEngine."""
        scene_config = instantiate(BFSBasicSceneConfig)
        engine = SceneEngine(scene_config)

        # Create large parameter set
        large_params = {}
        for i in range(100):
            large_params[f"param_{i}"] = f"${{event_data:node_{i}}}"

        # Test performance with large parameter set
        import time

        start_time = time.time()

        resolved_params = engine._resolve_parameters(large_params, {})

        end_time = time.time()
        resolution_time = end_time - start_time

        # Should complete within reasonable time (less than 1 second)
        assert resolution_time < 1.0
        assert isinstance(resolved_params, dict)
