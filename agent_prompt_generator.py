#!/usr/bin/env python3
"""
Generate Cursor CLI prompts from issue JSON files
"""
import json
import sys
from pathlib import Path

def format_issues(data):
    """Format issues for the prompt template."""
    
    # Format pytest (coverage data)
    pytest_text = data.get("pytest", "").strip()
    if not pytest_text:
        pytest_text = "No test coverage issues found"
    
    # Format ruff (array of issues)
    ruff_issues = data.get("ruff", [])
    if ruff_issues:
        ruff_text = "\n".join([
            f"- {issue['code']}: {issue['message']} (line {issue['location']['row']}, col {issue['location']['column']})"
            for issue in ruff_issues[:10]  # Limit to first 10 issues
        ])
        if len(ruff_issues) > 10:
            ruff_text += f"\n... and {len(ruff_issues) - 10} more issues"
    else:
        ruff_text = "No ruff issues found"
    
    # Format mypy (string of errors)
    mypy_text = data.get("mypy", "").strip()
    if not mypy_text:
        mypy_text = "No mypy issues found"
    else:
        # Clean up mypy output
        mypy_lines = [line.strip() for line in mypy_text.split('\n') if line.strip()]
        mypy_text = "\n".join(mypy_lines[:5])  # Limit to first 5 errors
        if len(mypy_lines) > 5:
            mypy_text += f"\n... and {len(mypy_lines) - 5} more errors"
    
    # Format xenon (complexity data)
    xenon_text = data.get("xenon", "").strip()
    if not xenon_text:
        xenon_text = "No complexity issues found"
    else:
        # Clean up xenon output
        xenon_lines = [line.strip() for line in xenon_text.split('\n') if line.strip()]
        xenon_text = "\n".join(xenon_lines[:5])  # Limit to first 5 issues
        if len(xenon_lines) > 5:
            xenon_text += f"\n... and {len(xenon_lines) - 5} more issues"
    
    return {
        "pytest": pytest_text,
        "ruff": ruff_text,
        "mypy": mypy_text,
        "xenon": xenon_text
    }

def generate_prompt(json_file_path):
    """Generate a Cursor CLI prompt from a JSON file."""
    
    # Load the JSON data
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # Get the target file path
    target_file = data.get("file", "unknown")
    
    # Format the issues
    issues = format_issues(data)
    
    # Load the template
    template_path = Path(__file__).parent / "agent_template.md"
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Replace placeholders
    prompt = template.replace("{{file}}", target_file)
    prompt = prompt.replace("{{pytest}}", issues["pytest"])
    prompt = prompt.replace("{{ruff}}", issues["ruff"])
    prompt = prompt.replace("{{mypy}}", issues["mypy"])
    prompt = prompt.replace("{{xenon}}", issues["xenon"])
    
    return prompt

def main():
    if len(sys.argv) != 2:
        print("Usage: python agent_prompt_generator.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"Error: File {json_file} not found")
        sys.exit(1)
    
    try:
        prompt = generate_prompt(json_file)
        print(prompt)
    except Exception as e:
        print(f"Error generating prompt: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
