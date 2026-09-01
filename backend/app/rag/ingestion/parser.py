"""
Lightweight structural parsing.

Research PDFs are messy, so we don't try to build a full document
tree. Instead we do a cheap heuristic pass to tag each page with the
most recent "section" heading seen (Abstract, Introduction, Methods,
Results, ...), which becomes useful metadata for citations later.
"""

import re
from dataclasses import dataclass

from app.rag.ingestion.loader import RawDocument

# Common top-level section names in research papers.
_KNOWN_SECTIONS = [
    "abstract", "introduction", "related work", "background",
    "methodology", "methods", "approach", "experiments",
    "results", "discussion", "conclusion", "limitations",
    "future work", "references", "acknowledgements", "appendix",
]

_HEADING_RE = re.compile(
    r"^\s*(?:\d+[\.\)]?\s*)?(" + "|".join(_KNOWN_SECTIONS) + r")\s*$",
    re.IGNORECASE,
)


@dataclass
class ParsedPage:
    page_number: int
    text: str
    section: str | None


@dataclass
class ParsedDocument:
    filename: str
    source_path: str
    title: str | None
    num_pages: int
    pages: list[ParsedPage]


def _detect_section_for_page(page_text: str, current_section: str | None) -> str | None:
    """Scan a page's lines for a recognizable section heading."""
    for line in page_text.splitlines():
        match = _HEADING_RE.match(line.strip())
        if match:
            return match.group(1).title()
    return current_section


def parse_document(raw_doc: RawDocument) -> ParsedDocument:
    """Attach a best-guess `section` label to every page."""
    parsed_pages: list[ParsedPage] = []
    current_section: str | None = None

    for page in raw_doc.pages:
        current_section = _detect_section_for_page(page.text, current_section)
        parsed_pages.append(
            ParsedPage(page_number=page.page_number, text=page.text, section=current_section)
        )

    return ParsedDocument(
        filename=raw_doc.filename,
        source_path=raw_doc.source_path,
        title=raw_doc.title,
        num_pages=raw_doc.num_pages,
        pages=parsed_pages,
    )
