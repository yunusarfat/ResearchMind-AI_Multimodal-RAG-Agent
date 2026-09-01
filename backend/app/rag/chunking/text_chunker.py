"""
Text chunking.

Splits cleaned page text into overlapping chunks suitable for
embedding. Uses a recursive splitting strategy: try to split on
paragraph breaks first, then sentences, then hard character limits,
so chunks stay semantically coherent instead of cutting mid-sentence
whenever possible.

Each chunk keeps a reference to the page number and section it came
from — this is what allows citations later ("Page 8, Table 3").
"""

from dataclasses import dataclass

from app.core.config import settings
from app.rag.ingestion.parser import ParsedDocument

_SEPARATORS = ["\n\n", "\n", ". ", " "]


@dataclass
class TextChunk:
    document_id: str
    content: str
    chunk_index: int
    page_number: int | None
    section: str | None
    content_type: str = "text"


def _split_recursive(text: str, chunk_size: int, separators: list[str]) -> list[str]:
    """Recursively split `text` using the first separator that yields
    pieces small enough to fit chunk_size, falling back to hard slicing."""
    if len(text) <= chunk_size:
        return [text]

    if not separators:
        # Hard fallback: slice by character count.
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    sep, remaining_seps = separators[0], separators[1:]
    parts = text.split(sep)

    chunks: list[str] = []
    current = ""
    for part in parts:
        candidate = (current + sep + part) if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(part) > chunk_size:
                chunks.extend(_split_recursive(part, chunk_size, remaining_seps))
                current = ""
            else:
                current = part
    if current:
        chunks.append(current)

    return chunks


def _add_overlap(chunks: list[str], overlap: int) -> list[str]:
    """Prefix each chunk (after the first) with the tail of the previous
    chunk so retrieval doesn't lose context at chunk boundaries."""
    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    overlapped = [chunks[0]]
    for i in range(1, len(chunks)):
        prev_tail = chunks[i - 1][-overlap:]
        overlapped.append(prev_tail + " " + chunks[i])
    return overlapped


def chunk_document(
    doc: ParsedDocument,
    document_id: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[TextChunk]:
    """Chunk every page of a document, preserving page/section metadata."""
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    all_chunks: list[TextChunk] = []
    global_idx = 0

    for page in doc.pages:
        raw_pieces = _split_recursive(page.text, chunk_size, _SEPARATORS)
        pieces = _add_overlap(raw_pieces, chunk_overlap)

        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue
            all_chunks.append(
                TextChunk(
                    document_id=document_id,
                    content=piece,
                    chunk_index=global_idx,
                    page_number=page.page_number,
                    section=page.section,
                )
            )
            global_idx += 1

    return all_chunks
