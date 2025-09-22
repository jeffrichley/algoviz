# Preview and Partial Rendering for ALGOViz

## Overview

This document outlines options for implementing preview and partial rendering capabilities in ALGOViz, inspired by common practices in animation and rendering tools like Manim, Maya, and other 3D graphics software.

## Current State

**New CLI (`render-zen`)**: Full hydra-zen integration with powerful override capabilities
**Old CLI (`render`)**: Has `preview` command with limited frames, but being removed

**Missing Features:**
- ❌ Quick preview with limited frames
- ❌ Partial algorithm execution
- ❌ Fast iteration for testing configurations

## Proposed Solutions

### Option 1: Quality-Based Preview (Easiest Implementation)

Use existing quality settings for faster previews:

```bash
# Draft quality for quick preview
uv run render-zen timing=draft renderer=draft

# Medium quality for testing
uv run render-zen timing=fast renderer=medium

# Full quality for final output
uv run render-zen timing=normal renderer=hd
```

**Pros:**
- ✅ Uses existing infrastructure
- ✅ No code changes needed
- ✅ Works immediately

**Cons:**
- ❌ Still renders full algorithm
- ❌ May not be fast enough for quick iteration

### Option 2: Frame Limiting (Recommended)

Add frame-based limiting parameters:

```bash
# Render only first 60 frames
uv run render-zen +max_frames=60

# Render specific frame range
uv run render-zen +start_frame=30 +end_frame=90

# Render every 5th frame
uv run render-zen +frame_step=5
```

**Implementation:**
- Add `max_frames`, `start_frame`, `end_frame`, `frame_step` parameters
- Modify renderer to stop after specified frames
- Useful for testing visual effects and timing

**Pros:**
- ✅ Fast feedback for visual testing
- ✅ Flexible frame control
- ✅ Easy to understand

**Cons:**
- ❌ May cut off mid-algorithm
- ❌ Doesn't show complete algorithm behavior

### Option 3: Algorithm Step Limiting (Most Useful for ALGOViz)

Limit by algorithm execution steps:

```bash
# Render only first 10 algorithm steps
uv run render-zen +max_steps=10

# Render specific step range
uv run render-zen +start_step=5 +end_step=15

# Render every 3rd step
uv run render-zen +step_interval=3
```

**Implementation:**
- Add `max_steps`, `start_step`, `end_step`, `step_interval` parameters
- Modify algorithm adapters to stop after specified steps
- Perfect for algorithm development and testing

**Pros:**
- ✅ Algorithm-specific (perfect for ALGOViz)
- ✅ Shows complete algorithm behavior up to limit
- ✅ Great for debugging algorithm logic
- ✅ Fast iteration for algorithm development

**Cons:**
- ❌ Requires changes to algorithm adapters
- ❌ More complex implementation

### Option 4: Hybrid Approach (Best of All Worlds)

Combine multiple limiting strategies:

```bash
# Quick preview: draft quality + limited steps
uv run render-zen timing=draft +max_steps=10 output_path=preview.mp4

# Visual test: medium quality + limited frames
uv run render-zen renderer=medium +max_frames=60 output_path=visual_test.mp4

# Algorithm test: normal quality + limited steps
uv run render-zen +max_steps=20 output_path=algorithm_test.mp4

# Full render: high quality + all steps
uv run render-zen renderer=hd output_path=final.mp4
```

## Implementation Plan

### Phase 1: Basic Frame Limiting
1. Add `max_frames` parameter to render function
2. Modify renderer to stop after specified frames
3. Test with existing algorithms

### Phase 2: Algorithm Step Limiting
1. Add `max_steps` parameter to algorithm adapters
2. Modify BFSAdapter and other adapters to respect step limits
3. Add step counting to event generation

### Phase 3: Advanced Options
1. Add `start_frame`, `end_frame`, `start_step`, `end_step` parameters
2. Add `frame_step`, `step_interval` for sampling
3. Add preview-specific output naming

### Phase 4: Integration
1. Add preview examples to documentation
2. Create preview presets (quick, visual, algorithm, final)
3. Add preview mode to help output

## Technical Details

### Frame Limiting Implementation
```python
def render_algorithm_video(
    # ... existing parameters ...
    max_frames: int = None,
    start_frame: int = 0,
    end_frame: int = None,
    frame_step: int = 1
):
    # Modify renderer to respect frame limits
    if max_frames:
        end_frame = start_frame + max_frames
    
    # Render with frame limits
    result = renderer.render_with_limits(
        start_frame=start_frame,
        end_frame=end_frame,
        frame_step=frame_step
    )
```

### Step Limiting Implementation
```python
def render_algorithm_video(
    # ... existing parameters ...
    max_steps: int = None,
    start_step: int = 0,
    end_step: int = None,
    step_interval: int = 1
):
    # Modify algorithm execution
    if max_steps:
        end_step = start_step + max_steps
    
    # Run algorithm with step limits
    events = algorithm.run_with_limits(
        start_step=start_step,
        end_step=end_step,
        step_interval=step_interval
    )
```

## Usage Examples

### Quick Preview
```bash
# Test if configuration works
uv run render-zen scene=bfs_advanced +max_steps=5 output_path=quick_test.mp4
```

### Visual Testing
```bash
# Test visual effects and timing
uv run render-zen scene=bfs_advanced +max_frames=60 renderer=medium output_path=visual_test.mp4
```

### Algorithm Development
```bash
# Debug algorithm logic
uv run render-zen +max_steps=10 +start_step=5 output_path=debug.mp4
```

### Final Render
```bash
# Full quality render
uv run render-zen scene=bfs_advanced renderer=hd output_path=final.mp4
```

## Benefits

1. **Faster Iteration**: Quick feedback for configuration testing
2. **Algorithm Development**: Test algorithm logic without full render
3. **Visual Testing**: Test visual effects and timing
4. **Resource Efficiency**: Use fewer resources for testing
5. **Flexibility**: Multiple limiting strategies for different use cases

## Future Enhancements

1. **Preview Presets**: Predefined preview configurations
2. **Interactive Preview**: Real-time preview during development
3. **Preview Comparison**: Side-by-side comparison of different configs
4. **Preview Gallery**: Collection of preview examples
5. **Auto-Preview**: Automatic preview generation for config changes

## Conclusion

Implementing preview and partial rendering capabilities will significantly improve the ALGOViz development experience by providing:
- Fast feedback for configuration testing
- Efficient algorithm development workflow
- Flexible rendering options for different use cases
- Better resource utilization

The recommended approach is to start with **Option 3 (Algorithm Step Limiting)** as it's most relevant to ALGOViz's use case, then add **Option 2 (Frame Limiting)** for visual testing, and finally implement **Option 4 (Hybrid Approach)** for maximum flexibility.
