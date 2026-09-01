# ResearchMind-AI

An agentic RAG system for research papers and documents — upload PDFs, ask questions, and get cited answers pulled from your own documents, the open web, or arXiv, depending on what the question needs.

Unlike a plain "embed and retrieve" RAG pipeline, ResearchMind routes every query through a planning agent that decides *how* to answer it: pull from your uploaded documents, search the web, search arXiv for papers, or just answer directly — then streams the response back with numbered citations pointing at the exact source chunk.

---

## Live Demo

- **App:** [your-frontend-url.vercel.app](https://research-mind-ai-wine.vercel.app/)

> Hosted on Render's free tier — the backend may take ~30–60s to wake up on the first request after a period of inactivity.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Design Notes](#design-notes)
- [Roadmap](#roadmap)

---

## Features

- **Agentic query routing** — a planner node (LangGraph) decides per-query whether to retrieve from your documents, search the web, search arXiv, or answer directly, instead of always doing the same fixed retrieval step.
- **Hybrid retrieval** — dense vector search (pgvector) fused with BM25 lexical search via Reciprocal Rank Fusion, so both semantic and exact-keyword matches surface.
- **Multimodal ingestion** — tables, images, and charts inside PDFs are extracted and described (via Gemini vision), then embedded and indexed the same way as text, so a query can retrieve a chart just as easily as a paragraph.
- **Cited answers** — every generated answer carries `[1] [2] ...` markers tied back to the exact chunk, page, and section it came from.
- **Streaming responses** — answers stream token-by-token over HTTP rather than waiting for the full generation to complete.
- **Dual auth** — email/password (JWT) and Google Sign-In (Firebase), both issuing the same backend-signed session token.
- **Multi-chat history** — conversations are persisted per user, so past chats and their sources can be revisited.

## Architecture

```
                          ┌──────────────┐
                          │   Planner    │  (decides the route)
                          └──────┬───────┘
              ┌───────────┬──────┴──────┬────────────┐
              ▼           ▼             ▼             ▼
        ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐
        │ Retriever│ │Web Search│ │Paper Search│ │  Direct  │
        │(your docs)│ │(internet)│ │  (arXiv)  │ │(no tool) │
        └────┬─────┘ └────┬─────┘ └─────┬─────┘ └────┬─────┘
             └────────────┴──────┬──────┴────────────┘
                                  ▼
                          ┌──────────────┐
                          │  Generator   │  (streams cited answer)
                          └──────────────┘
```

**Document ingestion pipeline:**

```
PDF upload
   → loader.py        (read PDF)
      → parser.py      (tag pages with section headings)
         → cleaner.py  (strip PDF noise, normalize whitespace)
            → text_chunker.py       (split into overlapping chunks)
            → multimodal/pipeline.py (extract + describe tables/images/charts)
               → text_embeddings.py  (embed everything via Gemini)
                  → Postgres (pgvector) + BM25 index
```


## Tech Stack

| Layer | Choice |
|---|---|
| API | FastAPI + Uvicorn |
| Agent orchestration | LangGraph |
| LLM | Google Gemini (`google-genai`) — generation, vision, and embeddings |
| Database | PostgreSQL + [pgvector](https://github.com/pgvector/pgvector) |
| ORM | SQLAlchemy 2.0 (async) + Alembic |
| Lexical search | rank-bm25 |
| PDF parsing | pypdf, pdfplumber, PyMuPDF |
| Auth | JWT (email/password) + Firebase Admin (Google Sign-In) |
| Web/paper search | ddgs (web), arxiv |

Embeddings run through the Gemini API rather than a local model — this keeps the service lightweight enough to run comfortably on small deploy targets (e.g. Render's free tier) without bundling `torch`.

## Project Structure

```
app/
├── agents/            # LangGraph planner, routing, and tool nodes
│   ├── nodes/          # planner, retriever, web_search, paper_search, generator
│   ├── routers/         # route_after_planning
│   ├── graph.py         # wires the nodes into a compiled graph
│   └── state.py
├── api/                # FastAPI routers: auth, documents, chats, chat
├── core/               # config, JWT/security, Firebase, LLM client
├── db/                  # SQLAlchemy models, session, init_db
├── multimodal/          # table/image/chart extraction + description
├── rag/
│   ├── ingestion/        # PDF loading, parsing, cleaning
│   ├── chunking/         # text chunker
│   ├── embeddings/       # Gemini embedding wrapper
│   ├── retrieval/        # vector search, BM25, hybrid fusion
│   ├── reranking/         # cross-encoder reranker (currently unused, see Roadmap)
│   └── context/           # builds the final cited context block
├── tools/                # web_search, paper_search (arXiv)
└── main.py               # FastAPI app entrypoint

scripts/                 # CLI utilities: ingest_documents, query_pipeline, evaluate_rag
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL with the `pgvector` extension
- A [Gemini API key](https://aistudio.google.com/apikey)
- (Optional) A Firebase project, if you want Google Sign-In

### 1. Clone and install

```bash
git clone 
cd researchmind/backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Postgres with pgvector

```bash
docker run -d --name researchmind-pg \
  -e POSTGRES_USER=researchmind \
  -e POSTGRES_PASSWORD=researchmind \
  -e POSTGRES_DB=researchmind \
  -p 5432:5432 \
  ankane/pgvector
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Fill in `GEMINI_API_KEY` at minimum. See [Environment Variables](#environment-variables) below for the full list.

### 4. Initialize the database

```bash
python -m app.db.init_db
```

Enables the `vector` extension, creates all tables, and builds the vector index.

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

The API is now live at `http://localhost:8000` — check `http://localhost:8000/health`.

```

## Environment Variables

| Variable | Description |
|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_HOST` / `POSTGRES_PORT` / `POSTGRES_DB` | Local Postgres connection (ignored if `DATABASE_URL_OVERRIDE` is set) |
| `DATABASE_URL_OVERRIDE` | Single connection string for managed Postgres (Render, Neon, Supabase, etc.) — takes priority over the individual fields above |
| `DB_SSL_REQUIRED` | Set `true` for managed Postgres hosts that require SSL |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins for CORS (defaults to `*`) |
| `EMBEDDING_MODEL` | Gemini embedding model, e.g. `gemini-embedding-001` |
| `VECTOR_DIM` | Embedding output dimension — must match your pgvector column and `output_dimensionality` used at embed time |
| `GEMINI_API_KEY` | Your Gemini API key |
| `GEMINI_MODEL` | Gemini model used for generation/vision, e.g. `gemini-2.5-flash` |
| `JWT_SECRET_KEY` | Secret used to sign session tokens — **set a long random value in production** |
| `JWT_ALGORITHM` | Defaults to `HS256` |
| `JWT_EXPIRE_MINUTES` | Session token lifetime |
| `FIREBASE_CREDENTIALS_PATH` | Path to your Firebase service-account JSON (only needed for Google Sign-In) |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Text chunking parameters |
| `VECTOR_TOP_K` / `BM25_TOP_K` / `HYBRID_TOP_K` / `RRF_K` | Retrieval tuning parameters |



## API Reference

All routes are prefixed as shown; `/chat/query` streams its response.

### Auth (`/auth`)
| Method | Route | Description |
|---|---|---|
| POST | `/auth/signup` | Create an account (email/password) |
| POST | `/auth/login` | Log in, returns a JWT |
| POST | `/auth/google` | Exchange a Firebase Google ID token for a session JWT |
| GET | `/auth/me` | Current user info |
| DELETE | `/auth/me` | Delete the current account |

### Documents (`/documents`)
| Method | Route | Description |
|---|---|---|
| POST | `/documents/upload` | Upload a PDF — parsed, chunked, embedded, and indexed (text + tables + images + charts) |

### Chats (`/chats`)
| Method | Route | Description |
|---|---|---|
| POST | `/chats` | Create a new chat |
| GET | `/chats` | List the user's chats |
| GET | `/chats/{chat_id}` | Get a chat with full message history |
| DELETE | `/chats/{chat_id}` | Delete a chat |

### Query (`/chat`)
| Method | Route | Description |
|---|---|---|
| POST | `/chat/query` | Ask a question in a chat — routes through the agent graph and streams a cited answer |

All routes except `/auth/*` and `/health` require a bearer token from login.

## Deployment

This project is set up to run as two independently deployed pieces:

- **Backend** → Render (or any host running a long-lived FastAPI process): `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Frontend** → Vercel 



## Design Notes

- **Embeddings run through the Gemini API, not a local model.** An earlier version used `sentence-transformers` (BGE models) locally, which pulls in `torch` — 300–500MB+ of RAM just from the import, before any model weights load. That's more headroom than small deploy targets (e.g. Render's 512MB tier) have to spare. Calling Gemini's `embed_content` instead keeps the whole service lightweight, at the cost of an API round-trip per embed call.
- **Reduced-dimension embeddings are L2-normalized manually.** Gemini's embedding model supports Matryoshka-style output truncation via `output_dimensionality`, but doesn't auto-normalize truncated vectors — since cosine similarity (and pgvector's `<=>` operator) assumes unit vectors, `text_embeddings.py` normalizes after every call.
- **Multimodal content shares the text pipeline.** Rather than a separate retrieval path for images/tables/charts, they're converted into `TextChunk` objects with a `content_type` tag (`"chart"`, `"table"`, etc.) and flow through the exact same embed → store → hybrid-search → cite pipeline as regular text.
- **The agent graph is built per-request**, not once at import time — the retriever node needs a request-scoped DB session and user ID, so `build_graph(session, user_id)` is called fresh for each query rather than shared as a singleton.
