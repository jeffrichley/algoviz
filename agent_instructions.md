# AI Agent Instructions

## Your Mission
You are an AI coding agent assigned to fix quality issues in Python files. Follow these steps exactly:

## 1. Check Your Assignment
- Look in `issues/assigned/agent_X/todo/` directory for JSON files
- Each JSON file contains issues for ONE specific Python file
- You are assigned to work on ONLY the files in your todo directory

## 2. Process Each Assignment
For each JSON file in your todo directory:

### A. Read the Issues
- Open the JSON file to see what needs fixing
- Look for: `ruff` (linting), `mypy` (type checking), `xenon` (complexity)
- **DO NOT** run `ruff --fix` globally - only fix the specific issues listed
- **DO NOT** run global formatting commands - only fix the specific file mentioned

### B. Fix the Issues
- Navigate to the actual Python file mentioned in the JSON
- Fix ONLY the specific issues listed:
  - **Ruff**: Fix linting errors (imports, formatting, style)
  - **MyPy**: Fix type annotation issues
  - **Xenon**: Reduce complexity in the specific function mentioned
- Make targeted, surgical fixes - don't reformat the entire codebase
- **Note**: Test files can also have ruff/mypy issues that need fixing

### C. Verify Your Work
Run these commands to verify your fixes:
```bash
# Check if you fixed the specific issues
uv run ruff check [filename]
uv run mypy [filename] 
uv run xenon [filename]

# Run tests to make sure you didn't break anything
uv run pytest tests/ -x
```

### D. Complete the Task
- If all issues are fixed AND tests pass: move the JSON file to `issues/assigned/agent_X/done/`
- If issues remain OR tests fail: fix the problems and repeat step C

## 3. Move to Next Assignment
- After completing one file, look for the next JSON file in your todo directory
- Repeat the process until your todo directory is empty

## Critical Rules
- **ONLY** work on files assigned to you in your todo directory
- **NEVER** run global formatting commands like `ruff --fix` on the entire codebase
- **ALWAYS** run tests after making changes
- **ONLY** modify the specific file mentioned in the JSON - whether it's a source file or test file
- **ALWAYS** move completed JSON files to your done directory

## Example Workflow
1. Check `issues/assigned/agent_5/todo/src_example.py.json`
2. Read the issues (e.g., "ruff: unused import", "xenon: function too complex")
3. Fix `src/example.py` to address those specific issues
4. Run `uv run ruff check src/example.py` - should show no errors
5. Run `uv run pytest tests/ -x` - should pass
6. Move `src_example.py.json` to `issues/assigned/agent_5/done/`
7. Look for next file in todo directory

Remember: You are fixing specific, targeted issues - not doing bulk code formatting!
