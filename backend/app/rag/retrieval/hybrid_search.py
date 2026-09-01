"""
Hybrid search: fuses dense (pgvector) and sparse (BM25) results using
Reciprocal Rank Fusion (RRF).

RRF is used instead of a weighted score-sum because vector similarity
and BM25 scores live on completely different scales -- RRF sidesteps
that by fusing on *rank position* rather than raw score, which is
simpler and more robust than tuning a weight coefficient.

    RRF(d) = sum over each ranker r of  1 / (k + rank_r(d))

`user_id` is required and passed through to both underlying searches
so results never cross accounts.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.rag.retrieval.bm25 import get_bm25_registry
from app.rag.retrieval.vector_search import RetrievedChunk, vector_search


async def hybrid_search(
    session: AsyncSession,
    query: str,
    user_id: str,
    top_k: int | None = None,
    rrf_k: int | None = None,
) -> list[RetrievedChunk]:
    top_k = top_k or settings.HYBRID_TOP_K
    rrf_k = rrf_k or settings.RRF_K

    vector_results = await vector_search(session, query, user_id=user_id, top_k=settings.VECTOR_TOP_K)
    bm25_results = await get_bm25_registry().search(
        session, query, user_id=user_id, top_k=settings.BM25_TOP_K
    )

    # rank position (1-indexed) per chunk_id, per retriever
    fused_scores: dict[str, float] = {}
    chunk_lookup: dict[str, RetrievedChunk] = {}

    for rank, chunk in enumerate(vector_results, start=1):
        fused_scores[chunk.chunk_id] = fused_scores.get(chunk.chunk_id, 0.0) + 1.0 / (rrf_k + rank)
        chunk_lookup[chunk.chunk_id] = chunk

    for rank, chunk in enumerate(bm25_results, start=1):
        fused_scores[chunk.chunk_id] = fused_scores.get(chunk.chunk_id, 0.0) + 1.0 / (rrf_k + rank)
        chunk_lookup.setdefault(chunk.chunk_id, chunk)

    ranked_ids = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    fused_results: list[RetrievedChunk] = []
    for chunk_id, score in ranked_ids:
        base = chunk_lookup[chunk_id]
        fused_results.append(
            RetrievedChunk(
                chunk_id=base.chunk_id,
                document_id=base.document_id,
                content=base.content,
                page_number=base.page_number,
                section=base.section,
                content_type=base.content_type,
                score=score,
                source="hybrid",
            )
        )

    return fused_results
