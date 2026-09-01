"""
Document loading.

Responsible only for: finding files on disk and extracting raw,
unprocessed text per page. No cleaning, no chunking — that happens
in later stages (cleaner.py, text_chunker.py).
"""

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class RawPage:
    page_number: int  # 1-indexed
    text: str


@dataclass
class RawDocument:
    filename: str
    source_path: str
    title: str | None
    num_pages: int
    pages: list[RawPage]


def discover_pdf_files(directory: str | Path) -> list[Path]:
    """Return all .pdf files under `directory` (non-recursive by default)."""
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    return sorted(directory.glob("*.pdf"))


def load_pdf(file_path: str | Path) -> RawDocument:
    """Load a single PDF and extract raw text for every page."""
    file_path = Path(file_path)
    reader = PdfReader(str(file_path))

    pages: list[RawPage] = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(RawPage(page_number=i, text=text))

    meta_title = None
    if reader.metadata is not None:
        meta_title = reader.metadata.title

    return RawDocument(
        filename=file_path.name,
        source_path=str(file_path),
        title=meta_title or file_path.stem,
        num_pages=len(pages),
        pages=pages,
    )


def load_pdfs_from_directory(directory: str | Path) -> list[RawDocument]:
    """Convenience wrapper: discover + load every PDF in a directory."""
    files = discover_pdf_files(directory)
    return [load_pdf(f) for f in files]
