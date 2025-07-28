#pdf_type_detector
import re

def detect_pdf_type(text_elements, font_size_counts):
    """
    Detects whether a PDF is poster-like or a structured document.
    - Poster-like: very large font difference, fewer pages
    - Structured: presence of numbered headings, many pages
    """
    if not text_elements:
        return "unknown"

    most_common_font = font_size_counts.most_common(1)[0][0] if font_size_counts else 10.0
    all_font_sizes = [el["font_size"] for el in text_elements]
    max_font_size = max(all_font_sizes) if all_font_sizes else most_common_font
    num_pages = max(el["page"] for el in text_elements) + 1

    # Check for structured PDF clues
    structured_candidates = [
        el for el in text_elements 
        if re.match(r"^\d+(\.\d+)*\s", el["text"].strip())
    ]

    # Poster if: few pages + big font difference and no structured headings
    if (most_common_font < max_font_size * 0.6) and num_pages < 3 and not structured_candidates:
        return "poster"
    return "structured"
