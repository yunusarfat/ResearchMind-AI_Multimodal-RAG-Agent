"""
Multimodal ingestion pipeline.

Orchestrates table extraction + image/chart extraction+description for
a single PDF, producing TextChunk objects that plug directly into the
same embedding/storage path as regular text chunks (app/rag/chunking).
This is what lets multimodal content ride the exact same hybrid
search + reranking + citation pipeline as text — a chart description
is just a chunk with content_type="chart".
"""

from app.multimodal.charts.chart_processor import process_chart
from app.multimodal.images.image_extractor import extract_images_from_pdf
from app.multimodal.tables.table_processor import extract_tables_from_pdf
from app.rag.chunking.text_chunker import TextChunk


def extract_multimodal_chunks(
    file_path: str,
    document_id: str,
    image_output_dir: str,
    start_chunk_index: int = 0,
    section_by_page: dict[int, str] | None = None,
) -> list[TextChunk]:
    """
    Extract tables, images, and charts from a PDF and return them as
    TextChunk objects ready for embedding.

    `start_chunk_index` should be set to len(existing_text_chunks) so
    chunk_index stays unique/ordered across text + multimodal content.
    `section_by_page` (page_number -> section name) is optional; when
    provided, multimodal chunks inherit the section their page belongs to.
    """
    section_by_page = section_by_page or {}
    chunks: list[TextChunk] = []
    idx = start_chunk_index

    # --- Tables ---
    for table in extract_tables_from_pdf(file_path):
        chunks.append(
            TextChunk(
                document_id=document_id,
                content=table.markdown,
                chunk_index=idx,
                page_number=table.page_number,
                section=section_by_page.get(table.page_number),
                content_type="table",
            )
        )
        idx += 1

    # --- Images & Charts ---
    extracted_images = extract_images_from_pdf(file_path, output_dir=image_output_dir)
    for image in extracted_images:
        result = process_chart(image)  # classifies + describes in one call
        if not result.description:
            continue  # skip images Gemini couldn't describe (e.g. corrupt/unsupported)

        chunks.append(
            TextChunk(
                document_id=document_id,
                content=result.description,
                chunk_index=idx,
                page_number=result.page_number,
                section=section_by_page.get(result.page_number),
                content_type="chart" if result.is_chart else "image",
            )
        )
        idx += 1

    return chunks
