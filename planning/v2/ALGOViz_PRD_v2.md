# ALGOViz Product Requirements Document (PRD) v2.0

**Owner:** Development Team  
**Status:** Current (Architecture v2.0)  
**Last Updated:** 2025-09-21
**Version:** v2.0 (Updated for Widget Architecture v2.0 - clean architecture phases)
**Supersedes:** planning/v1/ALGOViz_PRD.md

---

## 1. Purpose
This document defines the product requirements for ALGOViz, a modular framework for generating narrated algorithm visualization videos. It describes the **user-facing features** that the system must deliver across phases (MVP → Phase 5) using the clean Widget Architecture v2.0.

The audience for this PRD includes educators, content creators, students, and contributors.

---

## 2. Product Overview
ALGOViz enables users to:
- Choose an algorithm (BFS, DFS, A*, etc.).
- Choose a scenario (grid, maze, graph).
- Render a **high-quality visualization video** with narration, subtitles, and consistent timing.
- Extend the system with new algorithms or narration scripts easily.

Example MVP experience:
```
agloviz render --algo bfs --scenario maze.yaml --with-voiceover
```
Output: A narrated video of BFS solving the maze, with optional subtitles.

---

## 3. User Stories

### 3.1 Educator
> As an educator, I want to generate algorithm videos with narration so I can teach complex concepts more effectively.

### 3.2 Content Creator
> As a content creator, I want customizable storyboards and voiceover options so I can produce unique, branded algorithm explainers.

### 3.3 Student
> As a student, I want clear visuals with synchronized narration and subtitles so I can follow algorithm steps at my own pace.

### 3.4 Contributor
> As a contributor, I want to add new algorithms via adapters and storyboards without modifying the core system.

---

## 4. Requirements by Phase (Updated for v2.0)

### **Phase 1 (MVP - Clean Architecture Foundation)**
- **CLI Tooling**: `agloviz render`, `agloviz algo list`, `agloviz preview`.
- **Algorithm Support**: BFS using clean widget architecture.
- **Storyboard DSL**: Acts → Shots → Beats with scene configuration integration.
- **Director**: Pure orchestrator using SceneEngine.
- **Widgets**: Multi-level hierarchy (primitives, data structures, domain-specific).
- **Scene Configuration**: Event binding system with parameter templates.
- **Timing System**: Centralized config (`draft`, `normal`, `fast` modes).
- **Voiceover (Scaffold)**: Narration fields in storyboard, CLI flag `--with-voiceover`. **Silent by default**. CoquiTTS is the default backend.
- **Testing/CI**: Deterministic VizEvents, preview GIF generation, timing CSV export.

### **Phase 2 (Widget Architecture Foundation)**
- **Widget Architecture Foundation**: Complete multi-level widget hierarchy.
- **Generic Widget Library**: ArrayWidget, QueueWidget, StackWidget, TreeWidget.
- **Layout Engines**: Positioning and arrangement systems.
- **Scene Configuration System**: Complete declarative event binding.
- **Plugin System**: Widget plugins with scene configuration integration.
- **Framework Completion**: Clean, generic foundation ready for algorithms.

### **Phase 3 (Additional Algorithms)**
- **Additional Algorithms**: DFS, Dijkstra, A* using clean architecture.
- **Algorithm-Specific Scene Configurations**: Domain-specific scene configs.
- **Domain-Specific Widgets**: PathfindingGrid, SortingArray, TreeVisualizer.
- **Multi-Algorithm Validation**: Prove architecture works across algorithm types.
- **Scenarios**: Multiple grid/maze YAMLs with different start/goal setups.
- **Themes**: Visual palettes, roles (visited, frontier, goal, etc.).

### **Phase 4 (Full Integration)**
- **Full Voiceover Integration**: CoquiTTS voiceover service enabled.
- **Subtitles**: Export `.srt` files auto-generated from narration fields.
- **Hybrid Timing Enforcement**: Ensure narration and visuals remain synchronized across all beats.
- **Configurable Narration**: Inline YAML narration plus optional external files for localization.
- **Improved CLI**: `--quality`, `--frames`, `--output-format` options.

### **Phase 5 (Advanced Features)**
- **Plugin System Extension**: External algorithms discoverable via registry.
- **Expanded Algorithm Library**: Sorting algorithms, graph algorithms, etc.
- **Advanced Scenarios**: Graphs beyond grids, weighted edges.
- **Export Formats**: Support for GIF, MP4, and image sequences.
- **Contribution Templates**: Developer guide + templates for new algorithms.

### **Phase 6 (Professional Features)**
- **Bookmark Routing**: Word-level sync between narration and visuals.
- **Interactive Narration**: Ability to pause/resume narration while visuals continue.
- **Localization**: Multi-language narration and subtitles.
- **Educator Packs**: Prebuilt sets of videos with consistent branding and narration styles.
- **Integration Hooks**: APIs for embedding ALGOViz visualizations into external learning platforms.

---

## 5. Widget Architecture v2.0 Integration

### 5.1 Multi-Level Widget Hierarchy
**Level 1: Visual Primitives**
- TokenWidget, LineWidget, CircleWidget, TextWidget
- Direct Manim integration for rendering

**Level 2: Data Structure Widgets**
- ArrayWidget, QueueWidget, StackWidget, TreeWidget
- Generic operations: `add_element`, `remove_element`, `highlight_element`

**Level 3: Domain-Specific Extensions**
- PathfindingGrid, SortingArray, GraphVisualizer
- Algorithm-family-specific semantics

### 5.2 Scene Configuration System
- **Declarative Event Binding**: VizEvents → Widget actions via configuration
- **Parameter Templates**: Runtime resolution of event data
- **Algorithm Separation**: Algorithm logic separate from visual operations
- **Plugin Integration**: Scene configurations as plugin extension points

### 5.3 Clean Architecture Benefits
- **Zero Algorithm Pollution**: Generic components support any algorithm type
- **Extensibility**: New algorithms via scene configurations, no core changes
- **Maintainability**: Clear separation of concerns across all components
- **Testability**: Independent testing of visual and algorithm components

---

## 6. Out of Scope (for now)
- Interactive UI (play/pause inside videos) — post Phase 6.  
- Live demos where algorithms run in real-time instead of pre-rendered.  
- Multiplayer collaboration on storyboards.  

---

## 7. Success Criteria (Updated for v2.0)
- **Phase 1**: A user can render a BFS video using clean widget architecture.  
- **Phase 2**: Widget foundation supports any algorithm type without modification.
- **Phase 3**: At least 3 algorithms supported with reusable scene configurations.  
- **Phase 4**: Narrated videos generate synchronized subtitles automatically.  
- **Phase 5**: Contributors can add new algorithms without touching core code.  
- **Phase 6**: Narration bookmarks trigger visual sync in real time.

---

## 8. Architecture Compliance Requirements

### 8.1 Widget Architecture v2.0 Compliance
- All widgets must follow multi-level hierarchy
- No algorithm-specific methods in generic widgets
- Scene configuration integration required for all algorithms
- Parameter template system for event binding

### 8.2 Clean Architecture Principles
- Zero algorithm-specific pollution in core components
- Configuration-driven behavior, not hard-coded logic
- Plugin-ready extensibility without core modifications
- Clear separation between visual operations and algorithm semantics

### 8.3 Quality Standards
- Google-level documentation and code quality
- Comprehensive testing at each architectural level
- Consistent naming conventions across all components
- Production-ready error handling and diagnostics

---

# ✅ Summary
ALGOViz will evolve in clear, incremental phases with Widget Architecture v2.0 as the foundation.  
Phase 1 establishes clean architecture with BFS + scene configurations.  
Phase 2 completes the widget foundation for universal algorithm support.
Subsequent phases expand algorithms, narration, and plugins until ALGOViz becomes a **world-class, narrated algorithm visualization framework** with pristine architecture.

---
