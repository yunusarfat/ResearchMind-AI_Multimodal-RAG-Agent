"""
Image understanding.

Turns an extracted figure/photo into a text description via Gemini
vision, so it becomes a normal retrievable chunk (content_type="image").
This is a deliberate design choice: rather than storing raw image
embeddings and doing image-to-image or text-to-image search, we
convert everything to text up front. This keeps retrieval unified
(one embedding space, one hybrid search path) at the cost of losing
some visual nuance a dedicated multimodal embedding model would keep.
"""

from dataclasses import dataclass

from app.core.llm import describe_image
from app.multimodal.images.image_extractor import ExtractedImage

_IMAGE_CAPTION_INSTRUCTION = (
    "Describe this figure from a research paper in 2-4 sentences. "
    "Focus on what it shows (a diagram, architecture, screenshot, "
    "example output, etc.) and any labels or text visible in it. "
    "Be factual and specific — do not speculate beyond what's visible."
)


@dataclass
class ProcessedImage:
    page_number: int
    image_index: int
    image_path: str
    description: str


def process_image(extracted: ExtractedImage) -> ProcessedImage:
    """Generate a text description for one extracted image."""
    description = describe_image(extracted.image_path, _IMAGE_CAPTION_INSTRUCTION)

    return ProcessedImage(
        page_number=extracted.page_number,
        image_index=extracted.image_index,
        image_path=extracted.image_path,
        description=description,
    )


def process_images(extracted_images: list[ExtractedImage]) -> list[ProcessedImage]:
    return [process_image(img) for img in extracted_images]
