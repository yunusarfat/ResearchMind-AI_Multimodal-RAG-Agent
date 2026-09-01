"""
Text cleaning.

PDF text extraction produces a lot of noise: hyphenated line breaks,
repeated whitespace, page headers/footers, stray control characters.
This module cleans that up before chunking.
"""

import re

from app.rag.ingestion.parser import ParsedDocument, ParsedPage

_MULTI_SPACE_RE = re.compile(r"[ \t]+")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
_HYPHEN_LINEBREAK_RE = re.compile(r"(\w)-\n(\w)")  # "informa-\ntion" -> "information"
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = _CONTROL_CHARS_RE.sub("", text)
    text = _HYPHEN_LINEBREAK_RE.sub(r"\1\2", text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)

    return text.strip()


def clean_page(page: ParsedPage) -> ParsedPage:
    return ParsedPage(page_number=page.page_number, text=clean_text(page.text), section=page.section)


def clean_document(doc: ParsedDocument) -> ParsedDocument:
    cleaned_pages = [clean_page(p) for p in doc.pages]
    # Drop pages that are empty after cleaning (e.g. pure-image pages with no OCR)
    cleaned_pages = [p for p in cleaned_pages if p.text]
    return ParsedDocument(
        filename=doc.filename,
        source_path=doc.source_path,
        title=doc.title,
        num_pages=doc.num_pages,
        pages=cleaned_pages,
    )
