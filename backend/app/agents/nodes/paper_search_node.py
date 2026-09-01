"""
Paper search node.

Runs the arXiv paper search tool and builds a numbered context block
from the results — same pattern as web_search_node.py.
"""

import asyncio

from app.agents.state import AgentState
from app.rag.context.builder import build_external_context
from app.tools.paper_search import search_papers


async def paper_search_node(state: AgentState) -> AgentState:
    query = state["query"]

    results = await asyncio.to_thread(search_papers, query)

    items = [
        {
            "title": r.title,
            "snippet": f"{r.summary} (Authors: {', '.join(r.authors[:3])}"
                       f"{'et al.' if len(r.authors) > 3 else ''}; Published: {r.published})",
            "url": r.url,
        }
        for r in results
    ]
    context = build_external_context(items, content_type="paper")

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
