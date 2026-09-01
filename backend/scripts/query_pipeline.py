"""
End-to-end test of the retrieval pipeline for one user's documents:
hybrid search (vector + BM25 via RRF) -> rerank -> build context.

Usage:
    python -m scripts.query_pipeline "What is the main contribution?" --email you@example.com
"""

import argparse
import asyncio

from sqlalchemy import select

from app.db.database import get_session
from app.db.models import User
from app.rag.context.builder import build_context
from app.rag.reranking.reranker import get_reranker
from app.rag.retrieval.bm25 import get_bm25_registry
from app.rag.retrieval.hybrid_search import hybrid_search


async def get_user_id_by_email(email: str) -> str:
    async with get_session() as session:
        user = await session.scalar(select(User).where(User.email == email))
    if user is None:
        raise SystemExit(f"No account found for '{email}'. Sign up first via POST /auth/signup.")
    return str(user.id)


async def run_query(query: str, email: str) -> None:
    user_id = await get_user_id_by_email(email)

    async with get_session() as session:
        print("Building BM25 index for this user...")
        await get_bm25_registry().build_for_user(session, user_id)

        print("Running hybrid search (vector + BM25, RRF fusion)...")
        hybrid_results = await hybrid_search(session, query, user_id=user_id)

        print(f"Reranking top {len(hybrid_results)} candidates...")
        reranker = get_reranker()
        final_chunks = reranker.rerank(query, hybrid_results)

    context = build_context(final_chunks)

    print("\n" + "=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)
    print("\n--- CONTEXT (would be injected into the LLM prompt) ---\n")
    print(context.context_text or "(no relevant chunks found)")

    print("\n--- CITATIONS ---")
    for c in context.citations:
        print(f"{c.marker} doc={c.document_id[:8]} page={c.page_number} section={c.section} "
              f"type={c.content_type}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the RAG retrieval pipeline for one user.")
    parser.add_argument("query", help="Natural language question")
    parser.add_argument("--email", required=True, help="Email of the account whose documents to search")
    args = parser.parse_args()

    asyncio.run(run_query(args.query, args.email))
