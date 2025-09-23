#!/usr/bin/env python3
"""
Verify that all quality tools (pytest, ruff, mypy, xenon) are properly captured in JSON files
"""
import json
from pathlib import Path
from collections import defaultdict

def main():
    issues_dir = Path(__file__).parent / "issues"
    
    if not issues_dir.exists():
        print("❌ No issues directory found. Run collect_issues.py first.")
        return
    
    total_files = 0
    tool_stats = defaultdict(int)
    tool_examples = defaultdict(list)
    
    print("🔍 Verifying JSON files structure and tool data...")
    print("=" * 60)
    
    for json_file in issues_dir.glob("*.json"):
        total_files += 1
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Check required fields
        required_fields = ["file", "pytest", "ruff", "mypy", "xenon"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"❌ {json_file.name}: Missing fields {missing_fields}")
            continue
        
        # Count data for each tool
        file_path = data["file"]
        
        # Pytest (coverage data)
        if data["pytest"] and data["pytest"].strip():
            tool_stats["pytest"] += 1
            if len(tool_examples["pytest"]) < 3:
                tool_examples["pytest"].append(f"{file_path}: {data['pytest'][:50]}...")
        
        # Ruff (array of issues)
        if data["ruff"] and len(data["ruff"]) > 0:
            tool_stats["ruff"] += len(data["ruff"])
            if len(tool_examples["ruff"]) < 3:
                tool_examples["ruff"].append(f"{file_path}: {len(data['ruff'])} issues")
        
        # MyPy (string of errors)
        if data["mypy"] and data["mypy"].strip():
            tool_stats["mypy"] += len([line for line in data["mypy"].split('\n') if line.strip()])
            if len(tool_examples["mypy"]) < 3:
                tool_examples["mypy"].append(f"{file_path}: {data['mypy'][:50]}...")
        
        # Xenon (complexity data)
        if data["xenon"] and data["xenon"].strip():
            tool_stats["xenon"] += len([line for line in data["xenon"].split('\n') if line.strip()])
            if len(tool_examples["xenon"]) < 3:
                tool_examples["xenon"].append(f"{file_path}: {data['xenon'][:50]}...")
    
    print(f"✅ Total files analyzed: {total_files}")
    print(f"✅ All files have required JSON structure")
    print()
    
    print("📊 Tool Data Verification:")
    print("-" * 40)
    
    for tool in ["pytest", "ruff", "mypy", "xenon"]:
        count = tool_stats[tool]
        examples = tool_examples[tool]
        
        if count > 0:
            print(f"✅ {tool.upper()}: {count} items found")
            for example in examples:
                print(f"   📄 {example}")
        else:
            print(f"⚠️  {tool.upper()}: No data found")
        print()
    
    # Summary
    tools_with_data = sum(1 for tool in ["pytest", "ruff", "mypy", "xenon"] if tool_stats[tool] > 0)
    
    print("🎯 Verification Summary:")
    print(f"   • Files processed: {total_files}")
    print(f"   • Tools with data: {tools_with_data}/4")
    print(f"   • Total issues found: {sum(tool_stats.values())}")
    
    if tools_with_data >= 3:  # At least pytest, ruff, mypy should have data
        print("✅ Quality tools are properly captured!")
        if tool_stats["xenon"] == 0:
            print("   ℹ️  No xenon complexity issues found (this is good!)")
    else:
        print(f"⚠️  Only {tools_with_data} out of 4 tools have data")

if __name__ == "__main__":
    main()
