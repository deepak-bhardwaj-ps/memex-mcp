from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_memex_stdio_server_round_trip(tmp_path: Path) -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "memex_mcp.cli",
            "server",
            "--memory-root",
            str(tmp_path),
        ],
    )

    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            assert {
                "create_memory",
                "get_memory",
                "search_memory",
                "build_memory_index",
            }.issubset(tool_names)

            created = await session.call_tool(
                "create_memory",
                arguments={
                    "meta": {
                        "title": "Integration Memory",
                        "category": "tests",
                        "tags": ["integration"],
                        "short_description": "Round-trip MCP test memory.",
                    },
                    "content": "This durable note was written through the MCP stdio protocol.",
                },
            )
            created_payload = _json_payload(created)
            assert created_payload["id"] == "tests/Integration Memory"

            searched = await session.call_tool(
                "search_memory",
                arguments={"query": "stdio protocol", "include_content": False},
            )
            search_payload = _json_payload(searched)
            assert search_payload["count"] == 1
            assert search_payload["results"][0]["id"] == "tests/Integration Memory"
            assert "content" not in search_payload["results"][0]

            loaded = await session.call_tool(
                "get_memory",
                arguments={"id": "tests/Integration Memory"},
            )
            markdown = _text_payload(loaded)
            assert "title: Integration Memory" in markdown
            assert "MCP stdio protocol" in markdown

            indexed = await session.call_tool("build_memory_index", arguments={})
            assert _json_payload(indexed)["indexed_notes"] == 1

    assert (tmp_path / "tests" / "Integration Memory.md").exists()
    assert (tmp_path / "index.md").exists()


def _text_payload(result) -> str:
    return "".join(block.text for block in result.content if hasattr(block, "text"))


def _json_payload(result):
    return json.loads(_text_payload(result))
