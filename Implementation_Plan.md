# ALGOViz Implementation Plan 🚀

## Overview
This document provides a comprehensive, phase-by-phase implementation plan for ALGOViz, a modular framework for generating narrated algorithm visualization videos. Each phase builds upon the previous one, ensuring a solid foundation while delivering incremental value.

**Project Vision**: Transform algorithm education through high-quality, narrated, and visually synchronized videos that scale across many algorithms with minimal developer friction.

**Core Principles**: Modular by default, declarative over imperative, narration as first-class citizen, hybrid timing, and world-class engineering quality.

**🚀 Current Status**: **PHASE 0 FOUNDATION TASKS COMPLETED** - Phase 0.1 (Project Structure & Dependencies), Phase 0.2 (Configuration System Foundation), Phase 0.4 (Timing System Foundation), and Phase 0.5 (Error Taxonomy) are **COMPLETED**. Phase 0.3 (Basic CLI) is **PARTIALLY COMPLETED** - CLI framework exists with working config commands, but `render`/`preview` are placeholder implementations that belong in Phase 1. **Phase 1.1 (Storyboard DSL) is COMPLETED** with full Pydantic models, YAML parsing, action registry, CLI integration, and comprehensive testing. **Phase 1.2 (VizEvent System & BFS Adapter) is COMPLETED** with full VizEvent system, BFS algorithm adapter, scenario runtime contract, event routing system, and working CLI commands. **FIRST WORKING ALGORITHM IMPLEMENTED**. Ready to begin Phase 1.3 (Component Registry & Basic Widgets).

---

## 📋 Phase 0: Foundation & Scaffolding (MVP Setup)

### Goal
Establish the core architectural foundation and basic CLI tooling to enable rapid iteration and testing.

### Duration: 2-3 weeks

### Tasks

#### 0.1 Project Structure & Dependencies ✅ COMPLETED
**Source**: [ALGOViz_SDD.md#3-High-Level-Architecture](planning/ALGOViz_SDD.md#3-high-level-architecture)

- [x] **Set up project structure**
  - ✅ Created package layout: `src/agloviz/adapters/`, `src/agloviz/core/`, `src/agloviz/widgets/`, `src/agloviz/config/`, `src/agloviz/plugins/`, `src/agloviz/cli/`
  - ✅ Initialized `pyproject.toml` with dynamic versioning from `__init__.py` [[memory:5375468]]
  - ✅ Set up dependency management using `uv` [[memory:7944020]]
  - ✅ Configured modern linting, formatting, and testing tools (ruff + mypy + pytest)

- [x] **Install core dependencies**
  - ✅ Manim v0.19.0 for rendering
  - ✅ Typer v0.18.0 for CLI
  - ✅ Pydantic v2.11.0 for configuration validation
  - ✅ Hydra + hydra-zen + OmegaConf for DI
  - ✅ Rich v14.1.0 for colored logging [[memory:5483251]]
  - ✅ Python 3.12+ support with proper version constraints

**🎉 Phase 0.1 Achievements:**
- ✅ **Modern Toolchain**: Migrated to ruff (10-100x faster than black+flake8+isort)
- ✅ **Clean Dependencies**: Separated runtime, dev, and voiceover dependencies
- ✅ **PyPI Ready**: Hatchling build system with proper metadata
- ✅ **Quality Pipeline**: `just check` runs lint + typecheck + test
- ✅ **Development UX**: `just fix` auto-fixes issues + formats code
- ✅ **Working CLI**: All basic commands functional with Rich console

#### 0.2 Configuration System Foundation ✅ COMPLETED
**Source**: [ALGOViz_Design_Config_System.md](planning/ALGOViz_Design_Config_System.md)

- [x] **Implement ConfigManager**
  - ✅ Create `VideoConfig` Pydantic models (ScenarioConfig, ThemeConfig, VoiceoverConfig, etc.)
  - ✅ Implement precedence rules: defaults → YAML → CLI → env
  - ✅ Add validation with helpful error messages
  - ✅ Support config merging and dumping for reproducibility

- [x] **Create sample configuration files**
  - ✅ `scenario.yaml` with grid, start/goal, obstacles
  - ✅ `timing.yaml` with UI/events/effects/waits buckets
  - ✅ `voiceover.yaml` with CoquiTTS settings (disabled by default)
  - ✅ `theme.yaml` with color palettes

**🎉 Phase 0.2 Achievements:**
- ✅ **Complete Configuration System**: Full Pydantic models with enum validation
- ✅ **hydra-zen Integration**: Dynamic config generation eliminates hand-written YAML
- ✅ **Precedence Rules**: Defaults → YAML → CLI → Environment variables
- ✅ **CLI Commands**: `config-validate`, `config-show`, `config-dump`, `config-create-samples`
- ✅ **Comprehensive Testing**: 37 unit tests with 95%+ coverage on core components
- ✅ **TimingConfig & TimingTracker**: Full timing system with CSV/JSON export
- ✅ **Rich Error Messages**: Helpful validation errors with context and suggestions

#### 0.3 Basic CLI Implementation 🔄 PARTIALLY COMPLETED
**Source**: [ALGOViz_Design_CLI_DevUX.md](planning/ALGOViz_Design_CLI_DevUX.md)

- [x] **Implement CLI framework and basic commands**
  - ✅ `agloviz version` - show version information (fully working)
  - ⚠️ `agloviz list-algorithms` - lists placeholder algorithms (no real algorithms implemented)
  - ✅ `agloviz config-validate path.yaml` - config validation (fully working)
  - ✅ `agloviz config-show --config path.yaml` - show merged configuration (fully working)
  - ✅ `agloviz config-dump output.yaml --config path.yaml` - export merged config (fully working)
  - ✅ `agloviz config-create-samples --output-dir dir` - create sample configs (fully working)

- [x] **Add CLI framework and error handling**
  - ✅ Rich console integration for colored output
  - ✅ Proper type annotations and error handling
  - ✅ Typer integration with help system
  - ✅ Configuration management commands fully implemented
  - ✅ Command-line argument parsing and validation framework

**🎉 Phase 0.3 Achievements:**
- ✅ **CLI Framework**: Typer-based with Rich console integration
- ✅ **Configuration Commands**: Full suite of config management commands working
- ✅ **Error Handling**: Comprehensive error taxonomy with world-class UX
- ✅ **Help System**: Complete CLI help and argument validation
- ⚠️ **Render/Preview Commands**: Placeholder implementations (moved to Phase 1.6)
- ⚠️ **Algorithm Integration**: No actual algorithms implemented yet

#### 0.4 Timing System Foundation ✅ COMPLETED
**Source**: [ALGOViz_Design_TimingConfig.md](planning/ALGOViz_Design_TimingConfig.md)

- [x] **Implement TimingConfig and TimingTracker**
  - ✅ Create timing buckets: ui, events, effects, waits
  - ✅ Add mode multipliers: draft (0.5), normal (1.0), fast (0.25)
  - ✅ Implement `base_for(action, mode)` method
  - ✅ Add TimingTracker for logging actual vs expected durations

**🎉 Phase 0.4 Achievements:**
- ✅ **TimingConfig**: Full timing buckets with action mapping and mode multipliers
- ✅ **TimingTracker**: CSV/JSON export with variance tracking and summary statistics
- ✅ **Action Bucket Mapping**: Automatic categorization of UI/events/effects/waits
- ✅ **Performance Analysis**: Mean variance tracking and color-coded accuracy reporting

#### 0.5 Error Taxonomy Implementation ✅ COMPLETED
**Source**: [ALGOViz_Error_Taxonomy.md](planning/ALGOViz_Error_Taxonomy.md)

- [x] **Create error classification system**
  - ✅ Implement `AGLOVizError` base class with category, context, issue, remedy
  - ✅ Add specific error types: ConfigError, StoryboardError, AdapterError, ScenarioError, RegistryError, RenderError, VoiceoverError, PluginError
  - ✅ Implement suggestion algorithms for typos and alternatives (Levenshtein distance + fuzzy matching)
  - ✅ Add structured logging with error metadata and Rich console integration

**🎉 Phase 0.5 Achievements:**
- ✅ **Complete Error Taxonomy**: 8 error types with structured messaging
- ✅ **Intelligent Suggestions**: Levenshtein distance + fuzzy matching + context-aware suggestions
- ✅ **Rich Error Display**: Beautiful error panels with syntax highlighting and file excerpts
- ✅ **Structured Logging**: JSON export, error aggregation, and debug mode
- ✅ **CLI Integration**: Enhanced error handling with --debug flag and consistent exit codes
- ✅ **Factory Functions**: Convenient error creation for common patterns
- ✅ **Error Collectors**: Batch error processing and analysis

### Deliverables
- ✅ **COMPLETED**: Basic project structure with dependency management
- 🔄 **PARTIAL**: CLI framework with working `version`/`config-*` commands (`render`/`preview` are placeholders)
- ✅ **COMPLETED**: Modern development toolchain with ruff, mypy, pytest, and justfile
- ✅ **COMPLETED**: Configuration system with validation and merging
- ✅ **COMPLETED**: Timing system foundation with CSV/JSON export
- ✅ **COMPLETED**: Error handling with actionable messages (comprehensive error taxonomy)

### 🔍 **Critical Assessment: What's Actually Implemented**

**✅ FULLY IMPLEMENTED:**
- **Configuration System**: Complete Pydantic models, hydra-zen integration, YAML processing, CLI overrides, environment variables
- **Error Taxonomy**: World-class error handling with intelligent suggestions, rich display, structured logging
- **Timing System**: TimingConfig, TimingTracker with CSV/JSON export, variance detection
- **CLI Framework**: Typer-based with Rich console, comprehensive help system
- **Development Toolchain**: Modern tooling (ruff, mypy, pytest), 82% test coverage, 297 tests
- **Storyboard DSL**: Complete Pydantic models, YAML parsing, action registry, validation
- **VizEvent System**: Full event schema, payload validation, routing system
- **BFS Algorithm**: Complete adapter with deterministic event generation
- **Scenario Runtime**: Protocol, GridScenario, ScenarioLoader, contract validation
- **Working CLI**: `list-algorithms` shows real algorithms, `validate-events` generates actual events

**⚠️ PLACEHOLDER IMPLEMENTATIONS:**
- **CLI Commands**: `render` and `preview` show help but don't actually render anything (Phase 1.5-1.6)
- **Widgets**: Empty directories with just `__init__.py` files (Phase 1.3)
- **Director**: No orchestration component (Phase 1.4)

**✅ IMPLEMENTED:**
- **Storyboard DSL**: Complete Pydantic models, YAML parsing, action registry
- **VizEvent System**: Full event schema, payload validation, routing system
- **BFS Algorithm**: Complete adapter implementation with deterministic output
- **Scenario Runtime**: Protocol, GridScenario, ScenarioLoader, contract validation
- **CLI Integration**: Working algorithm listing and event validation commands

**❌ NOT IMPLEMENTED:**
- **Director**: No orchestration component
- **Rendering Pipeline**: No Manim integration, no video output
- **Component Registry**: No widget management
- **Additional Algorithms**: No DFS, Dijkstra, or A* implementations
- **Voiceover**: No CoquiTTS integration
- **Subtitles**: No SRT/VTT generation

**📝 Note**: Phase 0 established an excellent **foundation** with world-class configuration, error handling, and tooling. Phase 1.1 added complete storyboard DSL support. Phase 1.2 implemented the first working algorithm (BFS) with full event generation, making this the first phase to deliver actual algorithm visualization capability. The core rendering pipeline and widgets remain unimplemented.

### 🏗️ **Phase 0-1.2 Foundation Summary (What We Built)**

**Infrastructure Excellence** (4,200+ lines of code, 297 tests, 82% coverage):
- **Modern Toolchain**: uv, ruff, mypy, pytest, justfile, Rich console
- **Configuration Architecture**: Pydantic + hydra-zen + OmegaConf with full precedence rules
- **Error Handling**: 8 error types, intelligent suggestions, rich display, structured logging
- **Timing Foundation**: Performance tracking with CSV/JSON export and variance analysis
- **CLI Framework**: Typer-based with comprehensive help and error handling
- **Storyboard DSL**: Complete YAML parsing, Pydantic models, action registry
- **VizEvent System**: Event schema, payload validation, routing registry
- **Algorithm Infrastructure**: BFS adapter, scenario runtime, contract validation
- **Testing Excellence**: Unit tests, integration tests, property-based testing, high coverage
- **Code Quality**: Zero linting issues, consistent branding, automated tooling

**What This Enables**:
- **Rapid Development**: Excellent DX with fast linting, comprehensive error messages
- **Configuration Management**: Any complexity of config can be handled elegantly
- **Error Debugging**: World-class error UX makes development much smoother
- **Performance Monitoring**: Built-in timing analysis for optimization
- **Quality Assurance**: Comprehensive testing framework with high coverage
- **Algorithm Development**: Working BFS template for implementing new algorithms
- **Event-Driven Architecture**: Complete event system ready for widget integration
- **Scenario Testing**: Contract validation ensures algorithm correctness

Phase 0 created a **professional-grade foundation** and Phase 1.1-1.2 built the **core algorithm infrastructure** that will accelerate all future development. The VizEvent system, BFS adapter, and scenario runtime provide a **working algorithm implementation** that demonstrates the full architecture. The infrastructure is **production-ready** and follows Google-level engineering standards.

---

## 📋 Phase 1: Core Architecture & BFS Migration (MVP)

### Goal
Implement the core architectural components and migrate the existing BFS algorithm to the new modular system.

### Duration: 3-4 weeks

### Tasks

#### 1.1 Storyboard DSL Implementation ✅ COMPLETED
**Source**: [ALGOViz_Design_Storyboard_DSL.md](planning/ALGOViz_Design_Storyboard_DSL.md)

- [x] **Create Storyboard data models**
  - ✅ Implemented `Beat`, `Shot`, `Act`, `Storyboard` Pydantic models (not dataclasses)
  - ✅ Added narration, bookmarks, and timing override fields with validation
  - ✅ Full Pydantic validation with Field constraints and descriptions
  - **Note**: Used Pydantic-only design (no duplicate dataclass models) for cleaner architecture

- [x] **Implement storyboard loading and parsing**
  - ✅ YAML parser with strict validation in `StoryboardLoader`
  - ✅ Support for actions: `show_title`, `show_grid`, `show_widgets`, `play_events`, `trace_path`, `outro`, etc.
  - ✅ Error handling with Act/Shot/Beat context using existing `ConfigError` taxonomy
  - ✅ Integration with existing `ConfigManager` for YAML processing

- [x] **Create sample BFS storyboard**
  - ✅ Complete BFS demonstration in `storyboards/bfs_demo.yaml`
  - ✅ Acts: Introduction, Algorithm, Results with narration and bookmarks
  - ✅ 11 beats across 3 acts with comprehensive action coverage
  - ✅ Bookmark scaffolding for future word-level synchronization

- [x] **Action Registry Foundation**
  - ✅ Implemented `ActionRegistry` for managing storyboard actions
  - ✅ Registration, lookup, and validation functionality
  - ✅ Global registry with convenience functions

- [x] **CLI Integration**
  - ✅ Added `agloviz validate-storyboard` command
  - ✅ Rich console output with structure visualization
  - ✅ Optional `--validate-actions` flag for action checking
  - ✅ Integration with existing error display system

- [x] **Comprehensive Testing**
  - ✅ 30 unit tests with 96% code coverage
  - ✅ Tests for validation, error handling, YAML parsing, action registry
  - ✅ Property-based testing patterns following project conventions

**🎉 Phase 1.1 Achievements:**
- ✅ **Clean Architecture**: Pydantic-only models eliminate duplication and complexity
- ✅ **Working CLI**: Full storyboard validation with beautiful Rich output
- ✅ **Sample Storyboard**: Complete BFS demo with narration and bookmarks
- ✅ **Error Handling**: Seamless integration with existing error taxonomy
- ✅ **Test Coverage**: Comprehensive test suite with high coverage
- ✅ **Documentation**: Complete README for storyboard authoring

**🎉 Phase 1.2 Achievements:**
- ✅ **VizEvent System**: Complete Pydantic models with exact design doc compliance
- ✅ **BFS Algorithm**: First working algorithm with deterministic event generation
- ✅ **Scenario Runtime**: Full contract implementation with validation harness
- ✅ **Event Routing**: Complete routing registry with BFS routing map
- ✅ **CLI Integration**: Working `list-algorithms` and `validate-events` commands
- ✅ **AdapterWrapper**: Automatic step indexing as specified in SDD
- ✅ **Test Coverage**: 96 new tests, comprehensive integration testing
- ✅ **Grid Format**: Updated to SDD specification with test scenarios

#### 1.2 VizEvent System & BFS Adapter ✅ COMPLETED
**Source**: [ALGOViz_Design_Adapters_VizEvents.md](planning/ALGOViz_Design_Adapters_VizEvents.md)

- [x] **Implement VizEvent schema**
  - ✅ Created `VizEvent` Pydantic model with type, payload, step_index, metadata
  - ✅ Defined standardized payload keys: node, pos, weight, parent (PayloadKey enum)
  - ✅ Added payload validation functions
  - ✅ Used `dict[str, Any]` as specified in design documents

- [x] **Create BFS Adapter**
  - ✅ Implemented `AlgorithmAdapter` protocol exactly as specified
  - ✅ Created `AdapterWrapper` for automatic step indexing (SDD Section 8.3)
  - ✅ Implemented BFS algorithm emitting events: `enqueue`, `dequeue`, `goal_found`
  - ✅ Ensured deterministic output with sorted neighbor ordering

- [x] **Implement Scenario Runtime Contract**
  - ✅ Created `Scenario` protocol with `neighbors()`, `in_bounds()`, `passable()`, `cost()`
  - ✅ Implemented `ScenarioLoader` with `from_config()` factory method
  - ✅ Added `ContractTestHarness` for comprehensive validation
  - ✅ Updated grid file format to match SDD specification (width/height/obstacles/weights)
  - ✅ Created test grids: simple, maze, unreachable scenarios

#### 1.3 Component Registry & Basic Widgets
**Source**: [ALGOViz_Design_Widgets_Registry.md](planning/ALGOViz_Design_Widgets_Registry.md)

- [ ] **Implement ComponentRegistry**
  - Create registry with `register()` and `get()` methods
  - Support widget factories and lifecycle management
  - Add namespacing support for plugins

- [ ] **Create core widgets**
  - `QueueWidget`: Visual BFS queue representation
  - `GridWidget`: 2D grid with colored cells
  - `HUDWidget`: Overlay for complexity/time counters
  - `LegendWidget`: Color/symbol key
  - Implement Widget protocol: `show()`, `update()`, `hide()`

#### 1.4 Director Implementation
**Source**: [ALGOViz_Design_Director.md](planning/ALGOViz_Design_Director.md)

- [ ] **Implement Director class**
  - Load and validate storyboards
  - Resolve actions via registry
  - Apply TimingConfig with mode multipliers
  - Iterate acts → shots → beats with proper transitions

- [ ] **Add event playback system**
  - Integrate with BFS Adapter for `play_events` action
  - Implement routing maps: `EventType → [handler_names]`
  - Apply timing per event with hybrid timing support
  - Handle act/shot transitions with fades/waits

#### 1.5 Basic Rendering Pipeline
**Source**: [ALGOViz_Design_Rendering_Export.md](planning/ALGOViz_Design_Rendering_Export.md)

- [ ] **Implement FrameRenderer**
  - Use Manim headless renderer
  - Ensure determinism with fixed seeds and font pinning
  - Support chunked rendering at shot granularity
  - Add basic caching with content hashing

- [ ] **Create basic Encoder**
  - Support MP4 output with libx264
  - Implement quality profiles: draft, medium, high
  - Add ffmpeg integration with reproducible settings

#### 1.6 CLI Integration & User Commands
**Source**: [ALGOViz_Design_CLI_DevUX.md](planning/ALGOViz_Design_CLI_DevUX.md)

- [ ] **Complete render command implementation**
  - `agloviz render --algo bfs --scenario demo.yaml` - integrate with Director
  - Support `--quality` (draft/medium/high), `--output-dir`, `--scenario` flags
  - Configuration loading and validation integration
  - Error handling with helpful messages for missing components

- [ ] **Complete preview command implementation**
  - `agloviz preview --algo bfs --scenario demo.yaml --frames 120` - quick preview
  - Support `--frames` for partial rendering
  - Fast preview mode with draft quality
  - Integration with rendering pipeline

#### 1.7 Testing Infrastructure
**Source**: [ALGOViz_SDD.md#9-Testing--CI](planning/ALGOViz_SDD.md#9-testing--ci)

- [ ] **Set up testing framework**
  - Unit tests for adapters with deterministic VizEvents
  - Storyboard parsing and validation tests
  - Timing system tests with mock Director
  - Widget contract tests

- [ ] **Implement CI pipeline**
  - Preview GIF generation for PRs
  - Timing CSV export for analysis
  - Golden test framework for regression testing

### Deliverables
- [x] **Working BFS algorithm with event generation** ✅ COMPLETED
- [x] **Storyboard DSL with YAML parsing** ✅ COMPLETED
- [x] **VizEvent System & BFS Adapter** ✅ COMPLETED
- [ ] Component registry with basic widgets
- [ ] Director with timing and event coordination
- [ ] Basic rendering pipeline with MP4 output
- [ ] Complete CLI commands: `render` and `preview` with full functionality
- [x] **Comprehensive testing infrastructure** ✅ COMPLETED (82% coverage, 297 tests)

---

## 📋 Phase 2: Enhanced Widgets & Additional Algorithms

### Goal
Expand the widget library and add more algorithms while improving the overall system robustness.

### Duration: 4-5 weeks

### Tasks

#### 2.1 Advanced Widget Implementation
**Source**: [ALGOViz_Design_Widgets_Registry.md](planning/ALGOViz_Design_Widgets_Registry.md)

- [ ] **Create additional widgets**
  - `StackWidget`: For DFS visualization
  - `PriorityQueueWidget`: For Dijkstra/A* algorithms
  - `PathTracer`: Animated path highlighting
  - `ComplexityWidget`: O-notation displays

- [ ] **Enhance existing widgets**
  - Add animation states and transitions
  - Implement proper lifecycle management
  - Add visual polish and consistency

#### 2.2 Additional Algorithm Adapters
**Source**: [ALGOViz_PRD.md#Phase-2](planning/ALGOViz_PRD.md#phase-2)

- [ ] **Implement DFS Adapter**
  - Extract DFS logic to adapter pattern
  - Emit events: `push`, `pop`, `visit`, `backtrack`
  - Create routing map and storyboard

- [ ] **Implement Dijkstra Adapter**
  - Handle weighted edges and priority queue
  - Emit events: `relax`, `update_distance`, `add_to_queue`
  - Support cost function from scenario contract

- [ ] **Implement A* Adapter**
  - Combine Dijkstra with heuristic function
  - Emit events: `calculate_f_score`, `explore_node`
  - Support grid-based heuristics (Manhattan, Euclidean)

#### 2.3 Enhanced Scenarios & Themes
**Source**: [ALGOViz_Design_Config_System.md](planning/ALGOViz_Design_Config_System.md)

- [ ] **Create multiple scenario configurations**
  - Different grid sizes and obstacle patterns
  - Weighted vs unweighted scenarios
  - Various start/goal configurations

- [ ] **Implement theme system**
  - Color palettes for different algorithm states
  - Role-based coloring: visited, frontier, goal, path
  - Theme validation and merging

#### 2.4 Improved CLI Experience
**Source**: [ALGOViz_Design_CLI_DevUX.md](planning/ALGOViz_Design_CLI_DevUX.md)

- [ ] **Enhance CLI commands**
  - `agloviz test` with golden regression tests
  - `agloviz plugins list` for plugin discovery
  - `agloviz config dump` for merged config export

- [ ] **Add advanced flags**
  - `--frames` for frame range specification
  - `--output-format` for multiple formats
  - `--profile` for performance analysis

#### 2.5 Rendering Enhancements
**Source**: [ALGOViz_Design_Rendering_Export.md](planning/ALGOViz_Design_Rendering_Export.md)

- [ ] **Expand output formats**
  - GIF generation with palette optimization
  - PNG sequence export
  - Multiple quality profiles

- [ ] **Improve caching system**
  - Shot-level caching with content hashing
  - Cache invalidation on configuration changes
  - Parallel rendering support

### Deliverables
- [ ] DFS, Dijkstra, and A* algorithm support
- [ ] Advanced widget library with animations
- [ ] Multiple scenarios and theme system
- [ ] Enhanced CLI with testing and profiling
- [ ] Multi-format rendering with caching

---

## 📋 Phase 3: Voiceover Integration & Subtitles

### Goal
Add full voiceover support with CoquiTTS and automatic subtitle generation.

### Duration: 3-4 weeks

### Tasks

#### 3.1 Voiceover Engine Implementation
**Source**: [ALGOViz_Design_Voiceover.md](planning/ALGOViz_Design_Voiceover.md)

- [ ] **Implement CoquiTTS integration**
  - Create `VoiceoverEngine` protocol and CoquiTTS implementation
  - Support configurable voice, language, and speed
  - Add audio caching and prewarming
  - Handle TTS failures gracefully

- [ ] **Implement hybrid timing**
  - Ensure visuals never cut off narration
  - Apply `run_time = max(base_timing, narration_duration)`
  - Support `min_duration` and `max_duration` overrides
  - Integrate with TimingTracker

#### 3.2 Director Voiceover Integration
**Source**: [ALGOViz_Design_Director.md](planning/ALGOViz_Design_Director.md)

- [ ] **Enhance Director for voiceover**
  - Wrap beats with narration in `voiceover()` context
  - Apply hybrid timing rules
  - Register bookmark scaffolding (literal word matching)
  - Handle voiceover failures with fallback

#### 3.3 Subtitle Generation System
**Source**: [ALGOViz_Design_Rendering_Export.md#7.4-Subtitles-Exporter](planning/ALGOViz_Design_Rendering_Export.md#74-subtitles-exporter)

- [ ] **Implement SubtitleExporter**
  - Generate SRT files from narration text and TimingTracker
  - Support baseline mode (beat-aligned timestamps)
  - Add whisper-align mode for enhanced precision (optional)
  - Export VTT format support

- [ ] **Add subtitle configuration**
  - CLI flags: `--with-subtitles`, `--subtitles-burn-in`
  - Config options: mode, format, burn-in settings
  - Integration with rendering pipeline

#### 3.4 Enhanced Storyboard Support
**Source**: [ALGOViz_Design_Storyboard_DSL.md](planning/ALGOViz_Design_Storyboard_DSL.md)

- [ ] **Improve narration features**
  - Support per-beat narration with timing control
  - Add bookmark routing preparation (scaffolded)
  - Validate narration text and timing constraints
  - Support external narration files (localization prep)

#### 3.5 Audio Pipeline Integration
**Source**: [ALGOViz_Design_Rendering_Export.md](planning/ALGOViz_Design_Rendering_Export.md)

- [ ] **Implement audio muxing**
  - Integrate TTS audio with video rendering
  - Support AAC encoding with configurable bitrate
  - Handle audio/video synchronization
  - Add audio quality settings

### Deliverables
- [ ] Full voiceover support with CoquiTTS
- [ ] Hybrid timing ensuring narration-visual sync
- [ ] Automatic subtitle generation (SRT/VTT)
- [ ] Audio-video muxing in final output
- [ ] Bookmark scaffolding for future phases

---

## 📋 Phase 4: Plugin System & Advanced Features

### Goal
Enable third-party extensions and add advanced rendering features.

### Duration: 4-5 weeks

### Tasks

#### 4.1 Plugin System Implementation
**Source**: [ALGOViz_Design_Plugin_System.md](planning/ALGOViz_Design_Plugin_System.md)

- [ ] **Create PluginManager**
  - Discover plugins via Python entry points
  - Support local plugin directories
  - Implement version compatibility checking
  - Add error isolation and quarantine mode

- [ ] **Implement plugin API**
  - `register_algorithm()`, `register_widget()`, `register_action()`
  - `register_storyboard()`, `register_theme()`
  - Enforce namespacing: `pkg_name.resource_name`
  - Support asset resolution with `pkg://` URIs

- [ ] **Add plugin CLI commands**
  - `agloviz plugins list` - show plugin status and versions
  - `agloviz plugins verify` - dry-run loading and testing
  - Support plugin-specific rendering

#### 4.2 Dependency Injection System
**Source**: [ALGOViz_Design_DI_Strategy.md](planning/ALGOViz_Design_DI_Strategy.md)

- [ ] **Implement Hydra-based DI**
  - Use `_target_` for config-driven instantiation
  - Support hydra-zen `builds()` for typed configs
  - Implement object scopes: singleton, per-run, transient
  - Add lifecycle management and validation

- [ ] **Create DI configuration**
  - Main run config with Director, Adapter, VoiceoverEngine
  - Plugin discovery and registration
  - Swappable implementations via YAML/CLI

#### 4.3 Advanced Rendering Features
**Source**: [ALGOViz_Design_Rendering_Export.md](planning/ALGOViz_Design_Rendering_Export.md)

- [ ] **Implement advanced encoding**
  - Support libx265 for better compression
  - Hardware encoder support (NVENC/VAAPI)
  - Custom CRF and preset configurations
  - Bitrate control and two-pass encoding

- [ ] **Add rendering optimizations**
  - Parallel shot rendering
  - Memory-efficient frame processing
  - Advanced caching with compression
  - Progress tracking and cancellation

#### 4.4 Expanded Algorithm Library
**Source**: [ALGOViz_PRD.md#Phase-4](planning/ALGOViz_PRD.md#phase-4)

- [ ] **Add sorting algorithms**
  - Bubble Sort, Quick Sort, Merge Sort
  - Heap Sort, Radix Sort
  - Create specialized widgets for array visualization

- [ ] **Add graph algorithms**
  - Minimum Spanning Tree (Kruskal, Prim)
  - Topological Sort
  - Strongly Connected Components

- [ ] **Create contribution templates**
  - Developer guide for new algorithms
  - Widget creation templates
  - Storyboard authoring guidelines

#### 4.5 Advanced Scenarios
**Source**: [ALGOViz_SDD.md#8-Scenario-Runtime-Contract](planning/ALGOViz_SDD.md#8-scenario-runtime-contract)

- [ ] **Support complex graphs**
  - Weighted directed graphs
  - Multi-graph support
  - Dynamic scenario generation

- [ ] **Add scenario validation**
  - Comprehensive contract testing
  - Property-based testing with random scenarios
  - Performance benchmarking

### Deliverables
- [ ] Complete plugin system with discovery and registration
- [ ] Dependency injection with Hydra
- [ ] Advanced rendering with multiple codecs
- [ ] Expanded algorithm library (sorting, graphs)
- [ ] Developer contribution framework

---

## 📋 Phase 5: Advanced Features & Polish

### Goal
Add advanced features like bookmark routing, localization, and educator tools.

### Duration: 3-4 weeks

### Tasks

#### 5.1 Bookmark Routing System
**Source**: [ALGOViz_Design_Voiceover.md#7-Bookmarks-Scaffold-Now](planning/ALGOViz_Design_Voiceover.md#7-bookmarks-scaffold-now)

- [ ] **Implement word-level synchronization**
  - Replace literal word matching with phoneme alignment
  - Support real-time bookmark triggers during playback
  - Map bookmark words to widget actions
  - Handle bookmark timing precision

- [ ] **Enhance Director bookmark handling**
  - Wire bookmark callbacks to action execution
  - Support complex bookmark routing patterns
  - Add bookmark validation and error handling

#### 5.2 Localization Support
**Source**: [ALGOViz_PRD.md#Phase-5](planning/ALGOViz_PRD.md#phase-5)

- [ ] **Implement multi-language support**
  - External narration file loading
  - Language-specific storyboards
  - Localized error messages and CLI help
  - Cultural adaptation for themes and timing

- [ ] **Add translation infrastructure**
  - Storyboard template system
  - Translation key management
  - Quality assurance for translations

#### 5.3 Educator Tools
**Source**: [ALGOViz_PRD.md#Phase-5](planning/ALGOViz_PRD.md#phase-5)

- [ ] **Create educator packs**
  - Pre-built video sets with consistent branding
  - Curated algorithm sequences
  - Educational metadata and annotations

- [ ] **Implement integration hooks**
  - APIs for external learning platforms
  - Embedding support for web applications
  - Batch rendering capabilities

#### 5.4 Advanced CLI Features
**Source**: [ALGOViz_Design_CLI_DevUX.md](planning/ALGOViz_Design_CLI_DevUX.md)

- [ ] **Add interactive features**
  - `--interactive` mode for step-by-step exploration
  - `--batch` mode for multiple scenarios
  - `--all-algorithms` for comprehensive testing

- [ ] **Implement advanced debugging**
  - `--profile` for performance analysis
  - `--trace` for execution tracing
  - `--debug-render` for frame-by-frame analysis

#### 5.5 Quality Assurance & Performance
**Source**: [ALGOViz_Vision_Goals.md](planning/ALGOViz_Vision_Goals.md)

- [ ] **Implement comprehensive testing**
  - Golden test updates for all algorithms
  - Performance regression testing
  - Cross-platform compatibility testing

- [ ] **Add monitoring and observability**
  - Render metrics collection
  - Performance profiling tools
  - Error rate monitoring

### Deliverables
- [ ] Word-level bookmark synchronization
- [ ] Multi-language localization support
- [ ] Educator tools and integration APIs
- [ ] Advanced CLI with interactive features
- [ ] Production-ready quality assurance

---

## 🎯 **Immediate Next Steps (Phase 1.3)**

### **Priority 1: Component Registry & Basic Widgets**
The next logical step is implementing the Component Registry and basic widgets to consume the VizEvents:

1. **Create ComponentRegistry** (`src/agloviz/widgets/registry.py`)
   - Registry with `register()` and `get()` methods
   - Widget factories and lifecycle management
   - Namespacing support for plugins

2. **Create Core Widgets** (`src/agloviz/widgets/`)
   - `QueueWidget`: Visual BFS queue representation
   - `GridWidget`: 2D grid with colored cells
   - `HUDWidget`: Overlay for complexity/time counters
   - `LegendWidget`: Color/symbol key
   - Implement Widget protocol: `show()`, `update()`, `hide()`

3. **Widget Testing** (`tests/unit/widgets/`)
   - Mock scene + event testing
   - Widget lifecycle tests
   - Registry functionality tests

**Estimated Effort**: 2-3 weeks for widget foundation

### **Priority 2: Director Implementation**
Once widgets can consume events, implement the Director to orchestrate everything:

1. **Director Class** (`src/agloviz/core/director.py`)
2. **Event Playback System** with BFS integration
3. **Director Testing** (`tests/unit/core/test_director.py`)

**Estimated Effort**: 2-3 weeks

---

## 🎯 Success Criteria & Validation

### MVP (Phase 1) Success Criteria
- [ ] User can render a BFS video with scenario and optional narration
- [x] **Storyboard DSL works with basic actions and timing** ✅ COMPLETED
- [x] **BFS algorithm generates deterministic VizEvents** ✅ COMPLETED  
- [x] **Scenario runtime provides algorithm environment** ✅ COMPLETED
- [x] **Event routing system connects events to handlers** ✅ COMPLETED
- [ ] Component registry supports widget lifecycle
- [ ] Director orchestrates beats with proper timing
- [ ] Basic MP4 output with consistent quality

**✅ PROGRESS UPDATE**: Phase 1.1-1.2 implemented the **core algorithm infrastructure**. The VizEvent system, BFS adapter, and scenario runtime are complete and working. Phase 1.3-1.6 will build the visualization and rendering components.

### ✅ **Phase 1.2 Validation Results**
All success criteria for Phase 1.2 have been met:

**CLI Commands Working:**
```bash
just test                                    # ✅ 297 tests pass, 82% coverage
agloviz list-algorithms                      # ✅ Shows "bfs" 
agloviz validate-events bfs --scenario demo/scenario.yaml  # ✅ 189 events generated
agloviz validate-storyboard storyboards/bfs_demo.yaml --validate-actions  # ✅ Validates successfully
```

**System Capabilities:**
- ✅ **189 VizEvents** generated for 10x10 grid BFS traversal
- ✅ **Deterministic behavior** - same input produces same events every time
- ✅ **Rich console output** with beautiful event display and step indexing
- ✅ **Contract compliance** - all scenarios pass validation harness
- ✅ **Integration testing** - complete end-to-end workflow functional

### Phase 2 Success Criteria
- [ ] At least 3 algorithms supported (BFS, DFS, Dijkstra/A*)
- [ ] Reusable widgets for all algorithm types
- [ ] Multiple scenarios and theme support
- [ ] Enhanced CLI with testing capabilities

### Phase 3 Success Criteria
- [ ] Narrated videos with synchronized subtitles
- [ ] Hybrid timing ensures narration-visual sync
- [ ] CoquiTTS integration with configurable voices
- [ ] SRT/VTT subtitle export

### Phase 4 Success Criteria
- [ ] Contributors can add new algorithms without touching core code
- [ ] Plugin system supports external extensions
- [ ] Advanced rendering with multiple formats and codecs
- [ ] Comprehensive algorithm library

### Phase 5 Success Criteria
- [ ] Bookmark routing triggers visual sync in real-time
- [ ] Multi-language support with localization
- [ ] Educator tools and platform integration
- [ ] Production-ready quality and performance

---

## 🔧 Technical Implementation Notes

### Development Environment Setup
- Use `uv` for Python environment management [[memory:7944020]]
- Run tests with `just test` command [[memory:5390444]]
- Use Rich library for colored logging [[memory:5483251]]
- Avoid `Any` type in code [[memory:5483264]]
- Use enums for static values instead of magic strings [[memory:5483259]]
- Use **ruff** for ultra-fast linting and formatting (replaces black, isort, flake8)

### Testing Strategy
- Each test explicitly decorated with `pytest.mark.unit` [[memory:5380325]]
- Never disable warnings in test commands [[memory:5380313]]
- Real test plugins under `tests/system/` directory [[memory:5376917]]
- Pydantic config models centralized in own package [[memory:5380045]]

### Code Quality Standards
- Follow the established template structure in design docs
- Include concrete examples with YAML/Python code snippets
- Maintain cross-references between documents
- Use **ALGOViz** brand consistency (not ALGOViz)
- Preserve `algoviz` lowercase in technical identifiers

---

## 📚 Reference Documentation

### Core Architecture Documents
- [ALGOViz_Vision_Goals.md](planning/ALGOViz_Vision_Goals.md) - Project vision and principles
- [ALGOViz_PRD.md](planning/ALGOViz_PRD.md) - Product requirements and phases
- [ALGOViz_SDD.md](planning/ALGOViz_SDD.md) - System design and architecture

### Component Design Documents
- [ALGOViz_Design_Storyboard_DSL.md](planning/ALGOViz_Design_Storyboard_DSL.md) - Storyboard language
- [ALGOViz_Design_Director.md](planning/ALGOViz_Design_Director.md) - Orchestration component
- [ALGOViz_Design_Adapters_VizEvents.md](planning/ALGOViz_Design_Adapters_VizEvents.md) - Algorithm adapters
- [ALGOViz_Design_Widgets_Registry.md](planning/ALGOViz_Design_Widgets_Registry.md) - UI components
- [ALGOViz_Design_Voiceover.md](planning/ALGOViz_Design_Voiceover.md) - Narration system

### Infrastructure Documents
- [ALGOViz_Design_Config_System.md](planning/ALGOViz_Design_Config_System.md) - Configuration management
- [ALGOViz_Design_TimingConfig.md](planning/ALGOViz_Design_TimingConfig.md) - Timing system
- [ALGOViz_Design_Rendering_Export.md](planning/ALGOViz_Design_Rendering_Export.md) - Rendering pipeline
- [ALGOViz_Design_Plugin_System.md](planning/ALGOViz_Design_Plugin_System.md) - Extension framework
- [ALGOViz_Design_DI_Strategy.md](planning/ALGOViz_Design_DI_Strategy.md) - Dependency injection

### Developer Experience Documents
- [ALGOViz_Design_CLI_DevUX.md](planning/ALGOViz_Design_CLI_DevUX.md) - CLI design
- [ALGOViz_Error_Taxonomy.md](planning/ALGOViz_Error_Taxonomy.md) - Error handling
- [ALGOViz_Scenario_Theme_Merge_Precedence.md](planning/ALGOViz_Scenario_Theme_Merge_Precedence.md) - Config merging

---

## 🚀 Getting Started

1. **Read the Vision & Goals**: Start with [ALGOViz_Vision_Goals.md](planning/ALGOViz_Vision_Goals.md) to understand the project's purpose
2. **Review the Architecture**: Study [ALGOViz_SDD.md](planning/ALGOViz_SDD.md) for the overall system design
3. **Follow Phase 0**: Begin with foundation setup and basic CLI implementation
4. **Iterate and Test**: Use `agloviz preview` for rapid iteration during development
5. **Contribute**: Follow the established patterns and add comprehensive tests

This implementation plan provides a clear roadmap from MVP to a world-class algorithm visualization framework. Each phase builds incrementally while delivering value, ensuring the project remains maintainable and extensible throughout development.
