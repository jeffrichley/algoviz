#!/usr/bin/env python3
import subprocess
import json
import sys
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).parent
ISSUES_DIR = ROOT / "issues"
ISSUES_DIR.mkdir(exist_ok=True)

# Create directory structure
FOUND_DIR = ISSUES_DIR / "found"
ASSIGNED_DIR = ISSUES_DIR / "assigned"
CLEAN_DIR = ISSUES_DIR / "clean"

def run(cmd):
    """Run a command through uv run and return stdout as text."""
    result = subprocess.run(
        ["uv", "run"] + cmd,
        capture_output=True,
        text=True
    )
    # For xenon, we need stderr as well since it outputs errors there
    if cmd[0] == "xenon":
        return result.stdout + result.stderr
    return result.stdout

def count_issues(data):
    """Count total issues in a file's data."""
    count = 0
    
    # Count ruff issues
    if data.get("ruff"):
        count += len(data["ruff"])
    
    # Count mypy issues (lines with content)
    if data.get("mypy"):
        count += len([line for line in data["mypy"].split('\n') if line.strip()])
    
    # Count xenon issues (lines with content)
    if data.get("xenon"):
        count += len([line for line in data["xenon"].split('\n') if line.strip()])
    
    # Count pytest issues (if there's coverage data)
    if data.get("pytest"):
        count += 1
    
    return count

def has_issues(data):
    """Check if a file has any issues."""
    # Check ruff issues
    if data.get("ruff"):
        return True
    
    # Check mypy issues
    if data.get("mypy") and data.get("mypy").strip():
        return True
    
    # Check xenon issues
    if data.get("xenon") and data.get("xenon").strip():
        return True
    
    # Check pytest coverage issues (only if not 100% coverage)
    pytest_data = data.get("pytest", "").strip()
    if pytest_data and "100%" not in pytest_data:
        return True
    
    return False

def distribute_files(files_with_issues, num_agents):
    """Distribute files evenly among agents based on issue count."""
    if num_agents <= 0:
        return {}
    
    # Sort files by issue count (heaviest first)
    sorted_files = sorted(files_with_issues.items(), key=lambda x: x[1], reverse=True)
    
    # Initialize agent workloads
    agent_workloads = [[] for _ in range(num_agents)]
    agent_totals = [0] * num_agents
    
    # Distribute files using round-robin with weights
    for filename, issue_count in sorted_files:
        # Find agent with smallest current workload
        min_agent = min(range(num_agents), key=lambda i: agent_totals[i])
        
        # Assign file to that agent
        agent_workloads[min_agent].append(filename)
        agent_totals[min_agent] += issue_count
    
    return agent_workloads

def collect_issues():
    """Collect issues from all quality tools."""
    # 1. Kick off all tool runs in parallel
    commands = {
        "pytest": ["pytest", "--maxfail=50", "--disable-warnings", "-q", "--tb=short"],
        "ruff": ["ruff", "check", "--exit-zero", "--output-format", "json", "."],
        "mypy": ["mypy", "--pretty", "--show-error-codes", "--no-error-summary", "."],
        "xenon": ["xenon", "--max-absolute", "B", "--max-modules", "A", "--max-average", "A", "."],
    }

    outputs = {}
    with ThreadPoolExecutor(max_workers=len(commands)) as executor:
        future_to_name = {executor.submit(run, cmd): name for name, cmd in commands.items()}
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            outputs[name] = future.result()
            print(f"✅ Finished {name}")

    pytest_out = outputs["pytest"]
    mypy_out = outputs["mypy"]
    xenon_out = outputs["xenon"]

    try:
        ruff_data = json.loads(outputs["ruff"])
    except Exception:
        ruff_data = []

    # 2. Initialize per-file buckets
    files = subprocess.check_output(["git", "ls-files", "*.py"], text=True).splitlines()
    results = {f: {"file": f, "pytest": "", "ruff": [], "mypy": "", "xenon": ""} for f in files}

    # 3. Distribute pytest output
    for f in files:
        if f in pytest_out:
            results[f]["pytest"] = "\n".join(
                line for line in pytest_out.splitlines() if f in line
            )

    # 4. Distribute ruff findings
    for item in ruff_data:
        filename = item.get("filename")
        # Convert absolute path to relative path if needed
        if filename.startswith(str(ROOT) + "/"):
            filename = filename[len(str(ROOT)) + 1:]
        if filename in results:
            results[filename]["ruff"].append(item)

    # 5. Distribute mypy errors
    for f in files:
        if f in mypy_out:
            results[f]["mypy"] = "\n".join(
                line for line in mypy_out.splitlines() if f in line
            )

    # 6. Distribute xenon complexity
    for f in files:
        if f in xenon_out:
            results[f]["xenon"] = "\n".join(
                line for line in xenon_out.splitlines() if f in line
            )

    # 7. Filter and organize files
    files_with_issues = {}
    clean_files = []
    
    for f, data in results.items():
        base = f.replace("/", "_")
        
        if has_issues(data):
            # File has issues - move to found directory
            files_with_issues[base] = count_issues(data)
            with open(FOUND_DIR / f"{base}.json", "w") as out:
                json.dump(data, out, indent=2)
        else:
            # Clean file - move to clean directory
            clean_files.append(base)
            with open(CLEAN_DIR / f"{base}.json", "w") as out:
                json.dump(data, out, indent=2)
    
    return files_with_issues, clean_files

def distribute_to_agents(files_with_issues, num_agents):
    """Distribute files with issues to agents."""
    if not files_with_issues:
        print("📭 No files with issues found!")
        return
    
    print(f"📦 Found {len(files_with_issues)} files with issues")
    
    # Distribute files among agents
    agent_workloads = distribute_files(files_with_issues, num_agents)
    
    # Move files to assigned directories
    for agent_id, files in enumerate(agent_workloads, 1):
        agent_dir = ASSIGNED_DIR / f"agent_{agent_id}"
        todo_dir = agent_dir / "todo"
        done_dir = agent_dir / "done"
        
        # Create agent directories
        todo_dir.mkdir(parents=True, exist_ok=True)
        done_dir.mkdir(parents=True, exist_ok=True)
        
        agent_total_issues = 0
        for file_base in files:
            # Move file from found to agent's todo directory
            src = FOUND_DIR / f"{file_base}.json"
            dst = todo_dir / f"{file_base}.json"
            if src.exists():
                src.rename(dst)
                agent_total_issues += files_with_issues[file_base]
        
        print(f"🤖 Agent {agent_id}: {len(files)} files, {agent_total_issues} issues")

def clean_issues_directory():
    """Clean the issues directory completely."""
    if ISSUES_DIR.exists():
        print("🧹 Cleaning issues directory...")
        shutil.rmtree(ISSUES_DIR)
        print("✅ Issues directory cleaned")
    
    # Recreate the base directory
    ISSUES_DIR.mkdir(exist_ok=True)

def main():
    # Get number of agents from command line
    num_agents = 1
    if len(sys.argv) > 1:
        try:
            num_agents = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid number of agents. Using default: 1")
    
    # Clean slate - delete everything in issues directory
    clean_issues_directory()
    
    # Create all directories
    FOUND_DIR.mkdir(parents=True, exist_ok=True)
    ASSIGNED_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Collecting issues and distributing to {num_agents} agents...")
    print("=" * 60)
    
    # Collect issues
    files_with_issues, clean_files = collect_issues()
    
    print(f"📊 Collection Summary:")
    print(f"   • Total files analyzed: {len(files_with_issues) + len(clean_files)}")
    print(f"   • Files with issues: {len(files_with_issues)}")
    print(f"   • Clean files: {len(clean_files)}")
    print(f"   • Total issues: {sum(files_with_issues.values())}")
    
    if files_with_issues:
        print(f"\n📋 Distribution Summary:")
        print("-" * 40)
        distribute_to_agents(files_with_issues, num_agents)
    
    print(f"\n🎉 Setup complete!")
    print(f"   • Clean files: {CLEAN_DIR}/")
    print(f"   • Issue files: {FOUND_DIR}/")
    print(f"   • Agent assignments: {ASSIGNED_DIR}/")
    print(f"   • Each agent has: todo/ (work to do) and done/ (completed work)")

if __name__ == "__main__":
    main()
