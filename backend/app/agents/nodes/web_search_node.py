"""
Web search node.

Runs the web search tool and builds a numbered context block from the
results, using the same [1] [2] marker scheme as document retrieval —
so the generator prompt and citation rendering stay uniform regardless
of source.
"""

import asyncio

from app.agents.state import AgentState
from app.rag.context.builder import build_external_context
from app.tools.web_search import search_web


async def web_search_node(state: AgentState) -> AgentState:
    query = state["query"]

    # search_web is a blocking/sync call under the hood; run it off the
    # event loop thread so it doesn't stall other async work.
    results = await asyncio.to_thread(search_web, query)

    items = [{"title": r.title, "snippet": r.snippet, "url": r.url} for r in results]
    context = build_external_context(items, content_type="web")

    citations = [
        {
            "marker": c.marker,
            "chunk_id": c.chunk_id,
            "document_id": c.document_id,
            "page_number": c.page_number,
            "section": c.section,
            "content_type": c.content_type,
            "snippet": c.snippet,
        }
        for c in context.citations
    ]

    return {**state, "context_text": context.context_text, "citations": citations}
