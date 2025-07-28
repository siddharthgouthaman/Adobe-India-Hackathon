#parser.py
import fitz  # PyMuPDF
from collections import Counter

def extract_text_elements(pdf_path):
    doc = fitz.open(pdf_path)
    text_elements = []
    font_size_counts = Counter()

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict").get("blocks", [])
        for block in blocks:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    font_size = round(span.get("size", 10.0), 2)
                    font_name = span.get("font", "").lower()
                    is_bold = any(w in font_name for w in ["bold", "black", "heavy", "bd"])
                    text_elements.append({
                        "text": text,
                        "page": page_num,
                        "font_size": font_size,
                        "x0": round(span["bbox"][0], 2),
                        "y0": round(span["bbox"][1], 2),
                        "is_bold": is_bold
                    })
                    font_size_counts[font_size] += 1
    doc.close()
    return text_elements, font_size_counts
