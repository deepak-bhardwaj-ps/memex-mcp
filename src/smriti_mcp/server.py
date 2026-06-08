from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from smriti_mcp.store import DEFAULT_MEMORY_ROOT, MemoryStore


class MemoryMetaInput(BaseModel):
    title: str = Field(
        description="Human-readable memory title, for example 'Preferred deployment workflow'."
    )
    category: str = Field(
        description="Broad namespace used to group memories, for example 'project', 'user', or 'architecture'."
    )
    short_description: str | None = Field(
        default=None,
        description="One-sentence summary shown in search results and generated indexes.",
    )
    aliases: list[str] = Field(
        default_factory=list,
        description="Alternative names or phrases that should resolve to this memory.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Specific labels for filtering and retrieval, such as 'decision' or 'preference'.",
    )
    author: str | None = Field(
        default=None,
        description="Optional author or agent identity that created or owns the memory.",
    )
    status: str = Field(
        default="active",
        description="Lifecycle state for the memory. Use 'active' for current notes and 'archived' for retained historical notes.",
    )


class MemoryMetaPatch(BaseModel):
    title: str | None = Field(default=None, description="Replacement human-readable title.")
    category: str | None = Field(default=None, description="Replacement memory category.")
    short_description: str | None = Field(
        default=None,
        description="Replacement one-sentence summary for search results and indexes.",
    )
    aliases: list[str] | None = Field(
        default=None,
        description="Replacement list of aliases. Pass an empty list to clear aliases.",
    )
    tags: list[str] | None = Field(
        default=None,
        description="Replacement list of tags. Pass an empty list to clear tags.",
    )
    author: str | None = Field(default=None, description="Replacement author or owner.")
    status: str | None = Field(
        default=None,
        description="Replacement lifecycle state, commonly 'active' or 'archived'.",
    )


class SearchFilters(BaseModel):
    category: str | None = Field(default=None, description="Only return memories in this category.")
    author: str | None = Field(default=None, description="Only return memories by this author or owner.")
    status: str | None = Field(default=None, description="Only return memories with this lifecycle state.")
    tags: list[str] | None = Field(
        default=None,
        description="Only return memories containing all of these tags.",
    )


def create_server(memory_root: str | Path = DEFAULT_MEMORY_ROOT) -> FastMCP:
    store = MemoryStore(memory_root)
    server = FastMCP(
        "Smriti",
        instructions=(
            "Smriti gives agents durable markdown memory. Store facts, decisions, "
            "preferences, project context, and reusable notes that should survive "
            "beyond the current chat."
        ),
    )

    @server.tool(
        description=(
            "Create a durable markdown memory for facts, decisions, preferences, "
            "or project context that should survive beyond the current chat."
        )
    )
    def create_memory(
        meta: Annotated[
            MemoryMetaInput,
            Field(description="Structured metadata used for naming, grouping, filtering, and retrieval."),
        ],
        content: Annotated[
            str,
            Field(description="Markdown body of the memory. Use wikilinks like [[Other Memory]] to relate notes."),
        ],
        id: Annotated[
            str | None,
            Field(
                description=(
                    "Optional stable memory id such as 'project/Deploy Workflow'. "
                    "If omitted, Smriti creates one from category and title."
                )
            ),
        ] = None,
    ) -> dict[str, Any]:
        return store.create_memory(
            meta=meta.model_dump(exclude_none=True),
            content=content,
            id=id,
        )

    @server.tool(description="Retrieve a memory note by id and return its complete markdown with YAML frontmatter.")
    def get_memory(
        id: Annotated[str, Field(description="Memory id returned by create_memory, for example 'project/Deploy Workflow'.")]
    ) -> str:
        return store.get_memory(id)

    @server.tool(
        description=(
            "Append new markdown to an existing memory while preserving its current "
            "content and updating the modified timestamp."
        )
    )
    def append_memory(
        id: Annotated[str, Field(description="Memory id to append to.")],
        content: Annotated[str, Field(description="Markdown content to append to the end of the memory.")],
    ) -> dict[str, Any]:
        return store.append_memory(id=id, content=content)

    @server.tool(
        description=(
            "Patch memory metadata and optionally replace the full markdown body. "
            "Use append_memory when adding incremental observations."
        )
    )
    def update_memory(
        id: Annotated[str, Field(description="Memory id to update.")],
        meta: Annotated[
            MemoryMetaPatch | None,
            Field(description="Partial metadata changes. Omitted fields keep their existing values."),
        ] = None,
        content: Annotated[
            str | None,
            Field(description="Replacement markdown body. Leave null to preserve existing content."),
        ] = None,
    ) -> dict[str, Any]:
        patch = meta.model_dump(exclude_none=True) if meta is not None else None
        return store.update_memory(id=id, meta=patch, content=content)

    @server.tool(description="Mark a memory as archived without deleting its markdown file.")
    def archive_memory(
        id: Annotated[str, Field(description="Memory id to mark as archived.")]
    ) -> dict[str, Any]:
        return store.archive_memory(id)

    @server.tool(description="Permanently delete a memory note by id.")
    def delete_memory(
        id: Annotated[str, Field(description="Memory id to permanently delete.")]
    ) -> dict[str, Any]:
        return store.delete_memory(id)

    @server.tool(
        description=(
            "List memory metadata for browsing or filtering without returning full "
            "note bodies. Use search_memory when you need relevance ranking."
        )
    )
    def list_memories(
        category: Annotated[str | None, Field(description="Optional category filter.")] = None,
        status: Annotated[str | None, Field(description="Optional lifecycle status filter, such as 'active' or 'archived'.")] = None,
        tags: Annotated[list[str] | None, Field(description="Optional tags that every returned memory must contain.")] = None,
        limit: Annotated[int, Field(description="Maximum number of memories to return.", ge=1, le=500)] = 50,
    ) -> dict[str, Any]:
        results = store.list_memories(category=category, status=status, tags=tags, limit=limit)
        return {"results": results, "count": len(results)}

    @server.tool(
        description=(
            "Search durable memories with relevance ranking over title, aliases, "
            "tags, path, description, and body terms."
        )
    )
    def search_memory(
        query: Annotated[str, Field(description="Search terms, phrase, or topic to retrieve relevant memories for.")],
        limit: Annotated[int, Field(description="Maximum number of ranked results to return.", ge=1, le=50)] = 10,
        filters: Annotated[
            SearchFilters | None,
            Field(description="Optional exact-match metadata filters applied before ranking."),
        ] = None,
        include_content: Annotated[
            bool,
            Field(description="When true, include full markdown content in each result; set false to save context."),
        ] = True,
    ) -> dict[str, Any]:
        results = store.search_memory(
            query=query,
            limit=limit,
            filters=filters.model_dump(exclude_none=True) if filters is not None else None,
            include_content=include_content,
        )
        return {"results": results, "count": len(results)}

    @server.tool(description="Build or refresh the human-readable markdown memory index at index.md.")
    def build_memory_index(
        group_by_category: Annotated[
            bool,
            Field(description="When true, group index entries under category headings."),
        ] = True
    ) -> dict[str, Any]:
        return store.build_memory_index(group_by_category=group_by_category)

    @server.tool(
        description=(
            "Repair and rebuild the memory store: optionally fix frontmatter, "
            "apply or normalize wikilinks from memory titles and aliases using "
            "longest matches first, then rebuild index.md and index.yaml."
        )
    )
    def rebuild_memory(
        apply_wikilinks: Annotated[
            bool,
            Field(description="When true, add and normalize wikilinks based on memory titles and aliases."),
        ] = True,
        fix_frontmatter: Annotated[
            bool,
            Field(description="When true, repair missing or malformed required frontmatter fields before indexing."),
        ] = True,
        group_by_category: Annotated[
            bool,
            Field(description="When true, group generated index.md entries under category headings."),
        ] = True,
        dry_run: Annotated[
            bool,
            Field(description="When true, report proposed frontmatter and wikilink changes without writing files or indexes."),
        ] = False,
    ) -> dict[str, Any]:
        return store.rebuild_memory(
            apply_wikilinks=apply_wikilinks,
            fix_frontmatter=fix_frontmatter,
            group_by_category=group_by_category,
            dry_run=dry_run,
        )

    @server.tool(description="Load the generated markdown memory index, optionally refreshing it first.")
    def load_memory_index(
        refresh: Annotated[
            bool,
            Field(description="When true, rebuild index.md before returning it."),
        ] = False
    ) -> str:
        return store.load_memory_index(refresh=refresh)

    return server
