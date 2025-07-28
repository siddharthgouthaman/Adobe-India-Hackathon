from collections import defaultdict
import re
from .parser import extract_text_elements
from .text_cleaner import clean_text
from .pdf_type_detector import detect_pdf_type


def extract_title_and_outline(pdf_path):
    text_elements, font_size_counts = extract_text_elements(pdf_path)

    if not text_elements:
        return {"title": "Empty Document", "outline": []}

    pdf_type = detect_pdf_type(text_elements, font_size_counts)

    if pdf_type == "poster":
        return _extract_poster_style(text_elements, font_size_counts)
    else:
        return _extract_structured_style(text_elements, font_size_counts)


def _extract_poster_style(text_elements, font_size_counts):
    """Poster-style PDFs: pick largest heading as title."""
    most_common_font = font_size_counts.most_common(1)[0][0]
    all_font_sizes = [el["font_size"] for el in text_elements]
    max_font_size = max(all_font_sizes)

    lines_by_page = defaultdict(lambda: defaultdict(list))
    for el in text_elements:
        y_group = round(el["y0"] / 2) * 2
        lines_by_page[el["page"]][y_group].append(el)

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

    title = ""
    if outline:
        best_heading = max(outline, key=lambda x: x["size"])
        title = best_heading["text"]
        outline = []

    return {"title": title, "outline": outline}


def _extract_structured_style(text_elements, font_size_counts):
    """Structured PDFs: hierarchical H1/H2 extraction with form-specific rules."""
    first_page_elements = [el for el in text_elements if el["page"] == 0]
    sorted_by_font = sorted(first_page_elements, key=lambda e: (-e["font_size"], e["y0"]))

    title = ""
    if sorted_by_font:
        title = clean_text(sorted_by_font[0]["text"])

        # --- 🛠️ Form-specific title lock ---
        if "form" not in title.lower() and len(sorted_by_font) > 1:
            if (
                abs(sorted_by_font[1]["y0"] - sorted_by_font[0]["y0"]) < 40 and
                abs(sorted_by_font[1]["font_size"] - sorted_by_font[0]["font_size"]) < 2
            ):
                title += " " + clean_text(sorted_by_font[1]["text"])

    outline = []
    seen = set()
    body_font_size = font_size_counts.most_common(1)[0][0] if font_size_counts else 10.0

    for el in text_elements:
        txt = clean_text(el["text"])
        if not txt:
            continue

        # --- 🛠️ Empty heading filters ---
        if re.match(r"^0\.\d+$", txt.strip()):       # Version numbers
            continue
        if re.match(r"^\d+\.$", txt.strip()):        # Single number
            continue
        if re.match(r"^\d+(\.\d+)+$", txt.strip()):  # Pure section number
            continue
        if len(txt.split()) > 10:                    # Likely paragraph
            continue

        # --- Heading level detection ---
        if re.match(r"^\d+\.\d+", txt):              # H2
            level = "H2"
        elif re.match(r"^\d+\.", txt):               # H1
            level = "H1"
        else:
            if (
                el["font_size"] >= body_font_size * 1.3 and
                len(txt.split()) <= 6 and
                el["page"] > 1
            ):
                level = "H1"
            else:
                continue

        # --- 🛠️ Form lock for headings ---
        if "form" in title.lower() and level not in ["H1", "H2"]:
            continue

        key = (txt.lower(), el["page"])
        if key not in seen:
            outline.append({
                "level": level,
                "text": txt,
                "page": el["page"]
            })
            seen.add(key)

    return {"title": title, "outline": outline}
