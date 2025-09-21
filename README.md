# ALGOViz 🚀

A modular framework for generating narrated algorithm visualization videos.

## Overview

ALGOViz transforms algorithm education through high-quality, narrated, and visually synchronized videos that scale across many algorithms with minimal developer friction.

## Installation

```bash
# Install using uv (recommended)
uv sync

# Or install in development mode
uv pip install -e .
```

## Quick Start

```bash
# List available algorithms
agloviz list-algorithms

# Render a visualization (coming in Phase 1)
agloviz render bfs --scenario demo.yaml

# Preview a visualization (coming in Phase 1)
agloviz preview bfs --frames 120
```

## 📚 Planning Documents

**Current Version:** v2.0 (Widget Architecture Redesign)
- **Location:** `planning/v2/` 
- **Status:** Current architecture documents
- **Key Changes:** Multi-level widget hierarchy, scene configuration system

**Previous Version:** v1.0 (Original Architecture)
- **Location:** `planning/v1/`
- **Status:** Archived (contains BFS-specific pollution)
- **Reference:** Historical design decisions and evolution

See `planning/v2/README_DOCS.md` for complete documentation index.

## Development

This project is currently in Phase 0 (Foundation & Scaffolding). See [Implementation_Plan.md](Implementation_Plan.md) for the complete roadmap.

## License

MIT License - see [LICENSE](LICENSE) for details.
