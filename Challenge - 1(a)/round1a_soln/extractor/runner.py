# extractor/runner.py
import json
import logging
from pathlib import Path
from extractor.heading_extractor import extract_title_and_outline

logger = logging.getLogger(__name__)

def process_pdfs_in_directory(input_dir="input", output_dir="output"):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    input_path.mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)

    for pdf_file in input_path.glob("*.pdf"):
        try:
            logger.info(f"Processing: {pdf_file.name}")
            result = extract_title_and_outline(pdf_file)
            out_file = output_path / (pdf_file.stem + ".json")
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            logger.info(f"✅ Saved output to {out_file}")
        except Exception as e:
            logger.error(f"❌ Failed to process {pdf_file.name}: {e}")
