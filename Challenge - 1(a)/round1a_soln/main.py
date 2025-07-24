import os
import json
from pathlib import Path
import fitz  # PyMuPDF
import re
from collections import defaultdict

def extract_outline_from_pdf(pdf_path: Path) -> dict:
    all_text_elements = []
    text_size_counts = {}

    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue
                        font_size = round(span["size"], 2)
                        font_name = span["font"].lower()
                        is_bold = any(w in font_name for w in ["bold", "black", "heavy", "bd"])
                        all_text_elements.append({
                            "text": text,
                            "page": page_num,
                            "font_size": font_size,
                            "x0": round(span["bbox"][0], 2),
                            "y0": round(span["bbox"][1], 2),
                            "is_bold": is_bold
                        })
                        text_size_counts[font_size] = text_size_counts.get(font_size, 0) + 1
    doc.close()

    # --- TITLE EXTRACTION ---
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
    # Remove repeated overlapping OCR words (like "Proposal oposal")
    raw_title = re.sub(r"\b(\w{3,})\b(?:\s+\1\b)+", r"\1", raw_title)
    raw_title = re.sub(r"\s+", " ", raw_title)
    title = raw_title.strip()

    # --- HEADING DETECTION ---
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
        if re.match(r"^[\u2022\-•]$", text):  # skip bullet-only lines
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

    return {"title": title, "outline": outline}


def process_pdfs_in_directory():
    INPUT_DIR = Path("/app/input")
    OUTPUT_DIR = Path("/app/output")
    if not INPUT_DIR.exists():
        print("ERROR: Input directory not found.")
        return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = INPUT_DIR / filename
            output_path = OUTPUT_DIR / filename.replace(".pdf", ".json")
            extracted_data = extract_outline_from_pdf(pdf_path)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    process_pdfs_in_directory()
