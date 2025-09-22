# ALGOViz Planning Documents v2.0

**Architecture Version:** v2.0 (Hydra-zen First Architecture)  
**Status:** Current  
**Previous Version:** planning/v1/ (archived)  
**Key Changes:** Hydra-zen first philosophy, multi-level widget hierarchy, scene configuration system, clean architecture

---

## 🏗️ **Architecture v2.0 Overview**

The v2.0 architecture addresses fundamental design flaws discovered during Phase 1.4 with **hydra-zen first philosophy**:
- **Hydra-zen First**: All configuration uses structured configs, builds(), and ConfigStore
- **Multi-Level Widget Hierarchy**: Pure visual primitives, generic data structures, domain-specific extensions
- **Configuration-Driven Event Binding**: Declarative scene configurations with hydra-zen parameter templates
- **Clean Architecture**: No algorithm-specific pollution in core components
- **Manim Integration**: Leverage existing Manim primitives, add ALGOViz-specific functionality

## 📚 **Document Categories**

### **Core Architecture Documents (v2.0 - Hydra-zen First)**
- [ALGOViz_Design_Widget_Architecture_v2.md](ALGOViz_Design_Widget_Architecture_v2.md) - **Complete hydra-zen first architecture** ✅
- [ALGOViz_Design_Widgets_Registry_v2.md](ALGOViz_Design_Widgets_Registry_v2.md) - Multi-level widget hierarchy with ConfigStore ✅
- [ALGOViz_Design_Director_v2.md](ALGOViz_Design_Director_v2.md) - Pure orchestrator with hydra-zen scene integration ✅
- [ALGOViz_Design_Storyboard_DSL_v2.md](ALGOViz_Design_Storyboard_DSL_v2.md) - Hydra-zen storyboard templates ✅

### **Integration Documents (v2.0 - Hydra-zen Enhanced)**
- [ALGOViz_Design_Adapters_VizEvents_v2.md](ALGOViz_Design_Adapters_VizEvents_v2.md) - Scene configuration routing ✅
- [ALGOViz_PRD_v2.md](ALGOViz_PRD_v2.md) - Updated phases and widget naming ✅
- [ALGOViz_SDD_v2.md](ALGOViz_SDD_v2.md) - Multi-level package structure ✅

### **Infrastructure Documents (v2.0 - Hydra-zen First)**
- [ALGOViz_Design_Plugin_System_v2.md](ALGOViz_Design_Plugin_System_v2.md) - Hydra-zen plugin architecture ✅
- [ALGOViz_Design_DI_Strategy_v2.md](ALGOViz_Design_DI_Strategy_v2.md) - Hydra-zen first DI patterns ✅
- [ALGOViz_Design_Config_System.md](ALGOViz_Design_Config_System.md) - Hydra-zen configuration system ✅
- [ALGOViz_Error_Taxonomy.md](ALGOViz_Error_Taxonomy.md) - Enhanced with hydra-zen error patterns ✅

### **Infrastructure Documents (v2.0 - Compatible)**
- [ALGOViz_Design_TimingConfig.md](ALGOViz_Design_TimingConfig.md) - Compatible with hydra-zen ✅
- [ALGOViz_Design_Voiceover.md](ALGOViz_Design_Voiceover.md) - Compatible with hydra-zen ✅
- [ALGOViz_Design_Rendering_Export.md](ALGOViz_Design_Rendering_Export.md) - Compatible with hydra-zen ✅
- [ALGOViz_Vision_Goals.md](ALGOViz_Vision_Goals.md) - Compatible with hydra-zen ✅
- [ALGOViz_Scenario_Theme_Merge_Precedence.md](ALGOViz_Scenario_Theme_Merge_Precedence.md) - Compatible with hydra-zen ✅

## 🔄 **Migration from v1.0**

### **Breaking Changes**
- Widget contract no longer includes event handling
- Algorithm-specific actions moved from Director to scene configurations
- Multi-level widget hierarchy replaces single-level system

### **What's Preserved**
- Storyboard DSL structure (Acts → Shots → Beats)
- VizEvent system and algorithm adapters
- Timing system and configuration management
- Error taxonomy and CLI framework

### **Implementation Impact**
See [Implementation_Plan.md](../../Implementation_Plan.md) Phase 1.4.1-2.1 for implementation details.

## 📖 **Reading Guide**

### **For New Contributors**
1. Start with [ALGOViz_Vision_Goals.md](ALGOViz_Vision_Goals.md) - Project vision and goals
2. Review [ALGOViz_Design_Widget_Architecture_v2.md](../v1/ALGOViz_Design_Widget_Architecture_v2.md) - Core architecture
3. Understand configuration system: [ALGOViz_Design_Config_System.md](ALGOViz_Design_Config_System.md)

### **For Algorithm Developers**
1. Widget system: [ALGOViz_Design_Widgets_Registry_v2.md](ALGOViz_Design_Widgets_Registry_v2.md) ✅
2. Event system: [ALGOViz_Design_Adapters_VizEvents_v2.md](ALGOViz_Design_Adapters_VizEvents_v2.md) ✅
3. Storyboard DSL: [ALGOViz_Design_Storyboard_DSL_v2.md](ALGOViz_Design_Storyboard_DSL_v2.md) ✅

### **For Framework Contributors**
1. System architecture: [ALGOViz_SDD_v2.md](ALGOViz_SDD_v2.md) ✅
2. Director orchestration: [ALGOViz_Design_Director_v2.md](ALGOViz_Design_Director_v2.md) ✅
3. Plugin system: [ALGOViz_Design_Plugin_System_v2.md](ALGOViz_Design_Plugin_System_v2.md) ✅

## 📋 **Document Status Legend**

- ✅ **Complete (v2.0)** - Document migrated and ready
- 🔄 **In Progress** - Currently being migrated
- ⏳ **Planned** - Scheduled for future migration phases
- 📁 **Reference** - Located in planning/v1/ for reference only

---

**Note**: This documentation represents the complete v2.0 architecture migration. All documents are now available and ready for implementation.

## 🚀 **Quick Reference**

### **Essential Documents for Implementation**
- **Start Here**: [ALGOViz_Vision_Goals.md](ALGOViz_Vision_Goals.md) - Project vision and principles
- **Architecture**: [ALGOViz_Design_Widget_Architecture_v2.md](ALGOViz_Design_Widget_Architecture_v2.md) - Core v2.0 hydra-zen first architecture
- **Configuration**: [ALGOViz_Design_Config_System.md](ALGOViz_Design_Config_System.md) - Hydra-zen configuration system
- **System Design**: [ALGOViz_SDD_v2.md](ALGOViz_SDD_v2.md) - Complete technical architecture
- **Implementation Plan**: [Implementation_Plan.md](../../Implementation_Plan.md) - Development roadmap

### **Core Framework Components**
- **Widgets**: [ALGOViz_Design_Widgets_Registry_v2.md](ALGOViz_Design_Widgets_Registry_v2.md) - Multi-level widget hierarchy
- **Director**: [ALGOViz_Design_Director_v2.md](ALGOViz_Design_Director_v2.md) - Pure orchestrator with SceneEngine
- **Storyboard**: [ALGOViz_Design_Storyboard_DSL_v2.md](ALGOViz_Design_Storyboard_DSL_v2.md) - Generic actions with scene configuration
- **Events**: [ALGOViz_Design_Adapters_VizEvents_v2.md](ALGOViz_Design_Adapters_VizEvents_v2.md) - Algorithm event system

## 🎯 **Implementation Guidance**

### **Phase 1.4.1 - Director Architecture Cleanup**
**Primary Documents:**
- [ALGOViz_Design_Director_v2.md](ALGOViz_Design_Director_v2.md) - Pure orchestrator specification
- [ALGOViz_Design_Widget_Architecture_v2.md](../v1/ALGOViz_Design_Widget_Architecture_v2.md) - SceneEngine integration
- [ALGOViz_Design_Widgets_Registry_v2.md](ALGOViz_Design_Widgets_Registry_v2.md) - Widget contract without event handling

### **Phase 2.1 - Widget Architecture Foundation**
**Primary Documents:**
- [ALGOViz_Design_Widgets_Registry_v2.md](ALGOViz_Design_Widgets_Registry_v2.md) - Complete multi-level hierarchy
- [ALGOViz_Design_Widget_Architecture_v2.md](../v1/ALGOViz_Design_Widget_Architecture_v2.md) - Architecture specification
- [ALGOViz_SDD_v2.md](ALGOViz_SDD_v2.md) - Package structure and integration

## 📊 **Documentation Metrics**

### **Migration Statistics**
- **Total Documents**: 16 documents
- **V2.0 Versioned**: 8 documents (major updates/rewrites)
- **Unchanged**: 8 documents (no conflicts with v2.0)
- **Total Lines**: ~6,000 lines of comprehensive documentation
- **Migration Completion**: 100% (420 minutes across 6 phases)

### **Architecture Coverage**
- **Widget Architecture v2.0**: ✅ Complete specification
- **Scene Configuration System**: ✅ Fully documented
- **Multi-Level Widget Hierarchy**: ✅ 3-level system specified
- **Pure Orchestrator Director**: ✅ Clean architecture documented
- **Plugin System**: ✅ Extensible architecture specified
- **Zero Algorithm Pollution**: ✅ Achieved across all core components

## 🔧 **Troubleshooting & Support**

### **Common Questions**
- **Q**: Where do I start reading the documentation?
- **A**: Begin with [ALGOViz_Vision_Goals.md](ALGOViz_Vision_Goals.md), then [ALGOViz_Design_Config_System.md](ALGOViz_Design_Config_System.md) for hydra-zen patterns, then [ALGOViz_Design_Widget_Architecture_v2.md](ALGOViz_Design_Widget_Architecture_v2.md)

- **Q**: How do I implement a new algorithm?
- **A**: Follow the algorithm developer reading guide above, starting with [ALGOViz_Design_Adapters_VizEvents_v2.md](ALGOViz_Design_Adapters_VizEvents_v2.md)

- **Q**: What's the difference between v1.0 and v2.0?
- **A**: v2.0 introduces hydra-zen first architecture, eliminates BFS-specific pollution, and features multi-level widget hierarchy with structured config scene configuration

### **Implementation Support**
- **Development Roadmap**: [Implementation_Plan.md](../../Implementation_Plan.md)
- **Architecture Reference**: [ALGOViz_Design_Widget_Architecture_v2.md](../v1/ALGOViz_Design_Widget_Architecture_v2.md)
- **Error Handling**: [ALGOViz_Error_Taxonomy.md](ALGOViz_Error_Taxonomy.md)
- **Configuration**: [ALGOViz_Design_Config_System.md](ALGOViz_Design_Config_System.md)

---

**ALGOViz v2.0 Documentation - Hydra-zen First Architecture - Complete and Ready for Implementation** ✅
