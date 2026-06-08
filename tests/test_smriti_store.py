from pathlib import Path

import pytest

from smriti_mcp.store import MemoryStore


def test_create_memory_uses_title_filename_and_markdown_frontmatter(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)

    result = store.create_memory(
        {
            "title": "Agent Runtime Decision",
            "category": "Project Notes",
            "tags": ["runtime"],
        },
        "Use durable memory for decisions.",
    )

    assert result["id"] == "Project Notes/Agent Runtime Decision"
    assert (tmp_path / "Project Notes" / "Agent Runtime Decision.md").exists()
    markdown = store.get_memory(result["id"])
    assert "title: Agent Runtime Decision" in markdown
    assert "Use durable memory for decisions." in markdown


def test_create_memory_blocks_path_traversal(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)

    with pytest.raises(ValueError):
        store.create_memory(
            {"title": "Secret", "category": "notes"},
            "Body",
            id="../../secret",
        )


def test_search_memory_can_omit_full_content(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)
    store.create_memory(
        {"title": "Memory Search", "category": "notes", "tags": ["search"]},
        "Need relevance scoring for durable notes.",
    )

    results = store.search_memory("relevance", include_content=False)

    assert results[0]["id"] == "notes/Memory Search"
    assert "content" not in results[0]
    assert results[0]["snippets"]


def test_archive_and_delete_memory(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)
    created = store.create_memory({"title": "Old Note", "category": "notes"}, "Body")

    store.archive_memory(created["id"])
    archived = store.list_memories(status="archived")
    assert [item["id"] for item in archived] == [created["id"]]

    store.delete_memory(created["id"])
    assert store.list_memories() == []


def test_build_and_load_memory_index(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)
    store.create_memory(
        {"title": "Alpha", "category": "notes", "short_description": "first"},
        "Body",
    )

    result = store.build_memory_index()

    assert result["indexed_notes"] == 1
    assert "# Memory Index" in store.load_memory_index()
    assert "[[Alpha]] - first" in store.load_memory_index()


def test_wikilinks_resolve_to_title_preserving_filenames(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)
    target = store.create_memory(
        {"title": "Content Intelligence", "category": "notes"},
        "Reusable content strategy memory.",
    )
    source = store.create_memory(
        {"title": "Agent Writing Workflow", "category": "notes"},
        "Use [[Content Intelligence]] when drafting posts.",
    )

    index = store._build_machine_index(include_content=False)

    assert target["id"] == "notes/Content Intelligence"
    assert (tmp_path / "notes" / "Content Intelligence.md").exists()
    assert index["links"][source["id"]] == [target["id"]]
    assert index["backlinks"][target["id"]] == [source["id"]]


def test_apply_wikilinks_uses_longest_match_and_word_boundaries(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)
    store.create_memory(
        {"title": "Durable Memory", "category": "notes", "aliases": ["durable"]},
        "Target.",
    )
    note = store.create_memory(
        {"title": "Writing Note", "category": "notes"},
        "Durable memory matters. Endurable systems are different. Able alone is not the same.",
    )

    stats = store.apply_wikilinks()
    markdown = store.get_memory(note["id"])

    assert stats["links_added"] == 1
    assert "[[Durable Memory|Durable memory]] matters." in markdown
    assert "Endurable systems" in markdown
    assert "Able alone" in markdown


def test_apply_wikilinks_normalizes_aliases_and_skips_protected_text(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)
    store.create_memory(
        {"title": "Content Intelligence", "category": "notes", "aliases": ["CI"]},
        "Target.",
    )
    note = store.create_memory(
        {"title": "Protected Note", "category": "notes"},
        (
            "Use [[CI]] in prose.\n"
            "Keep [CI](https://example.com) as a markdown link.\n"
            "Keep `CI` in code.\n"
        ),
    )

    stats = store.apply_wikilinks()
    markdown = store.get_memory(note["id"])

    assert stats["links_normalized"] == 1
    assert stats["links_added"] == 0
    assert "[[Content Intelligence|CI]] in prose" in markdown
    assert "[CI](https://example.com)" in markdown
    assert "`CI`" in markdown


def test_rebuild_memory_fixes_frontmatter_applies_wikilinks_and_indexes(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)
    store.create_memory(
        {"title": "Content Intelligence", "category": "notes"},
        "Target.",
    )
    raw = tmp_path / "notes" / "Needs Frontmatter.md"
    raw.write_text("Talk about Content Intelligence here.\n", encoding="utf-8")

    result = store.rebuild_memory()
    markdown = raw.read_text(encoding="utf-8")

    assert result["frontmatter"]["fixed"] == 1
    assert result["wikilinks"]["links_added"] == 1
    assert result["index"]["indexed_notes"] == 2
    assert "title: Needs Frontmatter" in markdown
    assert "[[Content Intelligence]] here" in markdown


def test_search_and_index_preserve_existing_obsidian_paths(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)
    clipping = tmp_path / "Clippings" / "The biggest 𝗔𝗴𝗲𝗻𝘁𝗶𝗰 AI decision isn't model selection.md"
    clipping.parent.mkdir()
    clipping.write_text(
        """---
title: "The biggest 𝗔𝗴𝗲𝗻𝘁𝗶𝗰 AI decision isn't model selection"
tags:
  - clippings
---

Agentic AI decisions depend on access, memory, and governance.
""",
        encoding="utf-8",
    )

    results = store.search_memory("governance", include_content=False)
    indexed = store.build_memory_index()
    loaded = store.load_memory_index()

    assert results[0]["id"] == "Clippings/The biggest 𝗔𝗴𝗲𝗻𝘁𝗶𝗰 AI decision isn't model selection"
    assert indexed["indexed_notes"] == 1
    assert "[[The biggest 𝗔𝗴𝗲𝗻𝘁𝗶𝗰 AI decision isn't model selection]]" in loaded
