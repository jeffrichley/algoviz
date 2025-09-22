# ALGOViz Error Taxonomy & Messages v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0 - Hydra-zen First)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Enhanced for hydra-zen first architecture error patterns)
**Supersedes:** planning/v1/ALGOViz_Error_Taxonomy.md

---

## 1. Purpose
Define consistent error messages, remediation guidance, and failure modes across all ALGOViz components, **including hydra-zen specific error patterns**. Ensures users receive actionable, contextual feedback with consistent terminology and helpful suggestions for structured config and ConfigStore issues.

## 2. Error Categories (Enhanced for Hydra-zen)

### 2.1 Configuration Errors (Enhanced)
**Pattern**: `ConfigError: [context] - [specific issue] - [remedy]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Unknown config key | `Unknown config key '{key}' in {file}:{line}. Valid keys: {suggestions}` | `Unknown config key 'timing.foo' in scenario.yaml:12. Valid keys: ui, events, effects, waits` |
| Type mismatch | `Expected {expected_type} for '{key}' in {file}:{line}, got {actual_type}` | `Expected int for 'width' in maze.yaml:3, got str` |
| Missing required field | `Missing required field '{field}' in {file}:{line}` | `Missing required field 'start' in scenario.yaml:8` |
| Invalid enum value | `Invalid value '{value}' for '{key}'. Valid options: {options}` | `Invalid value 'ultra' for 'quality'. Valid options: draft, medium, high` |

### 2.2 Hydra-zen Configuration Errors (New)
**Pattern**: `HydraZenError: [config_context] - [issue] - [remedy]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Missing _target_ | `Structured config missing '_target_' field in {config_name}. Add '_target_: path.to.Class'` | `Structured config missing '_target_' field in widget/grid. Add '_target_: agloviz.widgets.GridWidget'` |
| Invalid _target_ | `Invalid '_target_' path '{target}' in {config_name}. Check import path and class name.` | `Invalid '_target_' path 'agloviz.widgets.NonExistentWidget' in widget/grid. Check import path and class name.` |
| ConfigStore not found | `Config '{config_key}' not found in ConfigStore. Available: {available_configs}` | `Config 'scene/invalid_scene' not found in ConfigStore. Available: ['scene/bfs_pathfinding', 'scene/dfs_pathfinding']` |
| Instantiation failure | `Failed to instantiate config '{config_name}': {error}. Check _target_ and parameters.` | `Failed to instantiate config 'widget/grid': missing required parameter 'width'. Check _target_ and parameters.` |
| zen_partial missing | `Structured config '{config_name}' should use zen_partial=True for flexibility` | `Structured config 'widget/grid' should use zen_partial=True for flexibility` |

### 2.3 Parameter Template Errors (New)
**Pattern**: `TemplateError: [template_context] - [resolution_issue] - [fix]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Invalid resolver | `Unknown resolver '{resolver}' in template '{template}'. Available resolvers: {available}` | `Unknown resolver 'invalid_data' in template '${invalid_data:event.node}'. Available resolvers: event_data, timing_value, config_value` |
| Resolution failure | `Failed to resolve template '{template}' in {context}: {error}` | `Failed to resolve template '${event_data:event.invalid_field}' in event binding: AttributeError('VizEvent' has no attribute 'invalid_field')` |
| Missing context | `Template '{template}' requires context '{required_context}' but none provided` | `Template '${event_data:event.node}' requires context 'event' but none provided` |
| Circular reference | `Circular reference detected in template '{template}': {cycle_path}` | `Circular reference detected in template '${config_value:self.reference}': config.self.reference -> config.self.reference` |

### 2.4 Storyboard Errors (Enhanced)
**Pattern**: `StoryboardError: [location] - [issue] - [suggestion]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Unknown action | `Unknown action '{action}' at Act {act}/Shot {shot}/Beat {beat}. Available: {core_actions}, scene: {scene_actions}, templates: {template_actions}` | `Unknown action 'trace_paht' at Act 2/Shot 1/Beat 3. Available: core: [show_title, play_events], scene: [place_start, place_goal], templates: [show_widgets]` |
| Missing action args | `Action '{action}' at Act {act}/Shot {shot}/Beat {beat} missing required args: {missing_args}` | `Action 'show_title' at Act 1/Shot 1/Beat 1 missing required args: text` |
| Invalid scene reference | `Scene '{scene}' referenced in beat action not found in ConfigStore. Available scenes: {available}` | `Scene 'invalid_scene' referenced in beat action not found in ConfigStore. Available scenes: ['bfs_pathfinding', 'dfs_pathfinding']` |
| Template instantiation | `Failed to instantiate storyboard template '{template}': {error}` | `Failed to instantiate storyboard template 'pathfinding_template': missing required parameter 'algorithm'` |

### 2.5 Algorithm Adapter Errors (Enhanced)
**Pattern**: `AdapterError: [{algorithm}] - [step_context] - [issue]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Adapter crash | `Algorithm '{algo}' crashed at step {step}: {error}. Try with minimal scenario for debugging.` | `Algorithm 'bfs' crashed at step 15: KeyError('neighbors'). Try with minimal scenario for debugging.` |
| Unknown algorithm | `Unknown algorithm '{algo}'. Available: {available_algos}` | `Unknown algorithm 'bf' Available: bfs, dfs, dijkstra, a_star` |
| Invalid scenario | `Algorithm '{algo}' requires {requirements}, but scenario provides {actual}` | `Algorithm 'dijkstra' requires weighted edges, but scenario provides unweighted grid` |
| Adapter instantiation | `Failed to instantiate adapter '{algo}': {error}. Check adapter configuration.` | `Failed to instantiate adapter 'a_star': missing required parameter 'heuristic'. Check adapter configuration.` |

### 2.6 Widget System Errors (Enhanced for Hydra-zen)
**Pattern**: `WidgetError: [widget_context] - [issue] - [remedy]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Widget not found | `Widget '{widget}' not found in scene. Available widgets: {available}` | `Widget 'priority_queue' not found in scene. Available widgets: ['grid', 'queue', 'legend']` |
| Widget instantiation | `Failed to instantiate widget '{widget}': {error}. Check widget configuration and _target_.` | `Failed to instantiate widget 'grid': ModuleNotFoundError('agloviz.widgets.pathfinding'). Check widget configuration and _target_.` |
| Action not found | `Widget '{widget}' has no action '{action}'. Available actions: {available}` | `Widget 'grid' has no action 'invalid_highlight'. Available actions: ['highlight_element', 'mark_start', 'mark_goal']` |
| Parameter mismatch | `Widget action '{widget}.{action}' received invalid parameters: {error}` | `Widget action 'grid.highlight_element' received invalid parameters: missing required argument 'index'` |

### 2.7 Scene Configuration Errors (New)
**Pattern**: `SceneError: [scene_context] - [configuration_issue] - [fix]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Scene not found | `Scene configuration '{scene}' not found in ConfigStore. Available: {available}` | `Scene configuration 'invalid_scene' not found in ConfigStore. Available: ['bfs_pathfinding', 'dfs_pathfinding', 'quicksort']` |
| Widget spec invalid | `Invalid widget spec for '{widget}' in scene '{scene}': {error}` | `Invalid widget spec for 'grid' in scene 'bfs_pathfinding': missing '_target_' field` |
| Event binding invalid | `Invalid event binding for event '{event}' in scene '{scene}': {error}` | `Invalid event binding for event 'enqueue' in scene 'bfs_pathfinding': widget 'invalid_widget' not found in scene` |
| Parameter template error | `Parameter template error in event binding '{event}' -> '{widget}.{action}': {template_error}` | `Parameter template error in event binding 'enqueue' -> 'queue.add_element': failed to resolve '${event_data:event.invalid_field}'` |

### 2.8 ConfigStore Errors (New)
**Pattern**: `ConfigStoreError: [operation] - [issue] - [solution]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Registration conflict | `Config '{config_name}' already registered in group '{group}'. Use different name or override=True.` | `Config 'bfs_pathfinding' already registered in group 'scene'. Use different name or override=True.` |
| Group not found | `ConfigStore group '{group}' has no configurations. Available groups: {available}` | `ConfigStore group 'invalid_group' has no configurations. Available groups: ['scene', 'widget', 'storyboard']` |
| Config validation | `Config '{config_name}' failed validation: {validation_error}` | `Config 'scene/bfs_pathfinding' failed validation: widget 'grid' missing required '_target_' field` |
| Dependency missing | `Config '{config_name}' depends on '{dependency}' which is not registered` | `Config 'scene/custom_scene' depends on 'widget/custom_widget' which is not registered` |

## 3. Error Context Enhancement (Hydra-zen)

### 3.1 Structured Config Context
```python
class HydraZenErrorContext:
    """Enhanced error context for hydra-zen operations."""
    
    def __init__(self, config_name: str = None, config_group: str = None, 
                 operation: str = None, template: str = None):
        self.config_name = config_name
        self.config_group = config_group
        self.operation = operation
        self.template = template
    
    def format_error(self, error_type: str, message: str, suggestion: str = None) -> str:
        """Format error with hydra-zen context."""
        context_parts = []
        
        if self.config_group and self.config_name:
            context_parts.append(f"Config: {self.config_group}/{self.config_name}")
        elif self.config_name:
            context_parts.append(f"Config: {self.config_name}")
        
        if self.operation:
            context_parts.append(f"Operation: {self.operation}")
        
        if self.template:
            context_parts.append(f"Template: {self.template}")
        
        context_str = " | ".join(context_parts)
        
        error_msg = f"{error_type}: {context_str} - {message}"
        
        if suggestion:
            error_msg += f"\nSuggestion: {suggestion}"
        
        return error_msg
```

### 3.2 Enhanced Error Suggestions
```python
def suggest_config_fix(config_name: str, error: Exception) -> str:
    """Provide specific suggestions for config errors."""
    cs = ConfigStore.instance()
    repo = cs.get_repo()
    
    if "not found" in str(error).lower():
        # Suggest similar config names
        available = list(repo.keys())
        suggestions = [name for name in available if config_name.lower() in name.lower()]
        return f"Did you mean one of: {suggestions[:3]}?"
    
    elif "_target_" in str(error).lower():
        return "Add '_target_: path.to.Class' field to your configuration"
    
    elif "instantiate" in str(error).lower():
        return "Check that the _target_ class exists and all required parameters are provided"
    
    return "Check configuration syntax and parameter values"

def suggest_template_fix(template: str, error: Exception) -> str:
    """Provide specific suggestions for template errors."""
    if "resolver" in str(error).lower():
        available_resolvers = ["event_data", "timing_value", "config_value", "widget_state"]
        return f"Use one of the available resolvers: {available_resolvers}"
    
    elif "event" in template and "not found" in str(error).lower():
        return "Check that event data contains the referenced field"
    
    elif "timing" in template:
        valid_timing_keys = ["ui", "events", "effects", "waits"]
        return f"Use valid timing keys: {valid_timing_keys}"
    
    return "Check template syntax: ${resolver:path.to.value}"
```

## 4. Error Recovery Strategies (Enhanced)

### 4.1 Hydra-zen Error Recovery
```python
class HydraZenErrorRecovery:
    """Error recovery strategies for hydra-zen operations."""
    
    @staticmethod
    def recover_from_instantiation_error(config, error: Exception):
        """Attempt to recover from instantiation errors."""
        if "missing" in str(error).lower() and "parameter" in str(error).lower():
            # Try with minimal parameters
            try:
                return instantiate(config, _partial_=True)
            except:
                pass
        
        elif "_target_" in str(error).lower():
            # Try to suggest alternative targets
            target = getattr(config, '_target_', 'unknown')
            suggestions = HydraZenErrorRecovery._suggest_alternative_targets(target)
            raise ValueError(f"Target '{target}' not found. Try: {suggestions}")
        
        # Re-raise original error if no recovery possible
        raise error
    
    @staticmethod
    def _suggest_alternative_targets(invalid_target: str) -> list[str]:
        """Suggest alternative targets based on common patterns."""
        suggestions = []
        
        if "widgets" in invalid_target:
            if "grid" in invalid_target.lower():
                suggestions.extend([
                    "agloviz.widgets.structures.ArrayWidget",
                    "agloviz.widgets.domains.pathfinding.PathfindingGrid"
                ])
            elif "queue" in invalid_target.lower():
                suggestions.extend([
                    "agloviz.widgets.structures.QueueWidget",
                    "agloviz.widgets.structures.StackWidget"
                ])
        
        return suggestions[:3]  # Limit to top 3 suggestions

    @staticmethod
    def recover_from_template_error(template: str, context: dict, error: Exception):
        """Attempt to recover from template resolution errors."""
        # Try with fallback values
        fallback_values = {
            "event_data:event.node": "(0, 0)",
            "timing_value:events": "0.8",
            "config_value:theme.color": "#FFFFFF"
        }
        
        for pattern, fallback in fallback_values.items():
            if pattern in template:
                return fallback
        
        # Return empty string as last resort
        return ""
```

### 4.2 ConfigStore Error Recovery
```python
class ConfigStoreErrorRecovery:
    """Error recovery for ConfigStore operations."""
    
    @staticmethod
    def suggest_config_alternatives(requested_config: str) -> list[str]:
        """Suggest alternative configurations when requested config not found."""
        cs = ConfigStore.instance()
        repo = cs.get_repo()
        
        # Extract group and name
        if "/" in requested_config:
            group, name = requested_config.split("/", 1)
            
            # Find similar configs in same group
            group_configs = [key for key in repo.keys() if key.startswith(f"{group}/")]
            
            # Fuzzy match on name
            suggestions = []
            for config_key in group_configs:
                config_name = config_key.split("/", 1)[1]
                if name.lower() in config_name.lower() or config_name.lower() in name.lower():
                    suggestions.append(config_key)
            
            return suggestions[:5]
        
        return []
    
    @staticmethod
    def validate_config_dependencies(config_name: str) -> list[str]:
        """Validate that config dependencies are available."""
        cs = ConfigStore.instance()
        repo = cs.get_repo()
        
        if config_name not in repo:
            return [f"Config '{config_name}' not found"]
        
        config = repo[config_name].node
        missing_deps = []
        
        # Check _target_ dependency
        if hasattr(config, '_target_'):
            target = getattr(config, '_target_')
            try:
                # Try to import the target
                module_path, class_name = target.rsplit('.', 1)
                import importlib
                module = importlib.import_module(module_path)
                getattr(module, class_name)
            except (ImportError, AttributeError):
                missing_deps.append(f"Target class '{target}' not available")
        
        return missing_deps
```

## 5. Error Message Templates (Complete)

### 5.1 Hydra-zen Specific Templates
```python
HYDRA_ZEN_ERROR_TEMPLATES = {
    "missing_target": "Configuration '{config}' missing '_target_' field. Add '_target_: path.to.Class' to specify the class to instantiate.",
    
    "invalid_target": "Cannot import '{target}' specified in '{config}'. Check that the module exists and the class is correctly named.",
    
    "instantiation_failed": "Failed to instantiate '{target}' from config '{config}': {error}. Verify all required parameters are provided.",
    
    "configstore_not_found": "Configuration '{config}' not found in ConfigStore. Available configurations:\n{available_list}",
    
    "template_resolution_failed": "Template '{template}' failed to resolve: {error}. Check that the referenced data exists in the current context.",
    
    "resolver_not_found": "Resolver '{resolver}' not registered. Available resolvers: {available_resolvers}. Register custom resolvers with OmegaConf.register_new_resolver().",
    
    "zen_partial_recommended": "Configuration '{config}' should use zen_partial=True to allow runtime parameter overrides.",
    
    "config_composition_error": "Error composing configurations: {error}. Check that all referenced configs exist and have compatible schemas."
}

def format_hydra_zen_error(error_key: str, **kwargs) -> str:
    """Format hydra-zen specific error message."""
    template = HYDRA_ZEN_ERROR_TEMPLATES.get(error_key, "Unknown hydra-zen error: {error}")
    return template.format(**kwargs)
```

## 6. Diagnostic Tools (Enhanced)

### 6.1 ConfigStore Diagnostic Tool
```python
def diagnose_configstore_state():
    """Diagnose ConfigStore state and potential issues."""
    cs = ConfigStore.instance()
    repo = cs.get_repo()
    
    print("📊 ConfigStore Diagnostic Report")
    print("=" * 40)
    
    # Group analysis
    groups = {}
    for config_name in repo.keys():
        if "/" in config_name:
            group = config_name.split("/")[0]
            groups[group] = groups.get(group, 0) + 1
    
    print("📋 Configuration Groups:")
    for group, count in groups.items():
        print(f"  {group}: {count} configurations")
    
    # Validation analysis
    print("\n🔍 Configuration Validation:")
    valid_configs = 0
    invalid_configs = []
    
    for config_name in repo.keys():
        try:
            config = repo[config_name].node
            if hasattr(config, '_target_'):
                # Try to validate target exists
                target = getattr(config, '_target_')
                module_path, class_name = target.rsplit('.', 1)
                import importlib
                module = importlib.import_module(module_path)
                getattr(module, class_name)
            valid_configs += 1
        except Exception as e:
            invalid_configs.append((config_name, str(e)))
    
    print(f"  ✅ Valid: {valid_configs}")
    print(f"  ⚠️ Invalid: {len(invalid_configs)}")
    
    if invalid_configs:
        print("\n❌ Invalid Configurations:")
        for config_name, error in invalid_configs[:5]:  # Show first 5
            print(f"  - {config_name}: {error}")

def diagnose_template_syntax():
    """Diagnose parameter template syntax across configurations."""
    from agloviz.core.resolvers import validate_resolver_syntax, get_available_resolvers
    
    cs = ConfigStore.instance()
    repo = cs.get_repo()
    
    print("🔍 Template Syntax Diagnostic")
    print("=" * 30)
    
    available_resolvers = get_available_resolvers()
    print(f"📋 Available Resolvers: {list(available_resolvers.keys())}")
    
    template_issues = []
    
    for config_name in repo.keys():
        config = repo[config_name].node
        # Would need to recursively check all string values for templates
        # This is a simplified version
        if hasattr(config, 'params'):
            params = getattr(config, 'params', {})
            for key, value in params.items():
                if isinstance(value, str) and value.startswith("${"):
                    if not validate_resolver_syntax(value):
                        template_issues.append((config_name, key, value))
    
    if template_issues:
        print(f"\n⚠️ Template Issues Found: {len(template_issues)}")
        for config_name, param_key, template in template_issues[:5]:
            print(f"  - {config_name}.{param_key}: {template}")
    else:
        print("\n✅ All templates use valid syntax")
```

---

## Summary

This enhanced Error Taxonomy v2.0 provides comprehensive error handling patterns for the hydra-zen first ALGOViz architecture, including:

1. **Hydra-zen Specific Error Categories**: ConfigStore, structured config, and parameter template errors
2. **Enhanced Error Context**: Detailed context information for hydra-zen operations
3. **Recovery Strategies**: Automatic error recovery and suggestion systems
4. **Diagnostic Tools**: ConfigStore and template syntax diagnostic utilities
5. **Comprehensive Error Templates**: Ready-to-use error message templates for all hydra-zen scenarios

The error system ensures users receive actionable, contextual feedback for all hydra-zen configuration and instantiation issues while maintaining consistency with the overall ALGOViz error handling philosophy.
