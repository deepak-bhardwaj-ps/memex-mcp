# Quick Start Guide

Get Memex MCP running with your favorite AI agent in minutes.

## Installation

```bash
pip install memex-mcp
```

## Claude Desktop

1. **Install Memex MCP**
   ```bash
   pip install memex-mcp
   ```

2. **Configure Claude Desktop**
   
   Edit `~/.config/claude_desktop_config.json` (macOS/Linux) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

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

3. **Restart Claude Desktop**
   
   Close and reopen Claude Desktop. You'll see "Memex" in the tools list.

4. **Start Using**
   
   In Claude, say something like:
   > "Create a memory about my favorite Python libraries"
   > "Search for memories about Python"
   > "Show me all my project notes"

## Cline (VSCode)

1. **Install Memex MCP**
   ```bash
   pip install memex-mcp
   ```

2. **Configure in .clinerules or cline config**
   
   ```json
   {
     "mcpServers": {
       "memex": {
         "type": "stdio",
         "command": "memex-mcp",
         "args": ["server", "--memory-root", "/path/to/memories"]
       }
     }
   }
   ```

3. **Use in Cline**
   
   Ask Cline to use memory tools:
   > "Remember this architecture decision: ..."

## Cursor

1. **Install Memex MCP**
   ```bash
   pip install memex-mcp
   ```

2. **Configure in Cursor settings**
   
   In Cursor's settings, add to MCP servers:

   ```json
   {
     "memex": {
       "command": "memex-mcp",
      "args": ["server", "--memory-root", "~/.memex/memory"]
     }
   }
   ```

3. **Start using**
   
   Refer to memories in your prompts or let Cursor use the tools automatically.

## Generic MCP Client

For any MCP-compatible client, configure:

```json
{
  "type": "stdio",
  "command": "memex-mcp",
  "args": ["server", "--memory-root", "~/.memex/memory"]
}
```

The server will start and expose these tools:
- `create_memory`
- `get_memory`
- `append_memory`
- `update_memory`
- `delete_memory`
- `archive_memory`
- `search_memory`
- `list_memories`
- `build_memory_index`
- `rebuild_memory`
- `load_memory_index`

## Memory Directory Structure

Memories are stored as markdown files:

```
~/.memex/memory/
├── project/
│   ├── Architecture Decisions.md
│   └── Performance Tuning.md
├── research/
│   ├── LLM Benchmarks.md
│   └── ML Papers.md
├── decisions/
│   ├── Use Postgres.md
│   └── Async Patterns.md
└── index.md (auto-generated)
```

## Common Workflows

### Create a lasting decision record

> "Create a memory in the decisions category about why we chose PostgreSQL over MySQL"

### Build a research archive

> "Create a memory about the latest LLM benchmarks I found"
> "Search my research memories for information about transformers"

### Maintain project notes

> "Add to my project notes about the API refactoring we discussed"
> "Show me all archived project memories"

### Rebuild and repair memory

> "Rebuild my memory: fix frontmatter, apply wikilinks, and refresh the index"
> "Build my memory index so I can see all my memories at a glance"
> "Load my memory index"

## Troubleshooting

### Command not found: `memex-mcp`

Ensure the package is installed:
```bash
pip install --upgrade memex-mcp
```

Check installation:
```bash
which memex-mcp
memex-mcp --help
```

### Memories not showing up in searches

1. Verify the memory root directory exists:
   ```bash
   ls -la ~/.memex/memory/
   ```

2. Check that memories were created:
   ```bash
   find ~/.memex/memory/ -name "*.md" | head
   ```

3. Rebuild the index:
   > "Build my memory index"

### Permission denied errors

Ensure the memory directory is writable:
```bash
chmod -R u+w ~/.memex/memory/
```

## Tips & Tricks

- **Use consistent categories** for better organization (`project`, `research`, `decisions`, `notes`)
- **Add tags** to memories for easier filtering and searching
- **Use wikilinks** like `[[Related Memory]]` to connect related thoughts by title
- **Review your index regularly** with `load_memory_index` to keep knowledge fresh
- **Archive old memories** instead of deleting to maintain history

## Getting Help

- Check [README.md](README.md) for full documentation
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for development setup
- Open an issue on GitHub for bugs or feature requests
