# ALGOViz Documentation Index

This directory contains the complete design and planning documentation for ALGOViz, a modular framework for generating narrated algorithm visualization videos.

## 📚 Document Overview

### Core Documents (Read First)

**1. [ALGOViz_Vision_Goals.md](ALGOViz_Vision_Goals.md)**  
Establishes the project vision, core principles, and long-term goals for ALGOViz as a world-class algorithm storytelling platform.

**2. [ALGOViz_PRD.md](ALGOViz_PRD.md)**  
Product Requirements Document defining user-facing features, success criteria, and phased development roadmap from MVP through Phase 5.

**3. [ALGOViz_SDD.md](ALGOViz_SDD.md)**  
System Design Document covering the complete technical architecture, data flow, and integration patterns for the modular framework.

### Architecture & Core Systems

**4. [ALGOViz_Design_Storyboard_DSL.md](ALGOViz_Design_Storyboard_DSL.md)**  
Defines the declarative YAML-based language for structuring algorithm visualizations into acts, shots, and beats with narration.

**5. [ALGOViz_Design_Director.md](ALGOViz_Design_Director.md)**  
Central orchestration component that executes storyboards, applies timing rules, and coordinates voiceover synchronization.

**6. [ALGOViz_Design_Voiceover.md](ALGOViz_Design_Voiceover.md)**  
Narration integration system using CoquiTTS with hybrid timing, bookmarks, and subtitle generation capabilities.
- Subtitles: baseline via TimingTracker, optional polish via Whisper.

**7. [ALGOViz_Design_Adapters_VizEvents.md](ALGOViz_Design_Adapters_VizEvents.md)**  
Algorithm adapter pattern and VizEvent system that converts algorithm execution into standardized visualization events.

**8. [ALGOViz_Design_Widgets_Registry.md](ALGOViz_Design_Widgets_Registry.md)**  
Reusable UI component system (QueueView, StackView, HUD, PathTracer) with factory-based registration and lifecycle management.

**9. [ALGOViz_Design_TimingConfig.md](ALGOViz_Design_TimingConfig.md)**  
Centralized timing system providing consistent animation pacing across draft, normal, and fast modes with hybrid timing support.

### Pipeline & Infrastructure

**10. [ALGOViz_Design_Rendering_Export.md](ALGOViz_Design_Rendering_Export.md)**  
End-to-end rendering pipeline converting storyboards into MP4/GIF/PNG artifacts with ffmpeg integration and quality profiles.

**11. [ALGOViz_Design_Config_System.md](ALGOViz_Design_Config_System.md)**  
Configuration management with Pydantic validation, YAML merging, CLI overrides, and precedence rules for reproducible builds.

**12. [ALGOViz_Design_Plugin_System.md](ALGOViz_Design_Plugin_System.md)**  
Extension framework enabling third-party algorithms, widgets, and themes through entry points with versioning and error isolation.

**13. [ALGOViz_Design_CLI_DevUX.md](ALGOViz_Design_CLI_DevUX.md)**  
Command-line interface design with Typer implementation, comprehensive flags, error messaging, and developer workflow optimization.

### Advanced Topics

**14. [ALGOViz_Design_DI_Strategy.md](ALGOViz_Design_DI_Strategy.md)**  
Dependency injection architecture using Hydra + hydra-zen + OmegaConf for configuration-driven object construction and lifecycle management.

**15. [ALGOViz_Scenario_Theme_Merge_Precedence.md](ALGOViz_Scenario_Theme_Merge_Precedence.md)**  
Concrete example of configuration merging with scenario.yaml + timing.yaml + theme.yaml + CLI overrides including before/after snippets.

**16. [ALGOViz_Error_Taxonomy.md](ALGOViz_Error_Taxonomy.md)**  
Comprehensive error classification system with consistent messaging, remediation guidance, and actionable feedback across all components.

---

## 🎯 Recommended Reading Order

### For New Contributors
Start with **Vision & Goals** → **PRD** → **SDD** to understand the project's purpose, requirements, and overall architecture.

### For System Architects
Focus on **SDD** → **DI Strategy** → **Config System** → **Plugin System** for the core technical foundation.

### For Algorithm Developers
Read **Adapters & VizEvents** → **Storyboard DSL** → **TimingConfig** → **CLI & DevUX** for the development workflow.

### For UI/Rendering Work
Study **Widgets & Registry** → **Director** → **Rendering & Export** → **Voiceover** for the visualization pipeline.

### For Configuration & DevOps
Review **Config System** → **Scenario/Theme Merge** → **CLI & DevUX** → **Error Taxonomy** for operational concerns.

---

## 📝 Contributing to Documentation

### Style Guidelines
- Use **ALGOViz** (not ALGOViz) for brand consistency in titles and prose
- Preserve `algoviz` lowercase in code blocks and technical identifiers  
- Include concrete examples with YAML/Python code snippets
- Structure with clear sections: Purpose, Non-Goals, Requirements, Implementation
- Add cross-references to related documents using exact filenames

### Linking Standards
- Internal links: `[Document Title](ALGOViz_Design_Component.md)`
- Section anchors: `[Config System](ALGOViz_Design_Config_System.md#precedence-rules)`
- External references: Include full URLs for specifications and dependencies

### Update Policy
- Mark documents with **Status:** Draft/Review/Approved and **Last Updated:** AUTO
- Update cross-references when renaming files or sections
- Maintain backward compatibility in public APIs documented here
- Run brand normalization scripts when making bulk changes

### Quality Checklist
- [ ] Document follows the established template structure
- [ ] All code examples are syntactically correct and tested
- [ ] Cross-references point to existing files and sections
- [ ] Technical decisions are clearly justified with rationale
- [ ] Examples include both success and failure scenarios

---

**Total Documents:** 16 design documents covering the complete ALGOViz architecture  
**Last Updated:** 2025-01-20  
**Maintainer:** Development Team
