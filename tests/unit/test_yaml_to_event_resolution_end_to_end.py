"""End-to-end test showing YAML file → SceneEngine → Dynamic event resolution.

This test demonstrates the complete flow:
1. Load YAML file with template parameters
2. Convert to Pydantic model via Hydra-zen
3. Create SceneEngine (which converts to internal OmegaConf)
4. Register custom resolvers
5. Resolve dynamic event parameters using the template system
"""

from hydra_zen import instantiate
from omegaconf import OmegaConf

from agloviz.config.hydra_zen import BFSBasicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.managers import SystemRegistry
from agloviz.core.scene import SceneEngine


class TestYamlToEventResolutionEndToEnd:
    """Test complete flow from YAML file to dynamic event resolution."""

    def test_yaml_file_to_dynamic_event_resolution(self):
        """Test complete flow: YAML → Pydantic → SceneEngine → Event resolution."""

        # Step 1: Initialize the system via registry (registers resolvers, loads configs)
        SystemRegistry.reset()  # Clean state
        orchestrator = SystemRegistry.get_orchestrator()
        print("System initialized via registry")

        # Step 2: Get YAML config from the orchestrator (already loaded with proper resolver context)
        yaml_config = orchestrator.get_yaml_config("bfs_pathfinding")
        print(f"Loaded YAML via orchestrator: {yaml_config.name}")
        print(f"YAML event bindings: {yaml_config.event_bindings}")

        # Step 3: Create scene config from YAML using the orchestrator's context
        # The orchestrator has resolvers registered, so we can safely instantiate
        scene_overrides = {k: v for k, v in yaml_config.items() if k != "timing_overrides"}
        scene_config = instantiate(BFSBasicSceneConfig, **scene_overrides)
        print(f"Scene config created: {scene_config.name}")

        # Step 4: Create SceneEngine (converts Pydantic to internal OmegaConf)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)
        print(f"SceneEngine created with {len(scene_engine.widgets)} widgets")

        # Step 5: Create a test event with data
        # The YAML expects "${event_data:event.node}" so we need "event" key
        test_event = {
            "event": {
                "node": "node_42",  # The YAML expects just the node ID, not an object
                "pos": [7, 3]       # The YAML expects "pos" not "position"
            },
            "step": 15
        }
        print(f"Test event: {test_event}")

        # Step 6: Get event binding parameters from the YAML-loaded config
        # The YAML file has template parameters like "${event_data:event.node}"
        enqueue_bindings = scene_engine.event_bindings["enqueue"]
        first_binding = enqueue_bindings[0]  # Queue binding
        template_params = first_binding.params
        print(f"Template parameters: {template_params}")

        # Step 7: Resolve the template parameters using SceneEngine's internal system
        resolved_params = scene_engine._resolve_parameters(template_params, test_event)
        print(f"Resolved parameters: {resolved_params}")

        # Step 8: Verify the resolution worked correctly
        # The YAML file has: element: "${event_data:event.node}"
        # This should resolve to the node ID from the test event
        assert resolved_params["element"] == "node_42"
        assert resolved_params["duration"] is not None  # Should resolve to timing value

        print("✅ End-to-end test passed!")

    def test_show_actual_yaml_template_syntax(self):
        """Show what the actual template syntax looks like in the YAML file."""

        # Initialize system via registry
        SystemRegistry.reset()  # Clean state
        orchestrator = SystemRegistry.get_orchestrator()

        # Get YAML config from orchestrator (with proper resolver context)
        yaml_config = orchestrator.get_yaml_config("bfs_pathfinding")

        print("\n=== YAML Template Syntax ===")
        for event_name, bindings in yaml_config.event_bindings.items():
            print(f"\nEvent: {event_name}")
            for i, binding in enumerate(bindings):
                print(f"  Binding {i}:")
                print(f"    Widget: {binding.widget}")
                print(f"    Action: {binding.action}")
                print(f"    Params: {binding.params}")

        # Show that the templates are preserved in the raw YAML structure
        # We need to access the raw data to see the template strings
        raw_yaml_data = OmegaConf.to_container(yaml_config, resolve=False)
        first_binding_raw = raw_yaml_data['event_bindings']['enqueue'][0]
        element_param_raw = first_binding_raw['params']['element']
        print(f"\nTemplate parameter (raw): {element_param_raw}")
        print(f"Template parameter type: {type(element_param_raw)}")

        # This should be a string with template syntax
        assert isinstance(element_param_raw, str)
        assert element_param_raw == "${event_data:event.node}"
        assert "${" in element_param_raw
        assert "event_data" in element_param_raw
