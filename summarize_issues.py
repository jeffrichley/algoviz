#!/usr/bin/env python3
"""
Quick summary of all quality issues found by collect_issues.py
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
    files_with_issues = 0
    issue_counts = defaultdict(int)
    
    ruff_issues = defaultdict(list)
    mypy_issues = []
    pytest_issues = []
    xenon_issues = []
    
    for json_file in issues_dir.glob("*.json"):
        total_files += 1
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        has_issues = False
        
        # Check ruff issues
        if data.get("ruff"):
            has_issues = True
            issue_counts["ruff"] += len(data["ruff"])
            for issue in data["ruff"]:
                ruff_issues[issue["code"]].append(data["file"])
        
        # Check mypy issues
        if data.get("mypy"):
            has_issues = True
            mypy_lines = data["mypy"].split('\n')
            mypy_issues.extend([(data["file"], line) for line in mypy_lines if line.strip()])
            issue_counts["mypy"] += len([l for l in mypy_lines if l.strip()])
        
        # Check pytest issues (coverage)
        if data.get("pytest"):
            has_issues = True
            pytest_issues.append((data["file"], data["pytest"]))
            issue_counts["pytest"] += 1
        
        # Check xenon complexity issues
        if data.get("xenon"):
            has_issues = True
            xenon_lines = data["xenon"].split('\n')
            xenon_issues.extend([(data["file"], line) for line in xenon_lines if line.strip()])
            issue_counts["xenon"] += len([l for l in xenon_lines if l.strip()])
        
        if has_issues:
            files_with_issues += 1
    
    print(f"📊 Quality Issues Summary")
    print(f"=" * 50)
    print(f"Total files analyzed: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Clean files: {total_files - files_with_issues}")
    print()
    
    print(f"🔍 Issue Breakdown:")
    for tool, count in issue_counts.items():
        print(f"  {tool}: {count} issues")
    
    if ruff_issues:
        print(f"\n🎯 Top Ruff Issues:")
        for code, files in sorted(ruff_issues.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"  {code}: {len(files)} files")
            for file in files[:3]:  # Show first 3 files
                print(f"    - {file}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")
    
    if mypy_issues:
        print(f"\n🔍 Sample MyPy Issues:")
        for file, issue in mypy_issues[:5]:
            print(f"  {file}: {issue}")
    
    if pytest_issues:
        print(f"\n🧪 Files with Test Coverage Issues:")
        for file, coverage in pytest_issues[:5]:
            print(f"  {file}: {coverage.strip()}")

if __name__ == "__main__":
    main()
