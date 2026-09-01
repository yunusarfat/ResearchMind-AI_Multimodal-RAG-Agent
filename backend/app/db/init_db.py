"""
One-time DB setup:
  1. Enable the pgvector extension.
  2. Create all tables + an IVFFlat index for fast approximate vector search.

Run with:  python -m app.db.init_db
"""

import asyncio

from sqlalchemy import text

from app.db.database import Base, engine
from app.db import models  # noqa: F401  (import so tables are registered on Base.metadata)


async def init_db() -> None:
    async with engine.begin() as conn:
        # 1. Enable pgvector
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        # 2. Create tables
        await conn.run_sync(Base.metadata.create_all)

        # 3. Approximate nearest-neighbour index (cosine distance).
        #    IVFFlat needs the table to have data before it's maximally useful,
        #    but creating it up front is fine for a project this size.
        await conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS chunks_embedding_idx
                ON chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
                """
            )
        )

    print("✅ pgvector extension enabled, tables created, index created.")


if __name__ == "__main__":
    asyncio.run(init_db())
