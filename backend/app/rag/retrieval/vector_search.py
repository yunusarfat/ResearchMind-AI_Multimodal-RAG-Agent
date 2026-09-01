"""
Dense (semantic) retrieval using pgvector.

Uses the `<=>` cosine-distance operator that pgvector adds to
Postgres. Since embeddings are normalized at encode time,
cosine_distance = 1 - cosine_similarity, so we convert back to a
similarity score for readability / fusion.

`user_id` is a required filter, not optional -- every retrieval call
in this app is scoped to a single account, so it is impossible to
accidentally search across users by forgetting to pass it.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import Chunk
from app.rag.embeddings.text_embeddings import get_embedder


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    content: str
    page_number: int | None
    section: str | None
    content_type: str
    score: float  # higher is better, meaning depends on retrieval method
    source: str  # "vector" | "bm25" | "hybrid" | "rerank"


async def vector_search(
    session: AsyncSession, query: str, user_id: str, top_k: int | None = None
) -> list[RetrievedChunk]:
    """Return the top_k chunks most semantically similar to `query`,
    restricted to chunks owned by `user_id`."""
    top_k = top_k or settings.VECTOR_TOP_K
    embedder = get_embedder()
    query_embedding = embedder.embed_query(query)

    # cosine_distance() is provided by pgvector.sqlalchemy's Vector type.
    distance = Chunk.embedding.cosine_distance(query_embedding)

    stmt = (
        select(Chunk, distance.label("distance"))
        .where(Chunk.user_id == user_id)
        .order_by(distance.asc())
        .limit(top_k)
    )

    result = await session.execute(stmt)
    rows = result.all()

    retrieved: list[RetrievedChunk] = []
    for chunk, dist in rows:
        similarity = 1 - float(dist)
        retrieved.append(
            RetrievedChunk(
                chunk_id=str(chunk.id),
                document_id=str(chunk.document_id),
                content=chunk.content,
                page_number=chunk.page_number,
                section=chunk.section,
                content_type=chunk.content_type,
                score=similarity,
                source="vector",
            )
        )

    return retrieved
