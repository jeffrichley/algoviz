# ALGOViz Error Taxonomy & Messages

**Owner:** Iris  
**Status:** Draft (approved by Jeff)  
**Last Updated:** AUTO

---

## 1. Purpose
Define consistent error messages, remediation guidance, and failure modes across all ALGOViz components. Ensures users receive actionable, contextual feedback with consistent terminology and helpful suggestions.

## 2. Error Categories

### 2.1 Configuration Errors
**Pattern**: `ConfigError: [context] - [specific issue] - [remedy]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Unknown config key | `Unknown config key '{key}' in {file}:{line}. Valid keys: {suggestions}` | `Unknown config key 'timing.foo' in scenario.yaml:12. Valid keys: ui, events, effects, waits` |
| Type mismatch | `Expected {expected_type} for '{key}' in {file}:{line}, got {actual_type}` | `Expected int for 'width' in maze.yaml:3, got str` |
| Missing required field | `Missing required field '{field}' in {file}:{line}` | `Missing required field 'start' in scenario.yaml:8` |
| Invalid enum value | `Invalid value '{value}' for '{key}'. Valid options: {options}` | `Invalid value 'ultra' for 'quality'. Valid options: draft, medium, high` |

### 2.2 Storyboard Errors
**Pattern**: `StoryboardError: [location] - [issue] - [suggestion]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Unknown action | `Unknown action '{action}' at Act {act}/Shot {shot}/Beat {beat}. Did you mean '{suggestion}'?` | `Unknown action 'trace_paht' at Act 2/Shot 1/Beat 3. Did you mean 'trace_path'?` |
| Missing action args | `Action '{action}' at Act {act}/Shot {shot}/Beat {beat} missing required args: {missing_args}` | `Action 'show_title' at Act 1/Shot 1/Beat 1 missing required args: text` |
| Invalid action args | `Action '{action}' at Act {act}/Shot {shot}/Beat {beat} has invalid arg '{arg}': {reason}` | `Action 'show_widgets' at Act 2/Shot 1/Beat 1 has invalid arg 'queue': expected bool, got str` |

### 2.3 Algorithm Adapter Errors
**Pattern**: `AdapterError: [{algorithm}] - [step_context] - [issue]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Adapter crash | `Algorithm '{algo}' crashed at step {step}: {error}. Try with minimal scenario for debugging.` | `Algorithm 'bfs' crashed at step 15: KeyError('neighbors'). Try with minimal scenario for debugging.` |
| Unknown algorithm | `Unknown algorithm '{algo}'. Available: {available_algos}` | `Unknown algorithm 'bf' Available: bfs, dfs, dijkstra, a_star` |
| Invalid scenario | `Algorithm '{algo}' requires {requirements}, but scenario provides {actual}` | `Algorithm 'dijkstra' requires weighted edges, but scenario provides unweighted grid` |

### 2.4 Scenario Contract Violations
**Pattern**: `ScenarioError: [contract_violation] - [location] - [remedy]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Out of bounds | `{entity} position {pos} is out of bounds for {width}x{height} grid` | `Start position (10, 5) is out of bounds for 8x8 grid` |
| Impassable position | `{entity} position {pos} is not passable (obstacle at location)` | `Goal position (3, 4) is not passable (obstacle at location)` |
| Invalid neighbors | `neighbors({node}) returned invalid position {neighbor}: {reason}` | `neighbors((2,3)) returned invalid position (2,8): out of bounds` |
| Cost function error | `cost({from_node}, {to_node}) failed: {reason}. Ensure nodes are adjacent.` | `cost((0,0), (5,5)) failed: nodes not adjacent. Ensure nodes are adjacent.` |

### 2.5 Widget & Registry Errors
**Pattern**: `RegistryError: [component_type] - [issue] - [available_options]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Unknown widget | `Widget '{widget}' not registered. Available widgets: {available}` | `Widget 'priority_que' not registered. Available widgets: queue, stack, priority_queue, hud` |
| Widget update failure | `Widget '{widget}' update failed for event '{event}': {error}. Skipping beat.` | `Widget 'queue' update failed for event 'enqueue': AttributeError('highlight'). Skipping beat.` |
| Registry collision | `Cannot register '{name}': already registered by {existing_source}` | `Cannot register 'bfs': already registered by core.adapters` |

### 2.6 Rendering & Export Errors
**Pattern**: `RenderError: [stage] - [issue] - [remedy]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Missing dependency | `{tool} not found. Install with: {install_command}` | `ffmpeg not found. Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Ubuntu)` |
| Disk space | `Insufficient disk space for render. Need {required}GB, have {available}GB. Try --output-dir /other/path` | `Insufficient disk space for render. Need 2.3GB, have 0.8GB. Try --output-dir /other/path` |
| Codec not supported | `Codec '{codec}' not supported. Falling back to {fallback}. Install {codec} support for better quality.` | `Codec 'libx265' not supported. Falling back to libx264. Install x265 for better compression.` |
| Font checksum mismatch | `Font checksum mismatch: expected {expected}, got {actual}. Font may be corrupted or replaced.` | `Font checksum mismatch: expected a1b2c3, got d4e5f6. Font may be corrupted or replaced.` |

### 2.7 Voiceover & TTS Errors
**Pattern**: `VoiceoverError: [component] - [issue] - [fallback_action]`

| Error | Message Template | Example |
|-------|------------------|---------|
| TTS backend missing | `TTS backend '{backend}' not available. Falling back to silent mode. Install {backend} for voiceover.` | `TTS backend 'coqui' not available. Falling back to silent mode. Install coqui-tts for voiceover.` |
| Voice not found | `Voice '{voice}' not found for language '{lang}'. Using default voice '{default}'.` | `Voice 'en_UK' not found for language 'en'. Using default voice 'en_US'.` |
| TTS synthesis failed | `TTS failed for beat at Act {act}/Shot {shot}/Beat {beat}: {error}. Continuing with visuals only.` | `TTS failed for beat at Act 1/Shot 2/Beat 3: timeout. Continuing with visuals only.` |

### 2.8 Plugin System Errors
**Pattern**: `PluginError: [{plugin_name}] - [issue] - [action_taken]`

| Error | Message Template | Example |
|-------|------------------|---------|
| Plugin load failure | `Plugin '{plugin}' failed to load: {error}. Skipping plugin. Check plugin compatibility.` | `Plugin 'my_algo_pack' failed to load: ImportError('missing scipy'). Skipping plugin. Check plugin compatibility.` |
| Version incompatibility | `Plugin '{plugin}' requires ALGOViz {required}, but running {current}. Skipping plugin.` | `Plugin 'advanced_widgets' requires ALGOViz >=2.0, but running 1.5. Skipping plugin.` |
| Namespace collision | `Plugin '{plugin}' tried to register '{resource}' but '{existing_plugin}' already provides it. Skipping registration.` | `Plugin 'algo_extras' tried to register 'bfs' but 'core' already provides it. Skipping registration.` |

## 3. Error Message Guidelines

### 3.1 Structure
1. **Error Type**: Clear category (ConfigError, StoryboardError, etc.)
2. **Context**: Where the error occurred (file:line, Act/Shot/Beat, step index)
3. **Specific Issue**: What exactly went wrong
4. **Remediation**: Actionable next steps or suggestions

### 3.2 Tone & Language
- **Be specific**: "Unknown action 'trace_paht'" not "Invalid action"
- **Be helpful**: Include suggestions and alternatives
- **Be actionable**: Tell users what they can do to fix it
- **Be consistent**: Use the same terminology across all components

### 3.3 Suggestion Algorithms
- **Levenshtein distance** for typo suggestions (action names, config keys)
- **Fuzzy matching** for similar available options
- **Context-aware**: Suggest actions commonly used in similar beats

## 4. Integration Points

### 4.1 Error Reporting
```python
class AGLOVizError(Exception):
    def __init__(self, category: str, context: str, issue: str, remedy: str = None):
        self.category = category
        self.context = context  
        self.issue = issue
        self.remedy = remedy
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        msg = f"{self.category}: {self.context} - {self.issue}"
        if self.remedy:
            msg += f" - {self.remedy}"
        return msg
```

### 4.2 CLI Error Display
- **Colors**: Red for errors, yellow for warnings, blue for suggestions
- **Context**: Show relevant file excerpts when possible
- **Exit codes**: Consistent codes for different error categories

### 4.3 Logging Integration
- **Structured logs**: Include error category, context, and remedy in log metadata
- **Debug mode**: Show full stack traces with `--debug`
- **Error aggregation**: Collect multiple config errors before failing

## 5. Testing Strategy
- **Error message regression tests**: Ensure messages don't change unexpectedly
- **Suggestion quality tests**: Verify typo correction and fuzzy matching
- **Internationalization ready**: Structure supports future localization

## 6. Open Questions
- Should we support error message localization in Phase 4+?
- How verbose should stack traces be in non-debug mode?
- Should plugins be able to register custom error message templates?

---
