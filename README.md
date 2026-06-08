# Memex MCP

> A portable memory server for AI agents, built for the Model Context Protocol (MCP).

[![PyPI version](https://img.shields.io/pypi/v/memex-mcp.svg)](https://pypi.org/project/memex-mcp/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()

Memex stores durable memories as plain markdown files with YAML frontmatter. This keeps your data readable, git-friendly, and easy to inspect outside any single agent runtime.

## Features

- **Framework agnostic**: Works with any MCP-compatible agent (Claude, OpenAI, local models, etc.)
- **Durable & portable**: All memories stored as plain markdown files—no database required
- **Git-friendly**: Version control your memories alongside your code
- **Search & filter**: Full-text search, filtering by tags, categories, and status
- **Relationship tracking**: Use `[[wikilinks]]` to connect related memories
- **Memory index**: Auto-generate markdown indexes of your entire memory store
- **Archive & organize**: Hierarchical organization with categories and status tracking

## Installation

### From PyPI

```bash
pip install memex-mcp
```

### From source

```bash
git clone https://github.com/deepak-bhardwaj-ps/memex-mcp.git
cd memex-mcp
pip install -e .
```

## Quick Start

### 1. Run the server locally

```bash
memex-mcp server --memory-root ~/.memex/memory
```

By default, Memex uses `~/.memex/memory`. You can override it with:

```bash
export MEMEX_MEMORY_ROOT="$HOME/.memex/memory"
memex-mcp server
```

### 2. Configure in your MCP client

**Claude Desktop** (`~/.config/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "memex": {
      "type": "stdio",
      "command": "memex-mcp",
      "args": ["server", "--memory-root", "~/.memex/memory"]
    }
  }
}
```

Then restart Claude Desktop and Memex will be available as a tool.

## Available Tools

### Core Operations

| Tool | Description |
|------|-------------|
| `create_memory` | Create a new durable markdown memory with metadata |
| `get_memory` | Retrieve a memory by ID and return its full content |
| `append_memory` | Add content to the end of an existing memory |
| `update_memory` | Patch metadata or replace memory content |
| `delete_memory` | Permanently remove a memory |

### Search & Browse

| Tool | Description |
|------|-------------|
| `search_memory` | Full-text search across title, tags, categories, and body. Returns ranked results |
| `list_memories` | Browse memory metadata without loading full content. Filter by status, category, tags |

### Organization

| Tool | Description |
|------|-------------|
| `archive_memory` | Mark a memory as archived (soft delete) |
| `build_memory_index` | Generate a markdown index of all memories for easy browsing |
| `rebuild_memory` | Fix frontmatter, apply/normalize wikilinks from titles and aliases, and rebuild indexes |
| `load_memory_index` | Load the generated index as markdown |

## Memory Format

Each memory is stored as a markdown file with YAML frontmatter:

```markdown
---
id: project/Example Architecture Decision
title: Example Architecture Decision
category: project
tags:
  - architecture
  - decision
status: active
short_description: Decided to use async/await pattern
created_at: "2026-06-05T10:30:00+10:00"
updated_at: "2026-06-05T10:30:00+10:00"
---

## Background

We needed to handle concurrent requests efficiently.

## Decision

Use async/await with asyncio for I/O-bound operations.

## Consequences

- Improved throughput for concurrent operations
- Need to manage event loop carefully in multi-threaded contexts

See also: [[Async Migration]], [[Performance Metrics]]
```

### Metadata Fields

- **id**: Unique identifier (auto-generated from category + title, or custom)
- **title**: Human-readable title
- **category**: Organizational category (becomes directory in file structure)
- **tags**: Array of searchable tags
- **status**: `active`, `archived`, or custom status
- **short_description**: Brief summary (used in indexes)
- **created_at**: ISO 8601 timestamp
- **updated_at**: ISO 8601 timestamp

## File Structure

```
~/.memex/memory/
├── project/
│   ├── Example Architecture Decision.md
│   ├── Async Migration.md
│   └── Performance Metrics.md
├── research/
│   └── LLM Benchmarks.md
├── decisions/
│   └── Use Postgres.md
└── index.md
```

Memex keeps default filenames aligned with memory titles so Obsidian-style wikilinks like
`[[API Rate Limiting Strategy]]` resolve to `API Rate Limiting Strategy.md`.

When you run `rebuild_memory`, Memex can automatically add missing wikilinks and normalize
alias links. It matches longer titles and aliases first and only links whole phrases, so
`Durable Memory` is preferred over `durable`, and `able` is not linked inside `durable`.

## Usage Examples

### Create a memory

```python
from memex_mcp.store import MemoryStore

store = MemoryStore("~/.memex/memory")

result = store.create_memory(
    {
        "title": "API Rate Limiting Strategy",
        "category": "decisions",
        "tags": ["api", "performance"],
        "short_description": "Decided on sliding window rate limiting",
    },
    content="We chose sliding window over token bucket because...",
)

# Returns: {"id": "decisions/API Rate Limiting Strategy", ...}
```

### Search memories

```python
results = store.search_memory(
    query="rate limiting",
    include_content=False,  # Just metadata
)

for result in results:
    print(f"{result['id']}: {result['title']}")
```

### List memories with filters

```python
active_decisions = store.list_memories(
    status="active",
    category="decisions",
)

for memory in active_decisions:
    print(f"{memory['title']} ({memory['status']})")
```

### Rebuild and repair memories

```python
result = store.rebuild_memory(
    fix_frontmatter=True,
    apply_wikilinks=True,
    group_by_category=True,
)

print(result["wikilinks"]["links_added"])
```

## Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run integration tests only
pytest tests/test_memex_mcp_integration.py -v
```

All tests pass, including full MCP stdio round-trip integration tests.

## Architecture

- **MemoryStore**: Core storage engine with markdown file I/O
- **Server**: MCP server exposing tools to agents
- **CLI**: Command-line interface for running the stdio server
- **Frontmatter**: YAML metadata parsing and generation

The package has **zero external database dependencies** and works with Python 3.10+.

## Roadmap

- [ ] Web UI for browsing memories
- [ ] Multi-user support with authentication
- [ ] Memory graph visualization
- [ ] Sync to cloud storage (S3, GCS)
- [ ] Memory embeddings for semantic search

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest tests/ -v`)
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Created by Deepak Bhardwaj.

## See Also

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Claude MCP Documentation](https://claude.ai/resources/docs)
- [Memex concept](https://en.wikipedia.org/wiki/Memex)
