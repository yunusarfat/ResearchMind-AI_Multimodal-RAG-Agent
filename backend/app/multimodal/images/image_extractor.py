"""
Image extraction from PDFs.

Uses PyMuPDF (fitz) to pull out embedded raster images page by page.
This is shared by both the "image" and "chart" processors — the only
difference between the two is how the extracted image is *described*
(image_processor.py vs chart_processor.py), not how it's extracted.

Note: this captures embedded raster images (photos, screenshots,
rendered plots saved as images) but will NOT catch vector-drawn
charts/diagrams that some tools generate directly as PDF vector
graphics rather than embedded bitmaps. Handling that would require
rendering full pages to images and running layout detection — a
reasonable v2 improvement, out of scope for this pass.
"""

from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF


@dataclass
class ExtractedImage:
    page_number: int  # 1-indexed
    image_index: int  # index of this image within the page
    image_path: str  # where the extracted image was saved on disk
    width: int
    height: int


def extract_images_from_pdf(
    file_path: str,
    output_dir: str,
    min_width: int = 100,
    min_height: int = 100,
) -> list[ExtractedImage]:
    """
    Extract every embedded image from a PDF, saving each to `output_dir`.

    min_width/min_height filter out tiny images (logos, icons, bullet
    graphics) that aren't meaningful figures/charts.
    """
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(file_path)
    stem = Path(file_path).stem
    extracted: list[ExtractedImage] = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        image_list = page.get_images(full=True)

        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            width, height = base_image.get("width", 0), base_image.get("height", 0)

            if width < min_width or height < min_height:
                continue

            ext = base_image.get("ext", "png")
            out_path = output_dir_path / f"{stem}_p{page_number + 1}_img{image_index}.{ext}"
            out_path.write_bytes(base_image["image"])

            extracted.append(
                ExtractedImage(
                    page_number=page_number + 1,
                    image_index=image_index,
                    image_path=str(out_path),
                    width=width,
                    height=height,
                )
            )

    doc.close()
    return extracted
