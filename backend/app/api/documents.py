"""
Document upload endpoint.

Reuses the exact same ingestion pipeline as scripts/ingest_documents.py
(loader -> parser -> cleaner -> chunker -> embedder -> DB), just driven
by an uploaded file instead of a directory scan, and scoped to the
authenticated user.

Duplicate uploads are detected via a SHA-256 hash of the raw bytes
*before* any parsing/embedding happens -- scoped per-user (the same
PDF uploaded by two different users is not a duplicate; the DB
enforces this via a (user_id, content_hash) unique constraint). This
avoids paying for Gemini vision calls and embedding compute on
content that user has already indexed.
"""

import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select

from app.api.schemas import DocumentUploadResponse
from app.core.deps import get_current_user
from app.db.database import get_session
from app.db.models import Chunk, Document, User
from app.multimodal.pipeline import extract_multimodal_chunks
from app.rag.chunking.text_chunker import chunk_document
from app.rag.embeddings.text_embeddings import get_embedder
from app.rag.ingestion.cleaner import clean_document
from app.rag.ingestion.loader import load_pdf
from app.rag.ingestion.parser import parse_document
from app.rag.retrieval.bm25 import get_bm25_registry

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_OUTPUT_DIR = "data/processed/images"


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    user_id = current_user.id
    contents = await file.read()
    content_hash = hashlib.sha256(contents).hexdigest()

    # --- Duplicate check, scoped to this user (before any parsing/embedding) ---
    async with get_session() as session:
        existing = await session.scalar(
            select(Document).where(
                Document.user_id == user_id,
                Document.content_hash == content_hash,
            )
        )
        if existing is not None:
            num_chunks_result = await session.execute(
                select(Chunk.id).where(Chunk.document_id == existing.id)
            )
            num_chunks = len(num_chunks_result.all())

            return DocumentUploadResponse(
                document_id=str(existing.id),
                filename=existing.filename,
                num_pages=existing.num_pages or 0,
                num_chunks=num_chunks,
                duplicate=True,
            )

    # Namespace uploaded files by user so two users' identically-named
    # files never collide on disk.
    user_upload_dir = UPLOAD_DIR / str(user_id)
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    dest_path = user_upload_dir / file.filename
    dest_path.write_bytes(contents)

    raw = load_pdf(dest_path)
    parsed = parse_document(raw)
    cleaned = clean_document(parsed)

    document_id = str(uuid.uuid4())
    text_chunks = chunk_document(cleaned, document_id=document_id)

    section_by_page = {p.page_number: p.section for p in cleaned.pages}
    multimodal_chunks = extract_multimodal_chunks(
        file_path=str(dest_path),
        document_id=document_id,
        image_output_dir=f"{IMAGE_OUTPUT_DIR}/{user_id}",
        start_chunk_index=len(text_chunks),
        section_by_page=section_by_page,
    )

    chunks = text_chunks + multimodal_chunks

    if not chunks:
        raise HTTPException(status_code=422, detail="No extractable content found in PDF.")

    embedder = get_embedder()
    texts = [c.content for c in chunks]
    embeddings = embedder.embed_documents(texts)

    async with get_session() as session:
        doc_row = Document(
            id=uuid.UUID(document_id),
            user_id=user_id,
            filename=raw.filename,
            source_path=str(dest_path),
            content_hash=content_hash,
            title=raw.title,
            num_pages=raw.num_pages,
        )
        session.add(doc_row)

        for chunk, embedding in zip(chunks, embeddings):
            session.add(
                Chunk(
                    document_id=uuid.UUID(document_id),
                    user_id=user_id,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    section=chunk.section,
                    content_type=chunk.content_type,
                    embedding=embedding,
                )
            )

        # Flush so the new rows are visible to the SELECT below (same
        # transaction), then refresh this user's BM25 index so the
        # document is immediately searchable without waiting for a restart.
        await session.flush()
        await get_bm25_registry().refresh_for_user(session, str(user_id))

    return DocumentUploadResponse(
        document_id=document_id,
        filename=raw.filename,
        num_pages=raw.num_pages,
        num_chunks=len(chunks),
        duplicate=False,
    )
