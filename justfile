# ALGOViz development commands
# Uses uv for Python environment management

# Default recipe - show available commands
default:
    @just --list

# Install dependencies
install:
    uv sync

# Run tests using pytest
test:
    uv run pytest

# Run tests with coverage
test-cov:
    uv run pytest --cov=src/agloviz --cov-report=term-missing

# Run linting
lint:
    uv run ruff check src/ tests/

# Format code
format:
    uv run ruff format src/ tests/

# Fix linting issues
fix:
    uv run ruff check --fix src/ tests/
    uv run ruff format src/ tests/

# Type checking
typecheck:
    uv run mypy src/

# Run all quality checks
check: lint typecheck test

# Clean up build artifacts
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    rm -rf .pytest_cache/
    rm -rf .coverage
    rm -rf htmlcov/

# Build package
build:
    uv build

# Install package in development mode
install-dev:
    uv pip install -e .

# Run quality tools (pytest, ruff, mypy, xenon)
quality:
    uv run pytest --tb=short
    uv run ruff check src/ tests/
    uv run mypy src/
    uv run xenon src/ --max-absolute B --max-modules A --max-average A

# Collect issues and distribute to agents
distribute N:
    uv run python collect_issues.py {{N}}

# Generate prompt for a specific JSON file
generate-prompt JSON_FILE:
    uv run python agent_prompt_generator.py {{JSON_FILE}}

# Run a specific agent
run-agent AGENT_ID:
    uv run python agent_runner.py {{AGENT_ID}}

# Run all agents (manual parallel execution)
run-all-agents:
    @echo "Run these commands in parallel in separate terminals:"
    @echo "just run-agent 1"
    @echo "just run-agent 2"
    @echo "just run-agent 3"
    @echo "etc..."

# Test cursor-agent with a specific file
test-cursor FILE:
    cursor-agent --print "Fix all quality issues in this file" {{FILE}}
