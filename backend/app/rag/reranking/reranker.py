"""
Reranking.

Hybrid search is fast but approximate (bi-encoder + BM25). A
cross-encoder reranker looks at (query, chunk) pairs *jointly*,
which is slower but much more precise — so we only run it on the
small shortlist that hybrid search already narrowed down.
"""

from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.core.config import settings
from app.rag.retrieval.vector_search import RetrievedChunk


class Reranker:
    def __init__(self, model_name: str | None = None, device: str | None = None):
        self.model_name = model_name or settings.RERANKER_MODEL
        self.device = device or settings.DEVICE
        self._model = CrossEncoder(self.model_name, device=self.device)

    def rerank(
        self, query: str, chunks: list[RetrievedChunk], top_k: int | None = None
    ) -> list[RetrievedChunk]:
        top_k = top_k or settings.RERANK_TOP_K
        if not chunks:
            return []

        pairs = [(query, c.content) for c in chunks]
        scores = self._model.predict(pairs)

        reranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)[:top_k]

        return [
            RetrievedChunk(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                content=c.content,
                page_number=c.page_number,
                section=c.section,
                content_type=c.content_type,
                score=float(score),
                source="rerank",
            )
            for c, score in reranked
        ]


@lru_cache
def get_reranker() -> Reranker:
    """Cached singleton — the cross-encoder model is expensive to load."""
    return Reranker()
