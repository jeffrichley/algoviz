# ALGOViz Product Requirements Document (PRD)

## 1. Purpose
This document defines the product requirements for ALGOViz, a modular framework for generating narrated algorithm visualization videos. It describes the **user-facing features** that the system must deliver across phases (MVP → Phase 5).

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

## 4. Requirements by Phase

### **MVP (Phase 0–1)**
- **CLI Tooling**: `agloviz render`, `agloviz algo list`, `agloviz preview`.
- **Algorithm Support**: BFS fully migrated to new architecture.
- **Storyboard DSL**: Acts → Shots → Beats with `action`, `args`, `narration`, `bookmarks` scaffolded.
- **Director**: Executes storyboard, applies timing rules (hybrid timing).
- **Widgets**: QueueView, Grid, HUD, Legend.
- **Timing System**: Centralized config (`draft`, `normal`, `fast` modes).
- **Voiceover (Scaffold)**: Narration fields in storyboard, CLI flag `--with-voiceover`. **Silent by default**. CoquiTTS is the default backend.
- **Testing/CI**: Deterministic VizEvents, preview GIF generation, timing CSV export.

### **Phase 2**
- **Additional Algorithms**: DFS, Dijkstra, A*.
- **Reusable Widgets**: StackView, PriorityQueueView, PathTracer.
- **Scenarios**: Multiple grid/maze YAMLs with different start/goal setups.
- **Themes**: Visual palettes, roles (visited, frontier, goal, etc.).
- **Improved CLI**: `--quality`, `--frames`, `--output-format` options.

### **Phase 3**
- **Full Voiceover Integration**: CoquiTTS voiceover service enabled.
- **Subtitles**: Export `.srt` files auto-generated from narration fields.
- **Hybrid Timing Enforcement**: Ensure narration and visuals remain synchronized across all beats.
- **Configurable Narration**: Inline YAML narration plus optional external files for localization.

### **Phase 4**
- **Plugin System**: External algorithms discoverable via registry.
- **Expanded Algorithm Library**: Sorting algorithms, graph algorithms, etc.
- **Advanced Scenarios**: Graphs beyond grids, weighted edges.
- **Export Formats**: Support for GIF, MP4, and image sequences.
- **Contribution Templates**: Developer guide + templates for new algorithms.

### **Phase 5**
- **Bookmark Routing**: Word-level sync between narration and visuals.
- **Interactive Narration**: Ability to pause/resume narration while visuals continue.
- **Localization**: Multi-language narration and subtitles.
- **Educator Packs**: Prebuilt sets of videos with consistent branding and narration styles.
- **Integration Hooks**: APIs for embedding ALGOViz visualizations into external learning platforms.

---

## 5. Out of Scope (for now)
- Interactive UI (play/pause inside videos) — post Phase 5.  
- Live demos where algorithms run in real-time instead of pre-rendered.  
- Multiplayer collaboration on storyboards.  

---

## 6. Success Criteria
- MVP: A user can render a BFS video with a scenario and (optionally) narration.  
- Phase 2: At least 3 algorithms supported with reusable widgets.  
- Phase 3: Narrated videos generate synchronized subtitles automatically.  
- Phase 4: Contributors can add new algorithms without touching core code.  
- Phase 5: Narration bookmarks trigger visual sync in real time.

---

# ✅ Summary
ALGOViz will evolve in clear, incremental phases.  
MVP ensures a working pipeline with BFS + storyboards.  
Subsequent phases expand algorithms, widgets, narration, and plugins until ALGOViz becomes a **world-class, narrated algorithm visualization framework**.
