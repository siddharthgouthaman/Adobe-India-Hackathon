# extractor/parser.py

import fitz  # PyMuPDF

def parse_pdf(pdf_path):
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
    return all_text_elements, text_size_counts
