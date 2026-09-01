"""
Context construction.

Takes the final reranked chunks and turns them into:
  1. A single context string to inject into the LLM prompt, with each
     chunk tagged [1], [2], ... so the model can cite them inline.
  2. A parallel list of citation metadata the frontend can use to
     resolve [1] -> "Paper.pdf, page 8".

Kept deliberately separate from prompting/generation (which belongs
to the agent layer added later) — this module's only job is turning
retrieved chunks into a clean, traceable context block.
"""

from dataclasses import dataclass

from app.core.config import settings
from app.rag.retrieval.vector_search import RetrievedChunk


@dataclass
class Citation:
    marker: str  # "[1]"
    chunk_id: str
    document_id: str
    page_number: int | None
    section: str | None
    content_type: str
    snippet: str  # short preview for UI
    source_url: str | None = None  # set for external sources (web, arxiv)


@dataclass
class BuiltContext:
    context_text: str
    citations: list[Citation]


def build_context(
    chunks: list[RetrievedChunk],
    max_chars: int | None = None,
    snippet_len: int = 160,
) -> BuiltContext:
    """
    Build a numbered context block:

        [1] (Page 8, Results) The proposed model achieves ...
        [2] (Page 3, Methodology) We use a two-stage ...

    Truncates to `max_chars` total if provided (simple compression —
    a smarter version could summarize instead of hard-truncating).
    """
    lines: list[str] = []
    citations: list[Citation] = []
    running_len = 0

    for i, chunk in enumerate(chunks, start=1):
        marker = f"[{i}]"
        location = ", ".join(
            part for part in [
                f"Page {chunk.page_number}" if chunk.page_number else None,
                chunk.section,
            ] if part
        )
        header = f"{marker} ({location})" if location else marker
        line = f"{header} {chunk.content}"

        if max_chars is not None and running_len + len(line) > max_chars:
            break

        lines.append(line)
        running_len += len(line)

        citations.append(
            Citation(
                marker=marker,
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                page_number=chunk.page_number,
                section=chunk.section,
                content_type=chunk.content_type,
                snippet=(chunk.content[:snippet_len] + "…") if len(chunk.content) > snippet_len else chunk.content,
            )
        )

    return BuiltContext(context_text="\n\n".join(lines), citations=citations)


def build_external_context(
    items: list[dict],
    content_type: str,
    snippet_len: int = 200,
) -> BuiltContext:
    """
    Build a numbered context block from external tool results (web
    search, arXiv paper search) using the same [1] [2] marker scheme
    as build_context, so the generator prompt and citation rendering
    stay uniform regardless of where a source came from.

    Each item is a dict with keys: title, snippet, url. (For paper
    search results, callers pass the paper summary as `snippet`.)
    """
    lines: list[str] = []
    citations: list[Citation] = []

    for i, item in enumerate(items, start=1):
        marker = f"[{i}]"
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        url = item.get("url", "")

        header = f"{marker} ({title})" if title else marker
        line = f"{header} {snippet}"
        lines.append(line)

        citations.append(
            Citation(
                marker=marker,
                chunk_id=url or f"{content_type}-{i}",
                document_id=url,
                page_number=None,
                section=title,
                content_type=content_type,
                snippet=(snippet[:snippet_len] + "…") if len(snippet) > snippet_len else snippet,
                source_url=url,
            )
        )

    return BuiltContext(context_text="\n\n".join(lines), citations=citations)
