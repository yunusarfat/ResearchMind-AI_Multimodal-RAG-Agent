# """
# Evaluate retrieval quality across methods: dense-only, BM25-only,
# hybrid (RRF), and hybrid+reranked, scoped to one user's documents.
# Prints a comparison table using real, computed metrics against your
# ground-truth eval set.

# Usage:
#     python -m scripts.evaluate_rag data/eval/eval_set.json --email you@example.com --k 5

# The eval set is a JSON file you create yourself (see
# data/eval/eval_set.example.json for the format) -- there is no way to
# compute honest metrics without real ground-truth answers from your
# own documents.
# """

# import argparse
# import asyncio
# import json

# from sqlalchemy import select

# from app.db.database import get_session
# from app.db.models import User
# from app.evaluation.retrieval import EvalQuery, average_metrics, evaluate_single_query
# from app.rag.reranking.reranker import get_reranker
# from app.rag.retrieval.bm25 import get_bm25_registry
# from app.rag.retrieval.hybrid_search import hybrid_search
# from app.rag.retrieval.vector_search import vector_search


# def load_eval_set(path: str) -> list[EvalQuery]:
#     with open(path, "r", encoding="utf-8") as f:
#         raw = json.load(f)
#     return [EvalQuery(query=item["query"], relevant_chunk_ids=item["relevant_chunk_ids"]) for item in raw]


# async def get_user_id_by_email(email: str) -> str:
#     async with get_session() as session:
#         user = await session.scalar(select(User).where(User.email == email))
#     if user is None:
#         raise SystemExit(f"No account found for '{email}'. Sign up first via POST /auth/signup.")
#     return str(user.id)


# async def run_evaluation(eval_set_path: str, email: str, k: int) -> None:
#     user_id = await get_user_id_by_email(email)
#     eval_queries = load_eval_set(eval_set_path)
#     if not eval_queries:
#         print("Eval set is empty.")
#         return

#     async with get_session() as session:
#         print("Building BM25 index for this user...")
#         await get_bm25_registry().build_for_user(session, user_id)

#         dense_results, bm25_results_metrics, hybrid_results_metrics, reranked_results_metrics = [], [], [], []

#         for eq in eval_queries:
#             # --- Dense only ---
#             dense = await vector_search(session, eq.query, user_id=user_id, top_k=k)
#             dense_ids = [c.chunk_id for c in dense]
#             dense_results.append(evaluate_single_query(dense_ids, eq.relevant_chunk_ids, k))

#             # --- BM25 only ---
#             bm25 = await get_bm25_registry().search(session, eq.query, user_id=user_id, top_k=k)
#             bm25_ids = [c.chunk_id for c in bm25]
#             bm25_results_metrics.append(evaluate_single_query(bm25_ids, eq.relevant_chunk_ids, k))

#             # --- Hybrid (RRF fusion) ---
#             hybrid = await hybrid_search(session, eq.query, user_id=user_id, top_k=k)
#             hybrid_ids = [c.chunk_id for c in hybrid]
#             hybrid_results_metrics.append(evaluate_single_query(hybrid_ids, eq.relevant_chunk_ids, k))

#             # --- Hybrid + Reranked ---
#             reranker = get_reranker()
#             reranked = reranker.rerank(eq.query, hybrid, top_k=k)
#             reranked_ids = [c.chunk_id for c in reranked]
#             reranked_results_metrics.append(evaluate_single_query(reranked_ids, eq.relevant_chunk_ids, k))

#     methods = {
#         "Dense (vector) only": dense_results,
#         "BM25 only": bm25_results_metrics,
#         "Hybrid (RRF)": hybrid_results_metrics,
#         "Hybrid + Reranked": reranked_results_metrics,
#     }

#     print(f"\n{'='*72}")
#     print(f"RETRIEVAL EVALUATION — {len(eval_queries)} queries, K={k}")
#     print(f"{'='*72}")
#     print(f"{'Method':<22}{'Recall@K':>12}{'Precision@K':>14}{'MRR':>10}{'Hit Rate':>12}")
#     print("-" * 72)

#     for name, results in methods.items():
#         avg = average_metrics(results)
#         print(
#             f"{name:<22}"
#             f"{avg.recall_at_k*100:>11.1f}%"
#             f"{avg.precision_at_k*100:>13.1f}%"
#             f"{avg.mrr:>10.3f}"
#             f"{avg.hit_rate*100:>11.1f}%"
#         )

#     print(f"{'='*72}\n")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Evaluate RAG retrieval quality for one user.")
#     parser.add_argument("eval_set", help="Path to eval_set.json")
#     parser.add_argument("--email", required=True, help="Email of the account whose documents to evaluate against")
#     parser.add_argument("--k", type=int, default=5, help="Top-K cutoff (default: 5)")
#     args = parser.parse_args()

#     asyncio.run(run_evaluation(args.eval_set, args.email, args.k))





"""
Evaluate retrieval quality across methods: dense-only, BM25-only,
hybrid (RRF), and hybrid+reranked, scoped to one user's documents.
Prints a comparison table using real, computed metrics against your
ground-truth eval set.

Usage:
    python -m scripts.evaluate_rag data/eval/eval_set.json --email you@example.com --k 5

The eval set is a JSON file you create yourself (see
data/eval/eval_set.example.json for the format) -- there is no way to
compute honest metrics without real ground-truth answers from your
own documents.
"""

import argparse
import asyncio
import json

from sqlalchemy import select

from app.db.database import get_session
from app.db.models import User
from app.evaluation.retrieval import EvalQuery, average_metrics, evaluate_single_query
# from app.rag.reranking.reranker import get_reranker
from app.rag.retrieval.bm25 import get_bm25_registry
from app.rag.retrieval.hybrid_search import hybrid_search
from app.rag.retrieval.vector_search import vector_search


def load_eval_set(path: str) -> list[EvalQuery]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [EvalQuery(query=item["query"], relevant_chunk_ids=item["relevant_chunk_ids"]) for item in raw]


async def get_user_id_by_email(email: str) -> str:
    async with get_session() as session:
        user = await session.scalar(select(User).where(User.email == email))
    if user is None:
        raise SystemExit(f"No account found for '{email}'. Sign up first via POST /auth/signup.")
    return str(user.id)


async def run_evaluation(eval_set_path: str, email: str, k: int) -> None:
    user_id = await get_user_id_by_email(email)
    eval_queries = load_eval_set(eval_set_path)
    if not eval_queries:
        print("Eval set is empty.")
        return

    async with get_session() as session:
        print("Building BM25 index for this user...")
        await get_bm25_registry().build_for_user(session, user_id)

        # dense_results, bm25_results_metrics, hybrid_results_metrics, reranked_results_metrics = [], [], [], []
        dense_results, bm25_results_metrics, hybrid_results_metrics = [], [], []

        for eq in eval_queries:
            # --- Dense only ---
            dense = await vector_search(session, eq.query, user_id=user_id, top_k=k)
            dense_ids = [c.chunk_id for c in dense]
            dense_results.append(evaluate_single_query(dense_ids, eq.relevant_chunk_ids, k))

            # --- BM25 only ---
            bm25 = await get_bm25_registry().search(session, eq.query, user_id=user_id, top_k=k)
            bm25_ids = [c.chunk_id for c in bm25]
            bm25_results_metrics.append(evaluate_single_query(bm25_ids, eq.relevant_chunk_ids, k))

            # --- Hybrid (RRF fusion) ---
            hybrid = await hybrid_search(session, eq.query, user_id=user_id, top_k=k)
            hybrid_ids = [c.chunk_id for c in hybrid]
            hybrid_results_metrics.append(evaluate_single_query(hybrid_ids, eq.relevant_chunk_ids, k))

            # --- Hybrid + Reranked ---
            # reranker = get_reranker()
            # reranked = reranker.rerank(eq.query, hybrid, top_k=k)
            # reranked_ids = [c.chunk_id for c in reranked]
            # reranked_results_metrics.append(evaluate_single_query(reranked_ids, eq.relevant_chunk_ids, k))

    methods = {
        "Dense (vector) only": dense_results,
        "BM25 only": bm25_results_metrics,
        "Hybrid (RRF)": hybrid_results_metrics,
        # "Hybrid + Reranked": reranked_results_metrics,
    }

    print(f"\n{'='*72}")
    print(f"RETRIEVAL EVALUATION — {len(eval_queries)} queries, K={k}")
    print(f"{'='*72}")
    print(f"{'Method':<22}{'Recall@K':>12}{'Precision@K':>14}{'MRR':>10}{'Hit Rate':>12}")
    print("-" * 72)

    for name, results in methods.items():
        avg = average_metrics(results)
        print(
            f"{name:<22}"
            f"{avg.recall_at_k*100:>11.1f}%"
            f"{avg.precision_at_k*100:>13.1f}%"
            f"{avg.mrr:>10.3f}"
            f"{avg.hit_rate*100:>11.1f}%"
        )

    print(f"{'='*72}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval quality for one user.")
    parser.add_argument("eval_set", help="Path to eval_set.json")
    parser.add_argument("--email", required=True, help="Email of the account whose documents to evaluate against")
    parser.add_argument("--k", type=int, default=5, help="Top-K cutoff (default: 5)")
    args = parser.parse_args()

    asyncio.run(run_evaluation(args.eval_set, args.email, args.k))
