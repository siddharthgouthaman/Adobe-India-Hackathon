from pathlib import Path
from pdfminer.high_level import extract_text

# This line makes your script location-independent
pdf_path = Path(__file__).parent / "Datasets" / "Pdfs" / "E0H1CM114.pdf"

text = extract_text(str(pdf_path))
print(text[:])