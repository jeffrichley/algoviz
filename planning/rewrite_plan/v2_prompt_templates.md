## 🎯 **Google-Level AI Agent Prompt Templates**

### **INPUT TEMPLATE: AI Agent Session Prompt**

```markdown
# ALGOViz Documentation Migration: [PHASE_NAME] Execution

## 🌟 **MISSION OVERVIEW**
You are executing a critical architectural migration for ALGOViz, a world-class algorithm visualization framework. During Phase 1.4 Director Implementation, we discovered fundamental design flaws: BFS-specific pollution in supposedly generic components. This threatens the framework's ability to support multiple algorithm types.

**Your Role**: Execute [PHASE_NAME] of a systematic documentation migration to establish clean, generic architecture that can support any algorithm type while maintaining Google-level engineering standards.

## 🏗️ **ARCHITECTURAL CONTEXT**

### **The Problem We're Solving**
- **Current State**: BFS-specific pollution in Director, widgets, and routing systems
- **Target State**: Multi-level widget hierarchy with scene configuration system
- **Critical Impact**: Framework must support sorting, trees, graphs - not just pathfinding

### **Architecture v2.0 Vision**
- **Level 1**: Pure visual primitives (Manim integration)
- **Level 2**: Generic data structure widgets (ArrayWidget, QueueWidget, TreeWidget)
- **Level 3**: Domain-specific extensions (PathfindingGrid, SortingArray)
- **Scene Configuration**: Declarative event binding with parameter templates
- **Hydra-Zen First**: Type-safe configuration system

### **Quality Standards**
- **Zero Algorithm-Specific Pollution** in core components
- **Complete Separation** of visual operations from algorithm semantics
- **Configuration-Driven** event handling (no hard-coded widget methods)
- **Plugin-Ready** architecture for extensibility
- **Manim Integration** without duplication

## 📋 **YOUR SPECIFIC MISSION: [PHASE_NAME]**

### **Phase Scope**
**Duration**: [ESTIMATED_TIME]  
**Documents**: [DOCUMENT_COUNT]  
**Complexity**: [COMPLEXITY_LEVEL]

### **Input Documents**
[DOCUMENT_LIST_WITH_CATEGORIES]

### **Expected Outputs**
[SPECIFIC_DELIVERABLES]

### **Success Criteria**
[PHASE_SPECIFIC_CRITERIA]

## 📚 **REFERENCE MATERIALS**

### **Primary References**
- **Migration Plan**: [Attach v2_plan.md] - Your detailed execution guide
- **Architecture Spec**: [Attach ALGOViz_Design_Widget_Architecture_v2.md] - Complete v2.0 architecture
- **Conflict Analysis**: [Attach v2_assessment.md] - Specific conflicts to resolve

### **Source Documents**
[ATTACH_RELEVANT_V1_DOCUMENTS]

### **Previous Phase Outputs** (if applicable)
[ATTACH_PREVIOUS_OUTPUTS]

## 🎯 **EXECUTION REQUIREMENTS**

### **Critical Rules**
1. **Follow the Plan Exactly**: Execute only your assigned phase steps
2. **Zero Tolerance for Pollution**: No algorithm-specific concepts in generic components
3. **Maintain Cross-References**: Update all internal document links
4. **Preserve Quality**: Match Google-level documentation standards
5. **Validate Output**: Check your work against success criteria

### **Document Standards**
- **Headers**: Use v2.0 versioning format
- **Structure**: Follow planned section organization
- **Examples**: Use generic methods, not algorithm-specific
- **Cross-References**: Point to v2.0 documents only
- **Code Blocks**: Use proper syntax highlighting and formatting

### **Validation Requirements**
- **Architecture Alignment**: All content must align with Widget Architecture v2.0
- **Conflict Resolution**: Address all identified conflicts from assessment
- **Consistency**: Maintain consistent terminology and examples
- **Completeness**: All planned sections must be implemented

## 🚀 **EXECUTION DIRECTIVE**

Execute [PHASE_NAME] following the detailed steps in v2_plan.md. Report completion status using the End of Execution Template. Ensure zero conflicts with Widget Architecture v2.0.

**Begin execution now.**
```








---

### **END OF EXECUTION TEMPLATE: Validation and Completion Report**

```markdown
# [PHASE_NAME] Execution Report

## ✅ **COMPLETION STATUS**

**Phase**: [PHASE_NAME]  
**Execution Time**: [ACTUAL_TIME]  
**Documents Processed**: [ACTUAL_COUNT]  
**Status**: [COMPLETED/PARTIAL/FAILED]

## 📊 **DELIVERABLES SUMMARY**

### **Documents Created/Updated**
[LIST_ALL_OUTPUT_FILES]

### **Key Changes Made**
[SUMMARIZE_MAJOR_CHANGES]

### **Architecture Compliance**
- [ ] No algorithm-specific pollution in core components
- [ ] Multi-level widget hierarchy referenced correctly
- [ ] Scene configuration system integrated
- [ ] Generic widget methods used (no BFS-specific methods)
- [ ] Manim integration approach followed

## 🔍 **CONFLICT RESOLUTION VERIFICATION**

### **Widget Contract Conflicts** ✅/❌
- [ ] Removed `update(scene, event, run_time)` from widget protocols
- [ ] Added pure visual operation methods only
- [ ] Scene configuration event handling documented

### **Algorithm-Specific Action Conflicts** ✅/❌  
- [ ] Removed `place_start`, `place_goal`, `place_obstacles` from core actions
- [ ] Moved algorithm-specific actions to scene configurations
- [ ] Updated action resolution to use scene system

### **Routing System Conflicts** ✅/❌
- [ ] Replaced hard-coded BFS methods (`highlight_enqueue`, `mark_frontier`)
- [ ] Updated to use generic widget methods (`highlight_element`, `enqueue`)
- [ ] Scene configuration routing examples provided

### **Package Structure Conflicts** ✅/❌
- [ ] Updated to multi-level widget hierarchy
- [ ] Primitives/structures/layouts/domains organization shown
- [ ] Plugin integration architecture documented

## 🔗 **CROSS-REFERENCE VALIDATION**

### **Internal References Check**
```bash
# Run this validation
grep -r "\[.*\](.*\.md" [OUTPUT_DIRECTORY] | grep -v "_v2.md" | grep -v "v1/"
```
**Result**: [BROKEN_REFERENCES_COUNT] broken references found

### **Architecture v2.0 Alignment Check**
- [ ] All examples use Widget Architecture v2.0 patterns
- [ ] All integration points reference scene configuration system
- [ ] All plugin examples use new architecture
- [ ] All code examples follow v2.0 conventions

## 🧪 **QUALITY ASSURANCE**

### **Documentation Standards**
- [ ] Headers use v2.0 versioning format
- [ ] Section structure follows planned organization
- [ ] Code blocks have proper syntax highlighting
- [ ] Examples are clear and consistent
- [ ] Cross-references work correctly

### **Content Quality**
- [ ] Technical accuracy verified
- [ ] Examples are realistic and useful
- [ ] Integration points clearly documented
- [ ] Migration guidance provided where needed

## ⚠️ **ISSUES IDENTIFIED**

### **Conflicts with Previous Phases**
[LIST_ANY_CONFLICTS_WITH_PREVIOUS_WORK]

### **Unresolved Issues**
[LIST_ANY_ISSUES_THAT_NEED_ATTENTION]

### **Recommendations for Next Phase**
[RECOMMENDATIONS_FOR_SUBSEQUENT_PHASES]

## 🎯 **NEXT PHASE READINESS**

### **Prerequisites for Next Phase**
- [ ] All deliverables completed and validated
- [ ] Cross-references updated correctly
- [ ] No architecture conflicts remain
- [ ] Output files ready for next phase consumption

### **Handoff to Next Phase**
**Ready for Next Phase**: ✅/❌  
**Blocking Issues**: [NONE/LIST_ISSUES]  
**Special Instructions for Next Phase**: [ANY_SPECIAL_NOTES]

## 📋 **EXECUTION CHECKLIST VERIFICATION**

### **Phase-Specific Checklist** (from v2_plan.md)
[COPY_RELEVANT_CHECKLIST_FROM_PLAN]

**All Items Completed**: ✅/❌

### **Quality Gates** (from v2_plan.md)
[COPY_RELEVANT_QUALITY_GATES_FROM_PLAN]

**All Gates Passed**: ✅/❌

## 🚀 **FINAL VALIDATION**

### **Architecture v2.0 Compliance Score**
- **Widget Hierarchy Compliance**: [SCORE]/10
- **Scene Configuration Integration**: [SCORE]/10  
- **Generic Core Components**: [SCORE]/10
- **Manim Integration Approach**: [SCORE]/10
- **Plugin Architecture Readiness**: [SCORE]/10

**Overall Compliance Score**: [TOTAL_SCORE]/50

### **Ready for Production**
**Assessment**: [READY/NEEDS_WORK/BLOCKED]  
**Confidence Level**: [HIGH/MEDIUM/LOW]  
**Recommendation**: [PROCEED/REVISE/ESCALATE]

---

## 📤 **OUTPUTS FOR NEXT PHASE**

### **Files to Hand Off**
[LIST_ALL_OUTPUT_FILES_WITH_PATHS]

### **Context for Next Agent**
[BRIEF_SUMMARY_FOR_NEXT_AGENT]

### **Validation Status**
All outputs validated against Widget Architecture v2.0: ✅/❌
```

---

## 🎯 **USAGE PATTERN**

### **For Each Phase:**
1. **Fill Input Template** with phase-specific details
2. **Attach Relevant Documents** (plan + source docs + previous outputs)
3. **Execute Phase** with AI agent
4. **Validate Output** using End Template
5. **Hand Off to Next Phase** with validated outputs

### **Template Customization Variables:**
- `[PHASE_NAME]` - e.g., "Phase 2: Copy Unchanged Documents"
- `[ESTIMATED_TIME]` - e.g., "15 minutes"
- `[DOCUMENT_COUNT]` - e.g., "8 documents"
- `[COMPLEXITY_LEVEL]` - e.g., "Low (copy and header updates)"
- `[DOCUMENT_LIST_WITH_CATEGORIES]` - Specific docs for this phase
- `[SPECIFIC_DELIVERABLES]` - What should be produced
- `[PHASE_SPECIFIC_CRITERIA]` - Success criteria for this phase

This approach provides **Google-level context engineering** with systematic validation, clear handoffs, and comprehensive quality assurance at each step.