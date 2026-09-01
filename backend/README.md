# ResearchMind — RAG Core (Phase 1)


This is the standalone RAG backend: ingestion → chunking → embeddings →
pgvector storage → hybrid search (dense + BM25) → reranking → context
building. No FastAPI yet — that wraps this in Phase 2.

## 1. Install PostgreSQL + pgvector

Easiest path: Docker.

```bash
docker run -d --name researchmind-pg \
  -e POSTGRES_USER=researchmind \
  -e POSTGRES_PASSWORD=researchmind \
  -e POSTGRES_DB=researchmind \
  -p 5432:5432 \
  ankane/pgvector
```

(`ankane/pgvector` is Postgres with the pgvector extension pre-installed.
If you install Postgres yourself instead, install the `pgvector` extension
separately — see https://github.com/pgvector/pgvector#installation.)

## 2. Python environment

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configure environment variables

```bash
cp .env.example .env
```

Defaults match the Docker command above, so you likely don't need to
edit anything for local dev.

## 4. Initialize the database

Creates the `vector` extension, the `documents`/`chunks` tables, and a
vector index.

```bash
python -m app.db.init_db
```

## 5. Ingest documents

Drop a few PDFs into `data/uploads/`, then:

```bash
python -m scripts.ingest_documents data/uploads
```

This loads each PDF → cleans text → chunks it → embeds chunks with
`BAAI/bge-base-en-v1.5` → stores everything in Postgres.

(First run downloads the embedding model from HuggingFace — a few
hundred MB, needs internet access once.)

## 6. Query the pipeline

```bash
python -m scripts.query_pipeline "What is the main contribution of this paper?"
```

This runs: BM25 index build → hybrid search (vector + BM25 fused via
RRF) → cross-encoder reranking → final context block with citation
markers `[1] [2] ...` — printed to the terminal so you can sanity-check
retrieval quality before wiring in FastAPI/agents.

---

## How the pieces connect

```
loader.py (read PDF)
   → parser.py (tag pages with section headings)
      → cleaner.py (strip PDF noise, normalize whitespace)
         → text_chunker.py (split into overlapping chunks)
            → text_embeddings.py (embed chunks, BGE model)
               → [stored in Postgres via db/models.py]

query
   → vector_search.py  ─┐
   → bm25.py            ─┼→ hybrid_search.py (RRF fusion)
                                → reranker.py (cross-encoder top-K)
                                   → context/builder.py (numbered context + citations)
```

- **`app/core/config.py`** is the single source of truth for every
  setting (model names, chunk size, top-k values). Everything else
  imports `settings` from here — change `.env`, not code.
- **`app/db/models.py`** defines `Document` and `Chunk`. `Chunk.embedding`
  is a `pgvector` `Vector(768)` column — dimension must match
  `VECTOR_DIM` in `.env` and whatever embedding model you use.
- **BM25 is in-memory** (`rank_bm25`), rebuilt from the DB via
  `BM25Index.build()`. Call this once at startup (or after ingesting
  new documents) — it's already wired into `scripts/query_pipeline.py`.
  When you build the FastAPI layer, build it once on app startup
  (`@app.on_event("startup")`) rather than per-request.
- **Hybrid search** fuses vector + BM25 rankings with Reciprocal Rank
  Fusion (RRF) — robust because it doesn't require tuning a weight
  between two differently-scaled score types.
- **Reranking** only runs on the ~15 hybrid candidates, not the whole
  corpus — it's a precision pass, not a search step.

## What's intentionally deferred to later phases

- FastAPI wrapper (routes, request/response schemas)
- LangGraph agent orchestration + MCP tools
- Multimodal processors (image/table/chart) — `Chunk.content_type`
  already supports `"table"`/`"image"`/`"chart"` values so this layer
  slots in without a schema change
- Verification layer, evaluation (Ragas), observability
- Auth, rate limiting, and the rest of the security layer

## Common gotchas

- **`VECTOR_DIM` mismatch**: if you change `EMBEDDING_MODEL` to one with
  a different output dimension, update `VECTOR_DIM` in `.env` *and*
  re-run `init_db.py` against a fresh DB (or migrate the column) — pgvector
  enforces the dimension at the column level.
- **Empty BM25 results**: the in-memory index only reflects chunks that
  existed the last time `.build()` was called. If you ingest more docs,
  rebuild it (restart the script, or add a refresh call).
- **GPU**: set `DEVICE=cuda` in `.env` if you have a CUDA GPU available —
  embedding/reranking will be significantly faster on larger corpora.
