# extractor/title_extractor.py

import re
from collections import defaultdict

def extract_title(all_text_elements):
    page1 = [el for el in all_text_elements if el["page"] == 0]
    title_lines = defaultdict(list)
    max_font = max(el["font_size"] for el in page1) if page1 else 0

    for el in page1:
        if abs(el["font_size"] - max_font) < 0.5:
            y = round(el["y0"])
            title_lines[y].append(el)

    full_title_parts = []
    for y in sorted(title_lines.keys()):
        line_spans = sorted(title_lines[y], key=lambda e: e["x0"])
        line_text = " ".join(span["text"] for span in line_spans)
        full_title_parts.append(line_text)

    raw_title = "  ".join(full_title_parts)
    raw_title = re.sub(r"\b(\w{3,})\b(?:\s+\1\b)+", r"\1", raw_title)
    raw_title = re.sub(r"\s+", " ", raw_title)
    return raw_title.strip()
