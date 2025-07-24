# extractor/runner.py

import os
import json
from pathlib import Path
from extractor.parser import parse_pdf
from extractor.title_extractor import extract_title
from extractor.heading_extractor import extract_headings

def extract_outline_from_pdf(pdf_path: Path) -> dict:
    all_text_elements, text_size_counts = parse_pdf(pdf_path)
    title = extract_title(all_text_elements)
    outline = extract_headings(all_text_elements, text_size_counts)
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
