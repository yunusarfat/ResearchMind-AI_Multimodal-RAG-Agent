"""
Sparse (lexical) retrieval using BM25.

Kept as an in-memory index (rank_bm25) rather than Postgres full-text
search so scoring is true BM25, not ts_rank -- this matters for exact
term / acronym / number queries ("BLEU score", "GPT-4") that dense
embeddings tend to blur.

One BM25 index is maintained PER USER (keyed by user_id), never a
single global index -- otherwise a query from user A could rank and
return chunks that belong to user B. Each user's index is built
lazily on first use and refreshed after that user uploads a document.

For a portfolio-scale corpus (a handful of users, dozens of papers
each) many small in-memory indices are fine; a larger deployment
would move this to Postgres FTS or a proper search service, still
partitioned by user/tenant.
"""

import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import Chunk

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


@dataclass
class _IndexedChunk:
    chunk_id: str
    document_id: str
    content: str
    page_number: int | None
    section: str | None
    content_type: str


class _UserBM25Index:
    """BM25 index for a single user's chunks."""

    def __init__(self) -> None:
        self._bm25: BM25Okapi | None = None
        self._chunks: list[_IndexedChunk] = []

    def build_from_rows(self, rows) -> None:
        self._chunks = [
            _IndexedChunk(
                chunk_id=str(c.id),
                document_id=str(c.document_id),
                content=c.content,
                page_number=c.page_number,
                section=c.section,
                content_type=c.content_type,
            )
            for c in rows
        ]
        tokenized_corpus = [_tokenize(c.content) for c in self._chunks]
        self._bm25 = BM25Okapi(tokenized_corpus) if tokenized_corpus else None

    def search(self, query: str, top_k: int):
        from app.rag.retrieval.vector_search import RetrievedChunk  # local import avoids cycle

        if self._bm25 is None or not self._chunks:
            return []

        tokenized_query = _tokenize(query)
        scores = self._bm25.get_scores(tokenized_query)

        ranked = sorted(zip(self._chunks, scores), key=lambda x: x[1], reverse=True)[:top_k]

        return [
            RetrievedChunk(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                content=c.content,
                page_number=c.page_number,
                section=c.section,
                content_type=c.content_type,
                score=float(score),
                source="bm25",
            )
            for c, score in ranked
            if score > 0
        ]


class BM25Registry:
    """Holds one _UserBM25Index per user_id. This is the module-level
    singleton the rest of the app imports via get_bm25_registry()."""

    def __init__(self) -> None:
        self._indices: dict[str, _UserBM25Index] = {}

    async def build_for_user(self, session: AsyncSession, user_id: str) -> None:
        """(Re)build the BM25 index for a single user from current DB state."""
        result = await session.execute(select(Chunk).where(Chunk.user_id == user_id))
        rows = result.scalars().all()

        index = _UserBM25Index()
        index.build_from_rows(rows)
        self._indices[user_id] = index

    async def refresh_for_user(self, session: AsyncSession, user_id: str) -> None:
        await self.build_for_user(session, user_id)

    async def get_or_build(self, session: AsyncSession, user_id: str) -> _UserBM25Index:
        """Return the user's index, building it lazily if this is the
        first request for that user since startup."""
        if user_id not in self._indices:
            await self.build_for_user(session, user_id)
        return self._indices[user_id]

    async def search(self, session: AsyncSession, query: str, user_id: str, top_k: int | None = None):
        top_k = top_k or settings.BM25_TOP_K
        index = await self.get_or_build(session, user_id)
        return index.search(query, top_k)


_bm25_registry = BM25Registry()


def get_bm25_registry() -> BM25Registry:
    """Module-level singleton so the API layer and scripts share one registry."""
    return _bm25_registry
