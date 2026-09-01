"""
Chart understanding.

Charts need different treatment than generic figures: a caption like
"a bar chart is shown" is useless for answering "what trend does
Figure 4 show?" — we need the actual axes, categories, and trend
direction pulled out as text.

To avoid paying for two separate Gemini vision calls per extracted
image (one to classify "is this a chart", one to describe it), this
module does both in a single call: the model first states the type,
then either gives a full trend/value extraction (if it's a chart) or
a short generic caption (if it's not). The ingestion pipeline uses
`is_chart` to decide which content_type to store the chunk under —
so a non-chart image extracted here doesn't need a second call to
image_processor.py.
"""

from dataclasses import dataclass

from app.core.llm import describe_image
from app.multimodal.images.image_extractor import ExtractedImage

_CHART_INSTRUCTION = (
    "Look at this image from a research paper and respond in exactly this format:\n\n"
    "TYPE: <chart or image>\n"
    "DESCRIPTION: <description>\n\n"
    "If TYPE is 'chart' (bar chart, line chart, scatter plot, etc.), the "
    "DESCRIPTION must extract: what is plotted on each axis, the "
    "categories/series shown, the overall trend, and any standout values "
    "(e.g. 'Model A reaches the highest F1 score of 0.91 at epoch 10'). "
    "Be precise about numbers you can actually read.\n"
    "If TYPE is 'image' (a diagram, screenshot, photo, or anything that "
    "isn't primarily a data chart), the DESCRIPTION should be a brief "
    "2-3 sentence caption instead."
)


@dataclass
class ProcessedChart:
    page_number: int
    image_index: int
    image_path: str
    is_chart: bool
    description: str


def _parse_response(raw_text: str) -> tuple[bool, str]:
    """Parse the TYPE:/DESCRIPTION: formatted response. Falls back to
    treating the whole response as a description if parsing fails."""
    is_chart = False
    description = raw_text.strip()

    lines = raw_text.strip().splitlines()
    if lines and lines[0].upper().startswith("TYPE:"):
        type_value = lines[0].split(":", 1)[1].strip().lower()
        is_chart = type_value == "chart"

        remaining = "\n".join(lines[1:]).strip()
        if remaining.upper().startswith("DESCRIPTION:"):
            description = remaining.split(":", 1)[1].strip()
        else:
            description = remaining

    return is_chart, description


def process_chart(extracted: ExtractedImage) -> ProcessedChart:
    """Classify + describe one extracted image in a single Gemini call."""
    raw_response = describe_image(extracted.image_path, _CHART_INSTRUCTION)
    is_chart, description = _parse_response(raw_response)

    return ProcessedChart(
        page_number=extracted.page_number,
        image_index=extracted.image_index,
        image_path=extracted.image_path,
        is_chart=is_chart,
        description=description,
    )


def process_charts(extracted_images: list[ExtractedImage]) -> list[ProcessedChart]:
    return [process_chart(img) for img in extracted_images]
