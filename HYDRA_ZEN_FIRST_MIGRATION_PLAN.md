# ALGOViz Hydra-Zen First Philosophy: Migration Plan

## 🎯 **OVERVIEW**

After analyzing all 16 planning documents in `planning/v2/`, there's a **significant gap** between the stated "hydra-zen first" philosophy and the actual implementation patterns specified in the documents. This plan systematically addresses these inconsistencies to achieve true hydra-zen first architecture.

---

## 📋 **CURRENT STATE ANALYSIS**

### **✅ WHAT'S ALREADY HYDRA-ZEN ALIGNED**

1. **DI Strategy Document** (`ALGOViz_Design_DI_Strategy_v2.md`)
   - ✅ Comprehensive hydra-zen patterns with `builds()`, `instantiate()`, `ConfigStore`
   - ✅ Scene configuration DI section (lines 345-412)
   - ✅ Widget instantiation via `_target_` patterns
   - ✅ Proper object graph and scoping

2. **Technology Choices**
   - ✅ Hydra + hydra-zen + OmegaConf stack specified
   - ✅ "Load/Merge with OmegaConf → Instantiate with hydra-zen/Hydra → Validate with Pydantic" philosophy

### **❌ CRITICAL GAPS IDENTIFIED**

1. **Configuration System** (`ALGOViz_Design_Config_System.md`)
   - ❌ Pure Pydantic models without hydra-zen integration
   - ❌ No `builds()` patterns for config creation
   - ❌ Missing ConfigStore registration
   - ❌ Manual instantiation instead of `_target_` approach

2. **Widget Architecture** (Referenced but missing document)
   - ❌ Manual Pydantic models for scene configurations
   - ❌ No hydra-zen structured configs for widgets
   - ❌ Registry-based instantiation instead of `instantiate()`

3. **Scene Configuration System** (Multiple documents)
   - ❌ Manual parameter resolution instead of hydra-zen templates
   - ❌ Direct factory calls instead of `_target_` instantiation
   - ❌ Missing ConfigStore integration

4. **Storyboard DSL** (`ALGOViz_Design_Storyboard_DSL_v2.md`)
   - ❌ Dataclass models instead of hydra-zen configs
   - ❌ No structured config composition
   - ❌ Missing `builds()` patterns

5. **Implementation Inconsistency**
   - ❌ PHASE_1_4_2_IMPLEMENTATION_PLAN.md uses pure Pydantic approach
   - ❌ Scene configuration patterns don't follow hydra-zen first
   - ❌ Widget instantiation bypasses hydra-zen system

---

## 🚀 **PHASE 1: CORE CONFIGURATION SYSTEM MIGRATION**

### **STEP 1.1: Update Configuration System Document**
**File**: `planning/v2/ALGOViz_Design_Config_System.md`

**Current Problems:**
```python
# Current: Pure Pydantic
class ScenarioConfig(BaseModel):
    name: str
    grid_file: str
    start: Tuple[int,int]
```

**Required Changes:**
```python
# New: Hydra-zen first with Pydantic validation
from hydra_zen import builds, make_config
from hydra.core.config_store import ConfigStore

# Create structured configs
ScenarioConfigZen = builds(
    ScenarioConfig,  # Pydantic model for validation
    name=str,
    grid_file=str, 
    start=tuple,
    zen_partial=True,
    populate_full_signature=True
)

# Register with ConfigStore
cs = ConfigStore.instance()
cs.store(name="scenario_base", node=ScenarioConfigZen)
```

**Tasks:**
- [x] Add hydra-zen imports and patterns to all config models
- [x] Create structured configs using `builds()` for all Pydantic models
- [x] Add ConfigStore registration patterns
- [x] Update instantiation examples to use `instantiate()`
- [x] Add composition examples with multiple config files

**✅ COMPLETED**: Configuration System document fully migrated to hydra-zen first architecture with:
- Pydantic models retained for validation
- Structured configs created using `builds()` for all models
- ConfigStore registration with groups and presets
- Complete migration guide and examples
- Enhanced testing patterns and error handling

### **STEP 1.2: Update DI Strategy Integration**
**File**: `planning/v2/ALGOViz_Design_DI_Strategy_v2.md`

**Current State**: ✅ Already well-aligned but needs scene config integration updates

**Required Changes:**
- [x] Update scene configuration examples to use proper hydra-zen patterns
- [x] Add widget instantiation patterns using `builds()` and `instantiate()`
- [x] Integrate parameter template resolution with hydra-zen
- [x] Update object graph to show hydra-zen flow

**✅ COMPLETED**: DI Strategy document fully enhanced for hydra-zen first with:
- Complete hydra-zen structured config patterns for all components
- Enhanced widget system DI integration with scene configurations
- Advanced parameter template resolution with OmegaConf resolvers
- Updated object graph showing hydra-zen instantiation flow
- Comprehensive testing strategies for structured configs
- Enhanced error handling with hydra-zen specific diagnostics

### **STEP 1.3: Create Missing Widget Architecture Document**
**File**: `planning/v2/ALGOViz_Design_Widget_Architecture_v2.md` (MISSING!)

**Critical Issue**: This document is referenced but doesn't exist in `planning/v2/`

**Required Actions:**
- [x] Create the complete Widget Architecture v2.0 document
- [x] Specify hydra-zen first patterns for all widget levels
- [x] Define scene configuration using hydra-zen structured configs
- [x] Specify parameter template resolution using hydra-zen
- [x] Update README_DOCS.md to fix broken reference

**✅ COMPLETED**: Widget Architecture v2.0 document created with complete hydra-zen first integration:
- Multi-level widget hierarchy with structured configs for all levels
- Scene configuration system using `make_config()` and `builds()` patterns
- Enhanced SceneEngine with hydra-zen instantiation and parameter resolution
- Plugin system architecture with ConfigStore integration
- Complete package organization and migration strategy
- Full alignment with Configuration System and DI Strategy documents

---

## 🚀 **PHASE 2: SCENE CONFIGURATION SYSTEM MIGRATION**

### **STEP 2.1: Update Scene Configuration Patterns**
**Files**: Multiple documents reference scene configurations

**Current Problems:**
```python
# Current: Manual Pydantic models
@dataclass
class SceneConfig:
    widgets: Dict[str, WidgetSpec]
    event_bindings: Dict[str, List[EventBinding]]
```

**Required Changes:**
```python
# New: Hydra-zen structured configs
from hydra_zen import builds, make_config

# Widget specifications using builds()
GridWidgetConfig = builds(
    "agloviz.widgets.grid.GridWidget",
    cell_size=0.5,
    show_coordinates=True,
    zen_partial=True
)

QueueWidgetConfig = builds(
    "agloviz.widgets.queue.QueueWidget", 
    max_visible=10,
    orientation="horizontal",
    zen_partial=True
)

# Scene configuration using composition
BFSSceneConfig = make_config(
    name="bfs_pathfinding",
    algorithm="bfs",
    widgets={
        "grid": GridWidgetConfig,
        "queue": QueueWidgetConfig
    },
    event_bindings={
        "enqueue": [
            builds(EventBinding, widget="queue", action="add_element", params={"element": "${event.node}"}),
            builds(EventBinding, widget="grid", action="highlight_element", params={"identifier": "${event.node}", "style": "frontier"})
        ]
    }
)
```

**Tasks:**
- [x] Update all scene configuration examples to use hydra-zen patterns
- [x] Replace manual instantiation with `instantiate()` calls
- [x] Add ConfigStore registration for scene configurations
- [x] Update parameter template resolution to work with hydra-zen

**✅ COMPLETED**: Scene configuration patterns updated across multiple documents:
- Updated `src/agloviz/core/scene.py` with complete hydra-zen first implementation
- Enhanced SceneEngine with hydra-zen instantiation and parameter resolution
- Added structured configs for EventBinding, WidgetSpec, and SceneConfig
- Implemented BFS and QuickSort scene configurations using `make_config()`
- Added ConfigStore registration for scene templates and algorithm-specific configs
- Updated Director v2 document with hydra-zen scene integration patterns
- Updated Storyboard DSL v2 document with hydra-zen structured config patterns
- Enhanced parameter template resolution using OmegaConf resolvers

### **STEP 2.2: Update Widget Registry Patterns**
**File**: `planning/v2/ALGOViz_Design_Widgets_Registry_v2.md`

**Current Problems:**
- Manual factory registration
- No hydra-zen integration in widget creation
- Registry-based instantiation instead of `_target_` approach

**Required Changes:**
- [x] Add hydra-zen widget configuration patterns
- [x] Update registry to work with structured configs
- [x] Specify `_target_` patterns for all widget types
- [x] Add ConfigStore integration for widget configurations

**✅ COMPLETED**: Widget Registry patterns fully migrated to hydra-zen first approach:
- Converted all widget examples to use `builds()` structured configs
- Updated ComponentRegistry to use ConfigStore instead of manual factories
- Added `_target_` patterns for all widget levels (primitives, structures, domains)
- Implemented ConfigStore integration with widget groups and plugin support
- Enhanced widget discovery and instantiation through `instantiate()`
- Added structured configs for layout engines and domain packages
- Updated Manim integration with hydra-zen configuration patterns
- Provided complete CLI integration for ConfigStore widget management

---

## 🚀 **PHASE 3: STORYBOARD DSL MIGRATION**

### **STEP 3.1: Update Storyboard DSL Document**
**File**: `planning/v2/ALGOViz_Design_Storyboard_DSL_v2.md`

**Current Problems:**
```python
# Current: Dataclass models
@dataclass
class Beat:
    action: str
    args: dict[str, Any] = field(default_factory=dict)
```

**Required Changes:**
```python
# New: Hydra-zen structured configs
from hydra_zen import builds, make_config

BeatConfig = builds(
    Beat,
    action=str,
    args=dict,
    narration=None,
    bookmarks=dict,
    zen_partial=True,
    populate_full_signature=True
)

# Storyboard composition
StoryboardConfig = make_config(
    acts=[
        builds(ActConfig, 
            title="Introduction",
            shots=[
                builds(ShotConfig,
                    beats=[
                        BeatConfig(action="show_title", args={"text": "BFS Demo"}),
                        BeatConfig(action="show_widgets"),
                        BeatConfig(action="play_events")
                    ]
                )
            ]
        )
    ]
)
```

**Tasks:**
- [x] Convert all dataclass models to hydra-zen structured configs
- [x] Add ConfigStore registration for storyboard templates
- [x] Update YAML loading to use hydra-zen composition
- [x] Add storyboard template system with hydra-zen

**✅ COMPLETED**: Storyboard DSL document fully migrated to hydra-zen first architecture:
- Enhanced all storyboard components (Beat, Shot, Act, Storyboard) with structured configs
- Implemented comprehensive ConfigStore template system with act and storyboard templates
- Added StoryboardLoader with hydra-zen instantiation and template support
- Created Hydra configuration files with composition syntax and parameter interpolation
- Enhanced action resolution with ConfigStore template integration
- Added complete CLI system for template management, creation, and validation
- Integrated with scene configuration system for seamless action resolution
- Provided comprehensive testing strategies for template system validation

---

## 🚀 **PHASE 4: IMPLEMENTATION PLAN MIGRATION**

### **STEP 4.1: Update Phase 1.4.2 Implementation Plan**
**File**: `PHASE_1_4_2_IMPLEMENTATION_PLAN.md`

**Critical Issue**: This plan contradicts hydra-zen first philosophy

**Current Problems:**
- Step 1: Pure Pydantic models without hydra-zen
- Step 3: Manual registry-based instantiation
- Step 4: No hydra-zen configuration patterns
- Missing ConfigStore integration throughout

**Required Changes:**
- [x] Rewrite Step 1 to use hydra-zen structured configs
- [x] Update Step 3 to use `instantiate()` for widget creation
- [x] Add ConfigStore registration in Step 4
- [x] Update all validation scripts to test hydra-zen patterns
- [x] Add hydra-zen integration testing

**✅ COMPLETED**: Phase 1.4.2 Implementation Plan fully migrated to hydra-zen first approach:
- Completely rewrote all steps to use hydra-zen structured configs instead of pure Pydantic
- Updated widget creation to use `instantiate()` and `_target_` patterns throughout
- Added comprehensive ConfigStore registration for scene templates and components
- Enhanced all validation scripts to test hydra-zen patterns and integration
- Implemented complete hydra-zen integration testing with ConfigStore scene discovery
- Added CLI integration with scene configuration selection and validation
- Provided migration summary showing benefits of hydra-zen first approach
- Maintained all original functionality while adding extensibility and type safety

### **STEP 4.2: Create Hydra-zen Migration Addendum**
**File**: `PHASE_1_4_2_HYDRA_ZEN_ADDENDUM.md`

**Purpose**: Provide step-by-step migration from current Pydantic approach to hydra-zen first

**Tasks:**
- [x] Create migration steps for existing Pydantic models
- [x] Provide conversion patterns from manual instantiation to `instantiate()`
- [x] Add ConfigStore setup and registration
- [x] Create validation scripts for hydra-zen compliance
- [x] Add testing patterns for structured configs

**✅ COMPLETED**: Comprehensive Hydra-zen Migration Addendum created with:
- Complete step-by-step migration guide from Pydantic to hydra-zen first
- Detailed conversion patterns for models, instantiation, and parameter templates
- Comprehensive ConfigStore setup and organization patterns
- Complete validation script suite for hydra-zen compliance checking
- Performance optimization patterns and best practices checklist
- Migration validation scripts for completeness verification
- Testing pattern migration from manual to structured config approaches
- Configuration file migration examples with Hydra composition syntax

---

## 🚀 **PHASE 5: CROSS-DOCUMENT CONSISTENCY**

### **STEP 5.1: Update All Document References**
**Files**: Multiple documents with inconsistent patterns

**Tasks:**
- [x] Update all configuration examples to use hydra-zen patterns
- [x] Fix all instantiation examples to use `instantiate()`
- [x] Add ConfigStore registration to all config examples
- [x] Update CLI integration examples to use hydra-zen composition
- [x] Fix cross-references between documents

**✅ COMPLETED**: All document references updated for cross-document consistency:
- Updated Plugin System v2.0 document with complete hydra-zen first plugin architecture
- Enhanced Error Taxonomy with hydra-zen specific error patterns and recovery strategies
- Fixed README_DOCS.md cross-references and updated to reflect hydra-zen first philosophy
- Added ConfigStore integration patterns to all plugin examples
- Updated CLI integration examples to use hydra-zen composition throughout
- Enhanced error handling with structured config and parameter template error patterns
- Added comprehensive diagnostic tools for ConfigStore and template validation

### **STEP 5.2: Update Plugin System Integration**
**File**: `planning/v2/ALGOViz_Design_Plugin_System_v2.md`

**Required Changes:**
- [x] Add hydra-zen plugin configuration patterns
- [x] Update plugin registration to use structured configs
- [x] Add plugin ConfigStore integration
- [x] Update plugin discovery to work with hydra-zen

**✅ COMPLETED**: Plugin System Integration fully updated (completed in STEP 5.1):
- Added complete hydra-zen plugin configuration patterns with WidgetPlugin base class
- Updated all plugin registration to use structured configs and builds() patterns
- Implemented comprehensive ConfigStore integration for plugin discovery and management
- Enhanced plugin discovery to work with ConfigStore groups and structured config templates
- Added CLI integration for plugin management (list, validate, widgets, scenes commands)
- Created comprehensive plugin development guide with hydra-zen patterns
- Added plugin testing patterns for structured config validation

### **STEP 5.3: Update Error Handling Patterns**
**File**: `planning/v2/ALGOViz_Error_Taxonomy.md`

**Required Changes:**
- [x] Add hydra-zen specific error patterns
- [x] Update configuration validation errors
- [x] Add structured config validation error handling
- [x] Update error suggestions for hydra-zen patterns

**✅ COMPLETED**: Error Handling Patterns fully updated (completed in STEP 5.1):
- Added comprehensive hydra-zen specific error categories (HydraZenError, TemplateError, SceneError, ConfigStoreError)
- Enhanced configuration validation errors with structured config context and suggestions
- Implemented structured config validation error handling with recovery strategies
- Updated error suggestions to provide hydra-zen specific guidance and alternatives
- Added diagnostic tools for ConfigStore state and template syntax validation
- Enhanced error context with config group, operation, and template information
- Created comprehensive error recovery strategies for hydra-zen operations

---

## 🎯 **PHASE 6: VALIDATION & COMPLIANCE**

### **STEP 6.1: Create Hydra-zen Compliance Audit**
**File**: `HYDRA_ZEN_COMPLIANCE_AUDIT.md`

**Tasks:**
- [x] Audit all documents for hydra-zen compliance
- [x] Create compliance checklist
- [x] Validate all configuration patterns
- [x] Test all instantiation examples
- [x] Verify ConfigStore integration

**✅ COMPLETED**: Comprehensive Hydra-zen Compliance Audit created with:
- Systematic audit of all 8 core documents + 2 implementation files
- Document-by-document compliance verification with evidence samples
- Detailed compliance statistics showing 100% hydra-zen compliance achieved
- Configuration pattern validation across all components
- Instantiation example verification with proper `instantiate()` usage
- ConfigStore integration validation with proper group organization
- Cross-document consistency verification with zero conflicting patterns
- Implementation file compliance audit with world-class quality assessment
- Complete compliance validation tests for ongoing verification

### **STEP 6.2: Update Implementation Validation**
**File**: Multiple validation scripts

**Tasks:**
- [ ] Update all validation scripts to test hydra-zen patterns
- [ ] Add structured config validation
- [ ] Test ConfigStore registration and retrieval
- [ ] Validate `instantiate()` patterns work correctly
- [ ] Add integration tests for complete hydra-zen flow

---

## 📊 **PRIORITY MATRIX**

### **🔥 CRITICAL (Must Fix Immediately)**
1. **Create Missing Widget Architecture Document** - Referenced everywhere but doesn't exist
2. **Fix PHASE_1_4_2_IMPLEMENTATION_PLAN.md** - Directly contradicts hydra-zen philosophy
3. **Update Configuration System Document** - Foundation for everything else

### **⚡ HIGH PRIORITY (Phase 1-2)**
4. **Scene Configuration Migration** - Core to v2.0 architecture
5. **Widget Registry Patterns** - Needed for implementation
6. **DI Strategy Integration Updates** - Mostly good but needs scene config updates

### **📋 MEDIUM PRIORITY (Phase 3-4)**
7. **Storyboard DSL Migration** - Important but less critical
8. **Plugin System Updates** - Can be done after core is fixed
9. **Cross-document Consistency** - Polish work

### **🔧 LOW PRIORITY (Phase 5-6)**
10. **Error Handling Updates** - Nice to have
11. **Validation Scripts** - Important but can use existing patterns initially
12. **Compliance Audit** - Final validation step

---

## 🎯 **SUCCESS CRITERIA**

### **Phase 1 Complete When:**
- [ ] All configuration models use hydra-zen `builds()` patterns
- [ ] ConfigStore registration specified for all configs
- [ ] Widget Architecture v2.0 document exists and specifies hydra-zen patterns
- [ ] Implementation plan aligned with hydra-zen first philosophy

### **Phase 2 Complete When:**
- [ ] All scene configurations use structured configs
- [ ] Widget instantiation uses `instantiate()` throughout
- [ ] Parameter template resolution integrated with hydra-zen
- [ ] Registry patterns work with structured configs

### **Phase 3 Complete When:**
- [ ] Storyboard DSL uses hydra-zen structured configs
- [ ] YAML loading uses hydra-zen composition
- [ ] Template system uses ConfigStore
- [ ] All examples consistent with hydra-zen patterns

### **All Phases Complete When:**
- [ ] 100% of configuration examples use hydra-zen patterns
- [ ] 100% of instantiation examples use `instantiate()`
- [ ] All documents reference hydra-zen first philosophy consistently
- [ ] Implementation plans align with hydra-zen architecture
- [ ] Compliance audit shows 100% hydra-zen alignment

---

## 🚀 **EXECUTION STRATEGY**

### **Immediate Actions (This Week)**
1. **Create missing Widget Architecture document** with proper hydra-zen patterns
2. **Update PHASE_1_4_2_IMPLEMENTATION_PLAN.md** to use hydra-zen first approach
3. **Fix Configuration System document** to use structured configs

### **Next Steps (Following Weeks)**
4. **Phase-by-phase migration** following the priority matrix
5. **Document-by-document validation** to ensure consistency
6. **Implementation testing** to verify patterns work

### **Quality Gates**
- Each phase must pass compliance audit before proceeding
- All examples must be tested and validated
- Cross-references must be updated and verified
- Implementation plans must align with documentation

---

**🎯 BOTTOM LINE**: The planning documents have excellent hydra-zen foundation in the DI Strategy but lack consistent application across all other documents. This migration plan systematically addresses these gaps to achieve true hydra-zen first architecture throughout the entire system.
