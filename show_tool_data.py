#!/usr/bin/env python3
"""
Show examples of data captured by each quality tool
"""
import json
from pathlib import Path

def main():
    issues_dir = Path(__file__).parent / "issues"
    
    # Find examples of each tool's data
    examples = {}
    
    for json_file in issues_dir.glob("*.json"):
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        file_path = data["file"]
        
        # Find pytest example
        if data["pytest"] and data["pytest"].strip() and "pytest" not in examples:
            examples["pytest"] = (file_path, data["pytest"])
        
        # Find ruff example
        if data["ruff"] and len(data["ruff"]) > 0 and "ruff" not in examples:
            examples["ruff"] = (file_path, data["ruff"][:2])  # First 2 issues
        
        # Find mypy example
        if data["mypy"] and data["mypy"].strip() and "mypy" not in examples:
            examples["mypy"] = (file_path, data["mypy"])
        
        # Find xenon example
        if data["xenon"] and data["xenon"].strip() and "xenon" not in examples:
            examples["xenon"] = (file_path, data["xenon"])
        
        # Stop when we have all examples
        if len(examples) >= 4:
            break
    
    print("🔍 Tool Data Examples:")
    print("=" * 60)
    
    for tool, (file_path, data) in examples.items():
        print(f"\n📊 {tool.upper()} - {file_path}")
        print("-" * 50)
        
        if tool == "pytest":
            print("Coverage data:")
            print(f"  {data}")
        elif tool == "ruff":
            print("Issue details:")
            for i, issue in enumerate(data):
                print(f"  Issue {i+1}: {issue['code']} - {issue['message']}")
                print(f"    Location: line {issue['location']['row']}, col {issue['location']['column']}")
        elif tool == "mypy":
            print("Type checking errors:")
            for line in data.split('\n')[:3]:  # First 3 lines
                if line.strip():
                    print(f"  {line}")
        elif tool == "xenon":
            print("Complexity data:")
            print(f"  {data}")
    
    if "xenon" not in examples:
        print(f"\n📊 XENON - No complexity issues found")
        print("-" * 50)
        print("  ✅ Your code has good complexity levels!")

if __name__ == "__main__":
    main()
