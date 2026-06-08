from __future__ import annotations

from pathlib import Path

import pytest

from smriti_mcp import cli


class FakeServer:
    def __init__(self) -> None:
        self.runs: list[str] = []

    def run(self, transport: str) -> None:
        self.runs.append(transport)


def test_server_subcommand_runs_with_explicit_memory_root(monkeypatch, tmp_path: Path) -> None:
    created: dict[str, object] = {}
    fake_server = FakeServer()

    def fake_create_server(memory_root: Path) -> FakeServer:
        created["memory_root"] = memory_root
        return fake_server

    monkeypatch.setattr(cli, "create_server", fake_create_server)

    cli.main(["server", "--memory-root", str(tmp_path), "--transport", "stdio"])

    assert created["memory_root"] == tmp_path
    assert fake_server.runs == ["stdio"]


def test_legacy_option_only_invocation_defaults_to_server(monkeypatch, tmp_path: Path) -> None:
    created: dict[str, object] = {}
    fake_server = FakeServer()

    def fake_create_server(memory_root: Path) -> FakeServer:
        created["memory_root"] = memory_root
        return fake_server

    monkeypatch.setattr(cli, "create_server", fake_create_server)

    cli.main(["--memory-root", str(tmp_path)])

    assert created["memory_root"] == tmp_path
    assert fake_server.runs == ["stdio"]


def test_no_args_defaults_to_server(monkeypatch, tmp_path: Path) -> None:
    fake_server = FakeServer()

    monkeypatch.setenv("SMRITI_MEMORY_ROOT", str(tmp_path))
    monkeypatch.setattr(cli, "create_server", lambda memory_root: fake_server)

    cli.main([])

    assert fake_server.runs == ["stdio"]


def test_fix_frontmatter_requires_explicit_path() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["fix-frontmatter"])

    assert exc.value.code == 2


def test_rebuild_subcommand_runs_memory_rebuild(monkeypatch, tmp_path: Path) -> None:
    calls: dict[str, object] = {}

    class FakeStore:
        def __init__(self, memory_root: Path) -> None:
            calls["memory_root"] = memory_root

        def rebuild_memory(
            self,
            apply_wikilinks: bool,
            fix_frontmatter: bool,
            group_by_category: bool,
            dry_run: bool,
        ) -> dict[str, object]:
            calls["apply_wikilinks"] = apply_wikilinks
            calls["fix_frontmatter"] = fix_frontmatter
            calls["group_by_category"] = group_by_category
            calls["dry_run"] = dry_run
            return {
                "dry_run": dry_run,
                "frontmatter": {"fixed": 1, "errors": 0},
                "wikilinks": {"files_modified": 1, "links_added": 2, "links_normalized": 3},
                "index": {"indexed_notes": 4, "index_path": str(tmp_path / "index.md")},
            }

    monkeypatch.setattr(cli, "MemoryStore", FakeStore)

    cli.main(["rebuild", "--memory-root", str(tmp_path), "--dry-run"])

    assert calls == {
        "memory_root": tmp_path,
        "apply_wikilinks": True,
        "fix_frontmatter": True,
        "group_by_category": True,
        "dry_run": True,
    }
