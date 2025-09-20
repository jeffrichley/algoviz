# ALGOViz Storyboards 📽️

This directory contains storyboard YAML files that define the structure and flow of algorithm visualization videos.

## Storyboard Structure

Storyboards follow a hierarchical structure: **Acts → Shots → Beats**

- **Act**: A major section of the video (e.g., "Introduction", "Algorithm Execution", "Results")
- **Shot**: A sequence of related visual elements within an act
- **Beat**: A single action or operation within a shot

## Example Structure

```yaml
acts:
  - title: "Introduction"
    shots:
      - beats:
          - action: show_title
            args: 
              text: "Algorithm Name"
            narration: "Welcome to this algorithm demonstration."
  
  - title: "Algorithm Execution"
    shots:
      - beats:
          - action: show_widgets
            args: 
              queue: true
              hud: true
          - action: play_events
            args: 
              routing: "algorithm_routing"
            narration: "Watch the algorithm work."
            bookmarks:
              key_word: "widget.action"
```

## Available Actions

| Action | Description | Common Args |
|--------|-------------|-------------|
| `show_title` | Display title card | `text`, `subtitle` |
| `show_grid` | Draw/reveal grid | `width`, `height` |
| `place_start` | Place start position | `pos` |
| `place_goal` | Place goal position | `pos` |
| `place_obstacles` | Render obstacles | `positions` |
| `show_widgets` | Show UI components | `queue`, `hud`, `legend` |
| `play_events` | Stream algorithm events | `routing`, `algorithm` |
| `trace_path` | Visualize path | `highlight_color`, `animate` |
| `show_complexity` | Display complexity info | `time_complexity`, `space_complexity` |
| `celebrate_goal` | Confetti/celebration | `effect` |
| `outro` | Fade out/credits | `fade_duration` |

## Narration and Bookmarks

### Narration
Add narration text to any beat:
```yaml
- action: show_title
  narration: "This video explains how the algorithm works."
```

### Bookmarks
Bookmarks map spoken words to widget actions:
```yaml
- action: play_events
  narration: "We enqueue the starting node."
  bookmarks:
    enqueue: "queue.highlight_frontier"
    starting: "grid.highlight_start"
```

## Validation

Validate your storyboard files using the CLI:
```bash
agloviz validate-storyboard storyboards/my_storyboard.yaml
```

With action validation:
```bash
agloviz validate-storyboard storyboards/my_storyboard.yaml --validate-actions
```

## File Naming Convention

- Use descriptive names: `bfs_demo.yaml`, `dijkstra_weighted.yaml`
- Include algorithm name and scenario type
- Use lowercase with underscores

## Tips for Writing Storyboards

1. **Keep beats focused**: Each beat should do one clear thing
2. **Use meaningful narration**: Write for the target audience
3. **Plan bookmark timing**: Think about when visual highlights should occur
4. **Test incrementally**: Validate your storyboard as you write it
5. **Consider timing**: Use `min_duration` and `max_duration` for critical beats

## Examples

- `bfs_demo.yaml` - Complete BFS demonstration with narration and bookmarks
- More examples will be added as algorithms are implemented

## Future Features

- External narration file support
- Internationalization (i18n) support  
- Template inheritance
- Conditional beats based on scenario properties
