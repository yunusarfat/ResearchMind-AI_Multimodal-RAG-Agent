"""
FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, chats, documents
from app.core.config import settings

app = FastAPI(title="ResearchMind API", version="0.1.0")

# In dev, ALLOWED_ORIGINS defaults to "*" (permissive). In production,
# set ALLOWED_ORIGINS to your exact frontend URL(s) -- e.g.
# "https://your-app.vercel.app" -- via environment variable.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chats.router)
app.include_router(chat.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
