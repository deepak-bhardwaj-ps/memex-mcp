# Frontmatter Health Check & Fix Tool

## Overview

The `fix-frontmatter` tool scans markdown memory files in a vault or memory root and ensures they have proper YAML frontmatter with required metadata fields. This is essential for indexing and discovery to work correctly.

## Why This Matters

Memory files in the Memex system require standardized frontmatter metadata to be properly indexed and discovered:

- **title** (required): Human-readable name of the memory
- **category** (required): Broad namespace for grouping (e.g., 'signal', 'content-ideas', 'project')
- **status** (default: 'active'): Lifecycle state ('active' or 'archived')
- **aliases** (optional): Alternative names for discovery
- **tags** (optional): Specific labels for filtering
- **short_description** (optional): One-sentence summary
- **author** (optional): Who created or owns this memory

## Quick Start

### Scan for Issues (Dry-run)

```bash
memxp-mcp fix-frontmatter /path/to/memory-root --dry-run
```

This shows what issues exist without making any changes.

### Fix All Issues

```bash
memxp-mcp fix-frontmatter /path/to/memory-root
```

This scans all files and:
- Adds missing `title` (extracted from first heading or filename)
- Adds missing `category` (inferred from directory structure)
- Ensures `status` defaults to 'active'
- Converts `aliases` and `tags` to proper lists
- Preserves all existing metadata

## What Gets Fixed

The tool intelligently fixes missing metadata:

### Title Resolution
1. **From first heading** in the document (if present)
2. **From filename** (normalized: removes dates, UUIDs, underscores, capitalizes words)
3. **From directory type** (e.g., "Signal" for files in `kb/signals/`)

### Category Resolution
1. **From `type` field** in existing frontmatter (if present)
2. **From directory structure** (e.g., `kb/signals/` → "signal", `kb/content-ideas/` → "content-ideas")
3. **From parent directory name** as fallback

### Other Fields
- `status`: Defaults to 'active'
- `aliases`: Always initialized as empty list
- `tags`: Always initialized as empty list
- `short_description`: Set to None if missing

## Examples

### Before: File with No Frontmatter
```markdown
# Content Drafts - 2026-06-05

Source: `ideas/2026-06-05.md`

Note: Idea #1 was already picked up...
```

### After: Fixed with Auto-Generated Frontmatter
```markdown
---
title: Content Drafts - 2026-06-05
category: content drafts
status: active
aliases: []
tags: []
short_description: null
---

# Content Drafts - 2026-06-05

Source: `ideas/2026-06-05.md`

Note: Idea #1 was already picked up...
```

### Before: File with Partial Frontmatter
```markdown
---
type: signal
date: 2026-06-05
source_name: Hacker News
url: https://example.com
---

# 2026-06-05 - ESP32-S31
```

### After: Frontmatter Enhanced
```markdown
---
type: signal
date: 2026-06-05
source_name: Hacker News
url: https://example.com
title: 2026-06-05 - ESP32-S31
category: signal
status: active
aliases: []
tags: []
short_description: null
---

# 2026-06-05 - ESP32-S31
```

## Command-Line Options

```
usage: memxp-mcp fix-frontmatter [-h] [--dry-run] vault_path

positional arguments:
  vault_path      Path to the markdown vault or memory root to scan.

optional arguments:
  -h, --help      Show this help message and exit
  --dry-run       Only report issues without fixing them
```

## Integration with kb-lint

The `kb-lint` skill can be run after fixing frontmatter to identify any remaining orphan pages or structural issues:

```bash
# Fix frontmatter first
memxp-mcp fix-frontmatter /path/to/memory-root

# Then check for other health issues
copilot /kb-lint
```

## FAQ

**Q: Will the tool overwrite my existing metadata?**
A: No. The tool only adds missing fields. All existing metadata is preserved.

**Q: What if I have custom frontmatter fields?**
A: Custom fields are preserved. The tool only adds the standard Memex fields.

**Q: Can I run this multiple times?**
A: Yes. Running it multiple times is safe. It will only add missing fields on subsequent runs.

**Q: How does it extract titles from filenames?**
A: It removes date prefixes (YYYY-MM-DD), UUIDs (like -325c5707), replaces dashes/underscores with spaces, and capitalizes each word.

**Q: What if a file has no heading and a cryptic filename?**
A: The tool uses the directory name as a fallback. For example, a file in `kb/signals/` gets category "signal".

## Troubleshooting

**All files showing as errors:**
- Check file permissions
- Ensure the vault path is correct
- Run with `--dry-run` first to see detailed error messages

**Some titles are not extracted correctly:**
- The tool looks for the first `# ` heading in the document
- If none exists, it extracts from the filename
- You can manually edit the title in the frontmatter

**Category assignment seems wrong:**
- Check the file's directory structure
- Categories are inferred from directory names or the `type` field
- You can manually adjust the category in the frontmatter

## Technical Details

- Written in: Python
- Dependencies: `pyyaml` (already in memex_mcp)
- Processing: Single-pass, atomic file writes
- Safety: Preserves all existing metadata

## See Also

- [Memex Knowledge Base Patterns](../QUICKSTART.md)
- [kb-lint Health Check](./kb-lint.md)
- [Memory File Format](./MEMORY_FORMAT.md)
