"""Test showing the CORRECT way to handle YAML templates.

The key insight: We need to preserve template syntax until we're ready to resolve it.
"""

from omegaconf import OmegaConf

from agloviz.core.resolvers import register_custom_resolvers


class TestCorrectYamlTemplateFlow:
    """Test the correct way to handle YAML templates."""

    def test_show_why_templates_get_lost(self):
        """Show why templates get lost in the current approach."""

        # Load YAML - templates are preserved here
        yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")
        print("=== YAML Loaded ===")
        print(
            f"Raw YAML element param: {yaml_config.event_bindings.enqueue[0].params.element}"
        )

        # The problem: When we access the parameter, OmegaConf tries to resolve it
        # But our custom resolvers aren't registered, so it fails and returns None
        element_param = yaml_config.event_bindings.enqueue[0].params.element
        print(f"Accessed element param: {element_param}")
        print(f"Type: {type(element_param)}")

        # This is why the templates get lost!

    def test_correct_approach_with_raw_yaml(self):
        """Test the correct approach: work with raw YAML until resolution time."""

        # Step 1: Load YAML and DON'T try to access template parameters yet
        # yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")

        # Step 2: Register resolvers BEFORE doing any template resolution
        register_custom_resolvers()

        # Step 3: Now we can safely access and resolve templates
        print("=== With Resolvers Registered ===")

        # Create a test event
        test_event = {
            "event": {  # Note: YAML uses "event.node", not "node.id"
                "node": "node_42",
                "pos": [7, 3],
            }
        }

        # Step 4: Manually resolve the template using OmegaConf
        template_string = "${event_data:event.node}"
        print(f"Template string: {template_string}")

        # Create a simple config with the template
        test_config = OmegaConf.create({"value": template_string})

        # Resolve it with our custom resolvers
        from agloviz.core.resolvers import ResolverContext

        context = ResolverContext(event=test_event)

        with context:
            resolved_config = OmegaConf.to_container(test_config, resolve=True)
            resolved_value = resolved_config["value"]

        print(f"Resolved value: {resolved_value}")
        assert resolved_value == "node_42"

        print("✅ Template resolution works when resolvers are registered!")

    def test_what_scene_engine_should_do(self):
        """Test what SceneEngine should do to preserve templates."""

        # The issue: SceneEngine converts Pydantic to OmegaConf AFTER instantiate()
        # But instantiate() already tried to resolve templates and failed

        # What SceneEngine should do:
        # 1. Keep the original YAML with templates
        # 2. Only resolve templates at runtime when resolvers are available

        print("=== What SceneEngine Should Do ===")

        # Load YAML with templates preserved
        # yaml_config = OmegaConf.load("configs/scene/bfs_pathfinding.yaml")

        # Register resolvers
        register_custom_resolvers()

        # Create test event
        test_event = {"event": {"node": "node_42", "pos": [7, 3]}}

        # Simulate what SceneEngine._resolve_parameters should do:
        # 1. Take the original template parameters from YAML
        original_params = {
            "element": "${event_data:event.node}",
            "duration": "${timing_value:ui}",
        }

        print(f"Original params: {original_params}")

        # 2. Create OmegaConf config with templates
        params_config = OmegaConf.create(original_params)

        # 3. Resolve with context
        from agloviz.core.resolvers import ResolverContext

        context = ResolverContext(event=test_event)

        with context:
            resolved_params = OmegaConf.to_container(params_config, resolve=True)

        print(f"Resolved params: {resolved_params}")

        # Verify resolution worked
        assert resolved_params["element"] == "node_42"
        assert resolved_params["duration"] is not None

        print("✅ This is how SceneEngine should handle templates!")
