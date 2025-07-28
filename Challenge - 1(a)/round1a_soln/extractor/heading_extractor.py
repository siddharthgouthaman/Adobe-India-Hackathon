#heading_extractor.py
from collections import defaultdict
import re
from .parser import extract_text_elements
from .text_cleaner import clean_text

def extract_title_and_outline(pdf_path):
    text_elements, font_size_counts = extract_text_elements(pdf_path)

    if not text_elements:
        return {"title": "Empty Document", "outline": []}

    most_common_font = font_size_counts.most_common(1)[0][0] if font_size_counts else 10.0
    all_font_sizes = [el["font_size"] for el in text_elements]
    max_font_size = max(all_font_sizes) if all_font_sizes else most_common_font
    num_pages = max(el["page"] for el in text_elements) + 1

    is_poster_like = (most_common_font < max_font_size * 0.6) and num_pages < 3

    lines_by_page = defaultdict(lambda: defaultdict(list))
    for el in text_elements:
        page = el["page"]
        y_group = round(el["y0"] / 2) * 2
        lines_by_page[page][y_group].append(el)

    outline = []
    seen = set()
    heading_threshold = max_font_size * 0.80

    for page in sorted(lines_by_page.keys()):
        for y in sorted(lines_by_page[page]):
            spans = sorted(lines_by_page[page][y], key=lambda e: e["x0"])
            combined_text = clean_text(" ".join(span["text"] for span in spans))

            if not combined_text or len(combined_text) < 3:
                continue
            if combined_text.strip().endswith(':'):
                continue
            if not re.search(r'[a-zA-Z]{3,}', combined_text):
                continue

            avg_font_size = sum(s["font_size"] for s in spans) / len(spans)
            is_bold = any(s["is_bold"] for s in spans)

            is_heading = (
                avg_font_size >= heading_threshold or
                (is_bold and avg_font_size > most_common_font * 1.25)
            )

            if is_heading:
                key = (combined_text.lower(), page)
                if key not in seen:
                    outline.append({
                        "level": "H1",
                        "text": combined_text,
                        "page": page,
                        "size": avg_font_size
                    })
                    seen.add(key)

    if is_poster_like and outline:
        best_heading = max(outline, key=lambda x: x["size"])
        outline = [best_heading]

    for item in outline:
        del item["size"]

    return {"title": "", "outline": outline}
