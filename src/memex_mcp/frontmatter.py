from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


class FrontmatterError(Exception):
    pass


class FrontmatterParseError(FrontmatterError):
    pass


def parse_markdown(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    raw_meta, body = match.groups()
    try:
        meta = yaml.safe_load(raw_meta) or {}
    except yaml.YAMLError as exc:
        raise FrontmatterParseError(str(exc)) from exc

    if not isinstance(meta, dict):
        raise FrontmatterParseError("Frontmatter must be a mapping.")
    return meta, body


def build_markdown(meta: dict[str, Any], body: str) -> str:
    if not meta:
        return body.lstrip()
    raw_meta = yaml.safe_dump(
        meta,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).strip()
    return f"---\n{raw_meta}\n---\n\n{body.lstrip()}"


@dataclass
class MemoryDocument:
    meta: dict[str, Any] = field(default_factory=dict)
    body: str = ""
    path: Path | None = None

    @classmethod
    def load(cls, path: str | Path) -> "MemoryDocument":
        resolved = Path(path)
        meta, body = parse_markdown(resolved.read_text(encoding="utf-8"))
        return cls(meta=meta, body=body, path=resolved)

    def to_markdown(self) -> str:
        return build_markdown(self.meta, self.body)

    def save(self, path: str | Path | None = None) -> None:
        target = Path(path) if path is not None else self.path
        if target is None:
            raise ValueError("No path supplied for memory document save.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.to_markdown(), encoding="utf-8")
        self.path = target
