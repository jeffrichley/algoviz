#!/usr/bin/env python3
"""Validate that migration from Pydantic to hydra-zen is complete."""

import ast
import sys
from pathlib import Path


def check_file_for_hydra_zen_patterns(file_path: Path) -> dict:
    """Check if file uses hydra-zen patterns."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        patterns = {
            "has_builds_import": "from hydra_zen import builds" in content,
            "has_instantiate_import": "from hydra_zen import" in content and "instantiate" in content,
            "has_configstore_import": "from hydra.core.config_store import ConfigStore" in content,
            "uses_builds": "builds(" in content,
            "uses_instantiate": "instantiate(" in content,
            "uses_zen_partial": "zen_partial=True" in content,
            "has_make_config": "make_config(" in content,
            "has_omegaconf": "from omegaconf import" in content
        }
        
        return patterns
        
    except Exception as e:
        return {"error": str(e)}


def validate_core_files_migration():
    """Validate core files have been migrated to hydra-zen."""
    core_files = [
        "src/agloviz/core/scene.py",
        "src/agloviz/core/resolvers.py",
        "src/agloviz/config/models.py",
        "src/agloviz/widgets/registry.py"
    ]
    
    results = {}
    
    for file_path in core_files:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️ File not found: {file_path}")
            results[file_path] = {"status": "missing"}
            continue
        
        patterns = check_file_for_hydra_zen_patterns(path)
        
        if patterns.get("error"):
            print(f"❌ Error checking {file_path}: {patterns['error']}")
            results[file_path] = {"status": "error", "error": patterns["error"]}
            continue
        
        # Check for hydra-zen patterns
        hydra_zen_score = sum([
            patterns.get("has_builds_import", False),
            patterns.get("has_instantiate_import", False),
            patterns.get("has_configstore_import", False),
            patterns.get("uses_builds", False),
            patterns.get("uses_instantiate", False)
        ])
        
        if hydra_zen_score >= 3:
            print(f"✅ {file_path} uses hydra-zen patterns (score: {hydra_zen_score}/5)")
            results[file_path] = {"status": "migrated", "score": hydra_zen_score, "patterns": patterns}
        else:
            print(f"⚠️ {file_path} may need hydra-zen migration (score: {hydra_zen_score}/5)")
            results[file_path] = {"status": "needs_migration", "score": hydra_zen_score, "patterns": patterns}
    
    return results


def validate_test_files_migration():
    """Validate test files have been updated for hydra-zen patterns."""
    test_files = [
        "tests/unit/test_hydra_zen_migration_step1.py",
        "tests/unit/test_hydra_zen_migration_step2.py", 
        "tests/unit/test_hydra_zen_migration_step3.py",
        "tests/unit/test_hydra_zen_migration_step4.py",
        "tests/unit/test_hydra_zen_migration_step5.py",
        "tests/unit/test_hydra_zen_migration_step6.py",
        "tests/unit/test_config_models.py"
    ]
    
    results = {}
    
    for file_path in test_files:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️ Test file not found: {file_path}")
            results[file_path] = {"status": "missing"}
            continue
        
        patterns = check_file_for_hydra_zen_patterns(path)
        
        if patterns.get("error"):
            print(f"❌ Error checking {file_path}: {patterns['error']}")
            results[file_path] = {"status": "error", "error": patterns["error"]}
            continue
        
        # Test files should have instantiate usage
        if patterns.get("uses_instantiate", False):
            print(f"✅ {file_path} includes hydra-zen test patterns")
            results[file_path] = {"status": "migrated", "patterns": patterns}
        else:
            print(f"⚠️ {file_path} may need hydra-zen test migration")
            results[file_path] = {"status": "needs_migration", "patterns": patterns}
    
    return results


def validate_configuration_files():
    """Validate configuration files exist and use proper Hydra patterns."""
    config_dir = Path("configs")
    
    if not config_dir.exists():
        print("❌ configs/ directory not found")
        return {"status": "missing"}
    
    required_patterns = [
        ("_target_", "Configuration files should use _target_ for instantiation"),
        ("# @package", "Configuration files should use @package annotations")
    ]
    
    config_files = list(config_dir.rglob("*.yaml"))
    results = {}
    
    for config_file in config_files:
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            patterns_found = []
            for pattern, description in required_patterns:
                if pattern in content:
                    patterns_found.append(pattern)
            
            try:
                relative_path = str(config_file.relative_to(Path.cwd()))
            except ValueError:
                # Handle absolute path case
                relative_path = str(config_file)
            
            if len(patterns_found) >= 1:  # At least one Hydra pattern
                print(f"✅ {relative_path} uses Hydra patterns: {patterns_found}")
                results[relative_path] = {"status": "hydra_compatible", "patterns": patterns_found}
            else:
                print(f"⚠️ {relative_path} may need Hydra patterns")
                results[relative_path] = {"status": "needs_hydra_patterns", "patterns": patterns_found}
                
        except Exception as e:
            print(f"❌ Error reading {config_file}: {e}")
            results[str(config_file)] = {"status": "error", "error": str(e)}
    
    return results


def validate_planning_document_consistency():
    """Validate planning documents reference hydra-zen patterns."""
    planning_docs = [
        "planning/v2/ALGOViz_Design_Config_System.md",
        "planning/v2/ALGOViz_Design_DI_Strategy_v2.md", 
        "planning/v2/ALGOViz_Design_Widget_Architecture_v2.md",
        "planning/v2/ALGOViz_Design_Storyboard_DSL_v2.md",
        "PHASE_1_4_2_HYDRA_ZEN_ADDENDUM.md"
    ]
    
    required_terms = ["hydra-zen", "builds()", "ConfigStore", "instantiate()"]
    results = {}
    
    for doc_path in planning_docs:
        path = Path(doc_path)
        if not path.exists():
            print(f"⚠️ Planning document not found: {doc_path}")
            results[doc_path] = {"status": "missing"}
            continue
        
        try:
            with open(path, 'r') as f:
                content = f.read()
            
            found_terms = [term for term in required_terms if term in content]
            missing_terms = [term for term in required_terms if term not in content]
            
            if len(found_terms) >= 3:  # Most hydra-zen terms present
                print(f"✅ {doc_path} includes hydra-zen patterns: {found_terms}")
                results[doc_path] = {"status": "updated", "found_terms": found_terms}
            else:
                print(f"⚠️ {doc_path} missing hydra-zen terms: {missing_terms}")
                results[doc_path] = {"status": "needs_update", "missing_terms": missing_terms}
                
        except Exception as e:
            print(f"❌ Error reading {doc_path}: {e}")
            results[doc_path] = {"status": "error", "error": str(e)}
    
    return results


def validate_import_patterns():
    """Validate that files use proper hydra-zen import patterns."""
    python_files = []
    
    # Find all Python files in src/
    src_dir = Path("src")
    if src_dir.exists():
        python_files.extend(src_dir.rglob("*.py"))
    
    # Find test files
    tests_dir = Path("tests")
    if tests_dir.exists():
        python_files.extend(tests_dir.rglob("test_*.py"))
    
    import_analysis = {
        "hydra_zen_imports": 0,
        "configstore_imports": 0,
        "omegaconf_imports": 0,
        "total_files": len(python_files),
        "files_with_hydra_zen": []
    }
    
    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                content = f.read()
            
            has_hydra_zen = "from hydra_zen import" in content
            has_configstore = "from hydra.core.config_store import" in content
            has_omegaconf = "from omegaconf import" in content
            
            if has_hydra_zen:
                import_analysis["hydra_zen_imports"] += 1
                import_analysis["files_with_hydra_zen"].append(str(py_file))
            
            if has_configstore:
                import_analysis["configstore_imports"] += 1
            
            if has_omegaconf:
                import_analysis["omegaconf_imports"] += 1
                
        except Exception as e:
            print(f"⚠️ Error analyzing {py_file}: {e}")
    
    print(f"📊 Import Analysis:")
    print(f"  Total Python files: {import_analysis['total_files']}")
    print(f"  Files with hydra-zen imports: {import_analysis['hydra_zen_imports']}")
    print(f"  Files with ConfigStore imports: {import_analysis['configstore_imports']}")
    print(f"  Files with OmegaConf imports: {import_analysis['omegaconf_imports']}")
    
    return import_analysis


def main():
    """Run migration completeness validation."""
    print("🔍 Validating migration completeness...")
    print("=" * 60)
    
    validation_functions = [
        ("Core Files Migration", validate_core_files_migration),
        ("Test Files Migration", validate_test_files_migration),
        ("Configuration Files", validate_configuration_files),
        ("Planning Document Consistency", validate_planning_document_consistency),
        ("Import Patterns", validate_import_patterns)
    ]
    
    all_results = {}
    
    for name, validation_func in validation_functions:
        print(f"\n🔸 {name}")
        print("-" * 40)
        try:
            result = validation_func()
            all_results[name] = result
        except Exception as e:
            print(f"❌ FAILED with exception: {e}")
            all_results[name] = {"error": str(e)}
    
    print("\n" + "=" * 60)
    print("📊 MIGRATION COMPLETENESS SUMMARY")
    print("=" * 60)
    
    # Analyze core files
    core_results = all_results.get("Core Files Migration", {})
    migrated_core = sum(1 for result in core_results.values() 
                       if isinstance(result, dict) and result.get("status") == "migrated")
    total_core = len(core_results)
    
    print(f"Core Files: {migrated_core}/{total_core} migrated to hydra-zen")
    
    # Analyze test files
    test_results = all_results.get("Test Files Migration", {})
    migrated_tests = sum(1 for result in test_results.values()
                        if isinstance(result, dict) and result.get("status") == "migrated")
    total_tests = len(test_results)
    
    print(f"Test Files: {migrated_tests}/{total_tests} include hydra-zen patterns")
    
    # Analyze config files
    config_results = all_results.get("Configuration Files", {})
    if isinstance(config_results, dict) and "status" not in config_results:
        hydra_configs = sum(1 for result in config_results.values()
                           if isinstance(result, dict) and result.get("status") == "hydra_compatible")
        total_configs = len(config_results)
        print(f"Config Files: {hydra_configs}/{total_configs} use Hydra patterns")
    
    # Analyze planning docs
    doc_results = all_results.get("Planning Document Consistency", {})
    updated_docs = sum(1 for result in doc_results.values()
                      if isinstance(result, dict) and result.get("status") == "updated")
    total_docs = len(doc_results)
    
    print(f"Planning Docs: {updated_docs}/{total_docs} reference hydra-zen")
    
    # Overall assessment
    migration_score = (migrated_core / max(total_core, 1) + 
                      migrated_tests / max(total_tests, 1) + 
                      updated_docs / max(total_docs, 1)) / 3
    
    print(f"\nOverall Migration Score: {migration_score:.2%}")
    
    if migration_score >= 0.8:
        print("🎉 Migration is substantially complete!")
        return 0
    elif migration_score >= 0.6:
        print("⚠️ Migration is mostly complete but needs some work")
        return 1
    else:
        print("❌ Migration needs significant work")
        return 2


if __name__ == "__main__":
    sys.exit(main())
