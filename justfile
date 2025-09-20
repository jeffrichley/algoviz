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
