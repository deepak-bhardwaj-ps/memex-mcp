from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from smriti_mcp.server import create_server
from smriti_mcp.store import DEFAULT_MEMORY_ROOT, MemoryStore
from smriti_mcp.fix_frontmatter import scan_vault, print_summary


def cmd_server(args) -> None:
    """Run the MCP server."""
    server = create_server(Path(args.memory_root).expanduser())
    server.run(transport=args.transport)


def cmd_fix_frontmatter(args) -> None:
    """Fix frontmatter in memory files."""
    vault_path = Path(args.vault_path).expanduser()
    stats = scan_vault(vault_path, dry_run=args.dry_run)
    print_summary(stats)

    # Exit with non-zero if there were errors
    if stats.get("errors", 0) > 0:
        raise SystemExit(1)


def cmd_rebuild(args) -> None:
    """Repair and rebuild memory files and indexes."""
    store = MemoryStore(Path(args.memory_root).expanduser())
    result = store.rebuild_memory(
        apply_wikilinks=not args.skip_wikilinks,
        fix_frontmatter=not args.skip_frontmatter,
        group_by_category=not args.no_group_by_category,
        dry_run=args.dry_run,
    )

    frontmatter = result.get("frontmatter") or {}
    wikilinks = result.get("wikilinks") or {}
    index = result.get("index") or {}

    print("\nMemory rebuild summary")
    print(f"{'=' * 60}")
    print(f"Dry run:             {result['dry_run']}")
    if frontmatter:
        print(f"Frontmatter fixed:   {frontmatter.get('fixed', 0)}")
        print(f"Frontmatter errors:  {frontmatter.get('errors', 0)}")
    if wikilinks:
        print(f"Wikilink files:      {wikilinks.get('files_modified', 0)}")
        print(f"Wikilinks added:     {wikilinks.get('links_added', 0)}")
        print(f"Wikilinks fixed:     {wikilinks.get('links_normalized', 0)}")
    if index:
        print(f"Indexed notes:       {index.get('indexed_notes', 0)}")
        print(f"Index path:          {index.get('index_path', '')}")

    if frontmatter.get("errors", 0) > 0:
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smriti-mcp",
        description="Smriti markdown memory tools and MCP server.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    server_parser = subparsers.add_parser("server", help="Run the MCP server")
    server_parser.add_argument(
        "--memory-root",
        default=os.environ.get("SMRITI_MEMORY_ROOT", str(DEFAULT_MEMORY_ROOT)),
        help="Directory where markdown memory notes are stored.",
    )
    server_parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport to use.",
    )
    server_parser.set_defaults(func=cmd_server)

    fix_parser = subparsers.add_parser(
        "fix-frontmatter",
        help="Scan and fix frontmatter in memory files",
    )
    fix_parser.add_argument(
        "vault_path",
        help="Path to the markdown vault or memory root to scan.",
    )
    fix_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report issues without fixing",
    )
    fix_parser.set_defaults(func=cmd_fix_frontmatter)

    rebuild_parser = subparsers.add_parser(
        "rebuild",
        help="Fix frontmatter, apply wikilinks, and rebuild memory indexes",
    )
    rebuild_parser.add_argument(
        "--memory-root",
        default=os.environ.get("SMRITI_MEMORY_ROOT", str(DEFAULT_MEMORY_ROOT)),
        help="Directory where markdown memory notes are stored.",
    )
    rebuild_parser.add_argument(
        "--skip-wikilinks",
        action="store_true",
        help="Do not add or normalize wikilinks.",
    )
    rebuild_parser.add_argument(
        "--skip-frontmatter",
        action="store_true",
        help="Do not repair frontmatter before rebuilding.",
    )
    rebuild_parser.add_argument(
        "--no-group-by-category",
        action="store_true",
        help="Do not group generated index.md entries under category headings.",
    )
    rebuild_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report proposed fixes without writing memory files or indexes.",
    )
    rebuild_parser.set_defaults(func=cmd_rebuild)

    parser.set_defaults(
        func=cmd_server,
        memory_root=os.environ.get("SMRITI_MEMORY_ROOT", str(DEFAULT_MEMORY_ROOT)),
        transport="stdio",
    )
    return parser


def normalize_argv(argv: Sequence[str]) -> list[str]:
    """Default option-only invocations to the server subcommand."""
    if not argv or argv[0].startswith("-"):
        return ["server", *argv]
    return list(argv)


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    raw_args = sys.argv[1:] if argv is None else argv
    args = parser.parse_args(normalize_argv(raw_args))
    args.func(args)


if __name__ == "__main__":
    main()
