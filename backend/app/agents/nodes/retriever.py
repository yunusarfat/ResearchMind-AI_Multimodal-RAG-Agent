# """
# Retriever node.

# Thin wrapper around the existing RAG pipeline (hybrid search -> rerank
# -> context builder). This node doesn't reimplement any retrieval
# logic -- it's the seam between the agent graph and the RAG core, and
# it's exactly where a future "which tool(s) to call" planner would
# plug in additional retrieval sources.

# `user_id` is bound into this node via functools.partial when the
# graph is built (see graph.py) -- every retrieval the agent performs
# is scoped to one user's documents.
# """

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.agents.state import AgentState
# from app.rag.context.builder import build_context
# from app.rag.reranking.reranker import get_reranker
# from app.rag.retrieval.hybrid_search import hybrid_search


# async def retrieve(state: AgentState, session: AsyncSession, user_id: str) -> AgentState:
#     """LangGraph node: sets state['context_text'] and state['citations'].

#     Takes `session` and `user_id` as explicit arguments (rather than
#     opening its own session or trusting state) since both are
#     request-scoped and must not be guessable/omittable.
#     """
#     query = state["query"]

#     hybrid_results = await hybrid_search(session, query, user_id=user_id)
#     reranker = get_reranker()
#     final_chunks = reranker.rerank(query, hybrid_results)
#     context = build_context(final_chunks)

#     citations = [
#         {
#             "marker": c.marker,
#             "chunk_id": c.chunk_id,
#             "document_id": c.document_id,
#             "page_number": c.page_number,
#             "section": c.section,
#             "content_type": c.content_type,
#             "snippet": c.snippet,
#         }
#         for c in context.citations
#     ]

#     return {**state, "context_text": context.context_text, "citations": citations}






"""
Retriever node.

Thin wrapper around the existing RAG pipeline (hybrid search -> context
builder). This node doesn't reimplement any retrieval logic -- it's the
seam between the agent graph and the RAG core.

`user_id` is bound into this node via functools.partial when the graph is
built (see graph.py) -- every retrieval the agent performs is scoped to
one user's documents.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.rag.context.builder import build_context
from app.rag.retrieval.hybrid_search import hybrid_search


async def retrieve(state: AgentState, session: AsyncSession, user_id: str) -> AgentState:
    """LangGraph node: sets state['context_text'] and state['citations'].

    Takes `session` and `user_id` as explicit arguments (rather than
    opening its own session or trusting state) since both are request-scoped
    and must not be guessable/omittable.
    """
    query = state["query"]

    hybrid_results = await hybrid_search(session, query, user_id=user_id)
    context = build_context(hybrid_results)

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