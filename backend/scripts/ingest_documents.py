"""
Ingest every PDF in a directory: load -> parse -> clean -> chunk ->
embed -> store in Postgres/pgvector, scoped to a specific user account.

Since every Document/Chunk now belongs to a user (see app/db/models.py),
this script requires an existing account's email -- sign up via
POST /auth/signup (or the frontend) first, then run:

    python -m scripts.ingest_documents data/uploads --email you@example.com
"""

import argparse
import asyncio
import hashlib
import uuid
from pathlib import Path

from sqlalchemy import select
from tqdm import tqdm

from app.db.database import get_session
from app.db.models import Chunk, Document, User
from app.multimodal.pipeline import extract_multimodal_chunks
from app.rag.chunking.text_chunker import chunk_document
from app.rag.embeddings.text_embeddings import get_embedder
from app.rag.ingestion.cleaner import clean_document
from app.rag.ingestion.loader import discover_pdf_files, load_pdf
from app.rag.ingestion.parser import parse_document
from app.rag.retrieval.bm25 import get_bm25_registry

IMAGE_OUTPUT_DIR = "data/processed/images"


async def get_user_id_by_email(email: str) -> str:
    async with get_session() as session:
        user = await session.scalar(select(User).where(User.email == email))

    if user is None:
        raise SystemExit(
            f"No account found for '{email}'. Sign up first via POST /auth/signup "
            f"(see /docs), then re-run this script with that email."
        )
    return str(user.id)


async def ingest_file(file_path, user_id: str) -> int:
    """Ingest a single PDF (text + tables + images/charts) for one user.
    Returns number of chunks stored (0 if skipped as a duplicate or empty)."""
    content_hash = hashlib.sha256(Path(file_path).read_bytes()).hexdigest()

    async with get_session() as session:
        existing = await session.scalar(
            select(Document).where(
                Document.user_id == user_id,
                Document.content_hash == content_hash,
            )
        )
        if existing is not None:
            print(f"  ⏭️  {Path(file_path).name} already ingested for this user "
                  f"(matches existing document {existing.id}), skipping.")
            return 0

    raw = load_pdf(file_path)
    parsed = parse_document(raw)
    cleaned = clean_document(parsed)

    document_id = str(uuid.uuid4())
    text_chunks = chunk_document(cleaned, document_id=document_id)

    section_by_page = {p.page_number: p.section for p in cleaned.pages}
    multimodal_chunks = extract_multimodal_chunks(
        file_path=str(file_path),
        document_id=document_id,
        image_output_dir=f"{IMAGE_OUTPUT_DIR}/{user_id}",
        start_chunk_index=len(text_chunks),
        section_by_page=section_by_page,
    )

    chunks = text_chunks + multimodal_chunks

    if not chunks:
        print(f"  ⚠️  No extractable content in {raw.filename}, skipping.")
        return 0

    embedder = get_embedder()
    texts = [c.content for c in chunks]
    embeddings = embedder.embed_documents(texts)

    async with get_session() as session:
        doc_row = Document(
            id=uuid.UUID(document_id),
            user_id=uuid.UUID(user_id),
            filename=raw.filename,
            source_path=raw.source_path,
            content_hash=content_hash,
            title=raw.title,
            num_pages=raw.num_pages,
        )
        session.add(doc_row)

        for chunk, embedding in zip(chunks, embeddings):
            session.add(
                Chunk(
                    document_id=uuid.UUID(document_id),
                    user_id=uuid.UUID(user_id),
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    section=chunk.section,
                    content_type=chunk.content_type,
                    embedding=embedding,
                )
            )

        await session.flush()
        await get_bm25_registry().refresh_for_user(session, user_id)

    return len(chunks)


async def main(directory: str, email: str) -> None:
    user_id = await get_user_id_by_email(email)

    files = discover_pdf_files(directory)
    if not files:
        print(f"No PDF files found in {directory}")
        return

    print(f"Found {len(files)} PDF(s) in {directory} — ingesting for {email}\n")

    total_chunks = 0
    for file_path in tqdm(files, desc="Ingesting"):
        n = await ingest_file(file_path, user_id)
        total_chunks += n

    print(f"\n✅ Ingested {len(files)} document(s), {total_chunks} chunk(s) total.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest PDFs into ResearchMind's RAG store for one user.")
    parser.add_argument("directory", help="Directory containing PDF files")
    parser.add_argument("--email", required=True, help="Email of the existing account to ingest into")
    args = parser.parse_args()

    asyncio.run(main(args.directory, args.email))
