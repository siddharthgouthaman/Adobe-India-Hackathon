# extractor/heading_extractor.py

import re
from collections import defaultdict

def extract_headings(all_text_elements, text_size_counts):
    body_font_size = max(text_size_counts, key=text_size_counts.get) if text_size_counts else 10.0
    unique_sizes = sorted(set(text_size_counts.keys()), reverse=True)
    heading_sizes = [sz for sz in unique_sizes if sz > body_font_size * 1.05]
    heading_level_map = {sz: f"H{min(i+1, 5)}" for i, sz in enumerate(heading_sizes)}

    candidates = []
    combined_lines = defaultdict(str)

    for el in all_text_elements:
        text = el["text"].strip()
        if not text or len(text) < 3:
            continue
        if len(text.split()) > 18:
            continue
        if re.match(r"^[\u2022\-•]$", text):
            continue

        is_heading = (
            (el["font_size"] in heading_level_map and el["x0"] < 150) or
            (el["is_bold"] and el["font_size"] > body_font_size and el["x0"] < 150)
        )

        if is_heading:
            key = (el["page"], round(el["y0"]))
            combined_lines[key] += (" " + text if combined_lines[key] else text)

    outline = []
    seen = set()
    for (page, y), text in sorted(combined_lines.items()):
        clean_text = text.strip()
        if not clean_text or len(clean_text) < 3:
            continue
        if clean_text.lower() in {"rfp", "to", "for"}:
            continue
        if re.match(r"^\d+\.\d+", clean_text):
            level = "H3"
        elif re.match(r"^\d+\.", clean_text):
            level = "H1"
        elif re.match(r"^appendix [a-z]:", clean_text.lower()):
            level = "H2"
        elif clean_text.endswith(":"):
            level = "H3"
        elif any(word in clean_text.lower() for word in ["summary", "background", "milestones"]):
            level = "H2"
        else:
            level = "H2"

        key = (level, clean_text.lower(), page)
        if key not in seen:
            outline.append({"level": level, "text": clean_text + " ", "page": page})
            seen.add(key)

    return outline
