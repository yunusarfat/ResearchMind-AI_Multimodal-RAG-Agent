"""
Table processing.

Uses pdfplumber to detect and extract tables structurally (rows/columns),
then renders each as a markdown table. Markdown is used as the stored
`content` for table chunks because:
  1. It's compact and embeds reasonably well (row/column structure is
     preserved as text, unlike a flattened paragraph).
  2. LLMs read markdown tables natively when building the final answer,
     so no extra parsing is needed downstream.

Each extracted table becomes its own retrievable chunk with
content_type="table", separate from surrounding body-text chunks.
"""

from dataclasses import dataclass

import pdfplumber


@dataclass
class ExtractedTable:
    page_number: int  # 1-indexed
    table_index: int  # index of this table within the page
    markdown: str
    num_rows: int
    num_cols: int


def _rows_to_markdown(rows: list[list[str | None]]) -> str:
    """Render a list-of-lists table as a GitHub-flavored markdown table."""
    if not rows:
        return ""

    def clean_cell(cell: str | None) -> str:
        if cell is None:
            return ""
        return " ".join(cell.replace("\n", " ").split())

    cleaned_rows = [[clean_cell(c) for c in row] for row in rows]
    header, *body = cleaned_rows

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for row in body:
        # Pad short rows so the markdown table stays well-formed.
        padded = row + [""] * (len(header) - len(row))
        lines.append("| " + " | ".join(padded[: len(header)]) + " |")

    return "\n".join(lines)


def extract_tables_from_pdf(file_path: str) -> list[ExtractedTable]:
    """Extract every table from every page of a PDF."""
    extracted: list[ExtractedTable] = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            for table_index, raw_rows in enumerate(tables):
                if not raw_rows or len(raw_rows) < 2:
                    continue  # skip empty or header-only "tables" (often false positives)

                markdown = _rows_to_markdown(raw_rows)
                if not markdown.strip():
                    continue

                extracted.append(
                    ExtractedTable(
                        page_number=page_number,
                        table_index=table_index,
                        markdown=markdown,
                        num_rows=len(raw_rows),
                        num_cols=len(raw_rows[0]) if raw_rows else 0,
                    )
                )

    return extracted
