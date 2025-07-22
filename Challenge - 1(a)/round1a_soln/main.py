import os
import json
from pathlib import Path
import fitz  # PyMuPDF
from collections import Counter

def extract_outline_from_pdf(pdf_path: Path) -> dict:
    title = "Untitled Document"
    outline = []
    
    all_text_elements = []  # List to hold text metadata
    text_size_counts = Counter()  # Count font sizes for heuristics
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if not text:
                                continue
                            
                            font_size = round(span["size"], 1)
                            x0 = round(span["bbox"][0], 2)
                            y0 = round(span["bbox"][1], 2)  # Top y-coordinate
                            is_bold = "bold" in span["font"].lower()
                            
                            all_text_elements.append({
                                "text": text,
                                "page": page_num + 1,  # Adjust for 1-based paging
                                "font_size": font_size,
                                "x0": x0,
                                "y0": y0,
                                "is_bold": is_bold
                            })
                            text_size_counts[font_size] += 1
        
        doc.close()
        
        if not all_text_elements:
            return {"title": title, "outline": []}
        
        # Step 1: Determine body font size (most common)
        sorted_sizes_by_freq = sorted(text_size_counts.items(), key=lambda item: item[1], reverse=True)
        body_font_size = sorted_sizes_by_freq[0][0] if sorted_sizes_by_freq else 0
        
        # Step 2: Potential heading sizes (larger than body)
        unique_sizes = sorted(set(text_size_counts.keys()), reverse=True)
        potential_heading_sizes = [s for s in unique_sizes if s > body_font_size * 1.05]
        
        # Step 3: Ratio-based heading level map
        heading_level_map = {}
        levels = ["H1", "H2", "H3"]
        if potential_heading_sizes:
            heading_level_map[potential_heading_sizes[0]] = levels[0]
            prev_size = potential_heading_sizes[0]
            current_level = 1
            for size in potential_heading_sizes[1:]:
                if current_level >= len(levels):
                    break
                ratio = size / prev_size
                if ratio < 0.85:  # Significant drop -> next level
                    heading_level_map[size] = levels[current_level]
                    prev_size = size
                    current_level += 1
                else:
                    heading_level_map[size] = levels[current_level - 1]  # Same level
        
        # Step 4: Improved Title Detection (concat multi-line if close)
        page_1_elements = sorted([el for el in all_text_elements if el["page"] == 1],
                                 key=lambda x: (-x["font_size"], x["y0"]))
        title_parts = []
        if page_1_elements:
            candidate = page_1_elements[0]
            if candidate["font_size"] > body_font_size * 1.5:
                title_parts.append(candidate["text"])
                # Check for nearby lines (within 50pt y-diff)
                for el in page_1_elements[1:]:
                    if abs(el["y0"] - candidate["y0"]) < 50 and el["font_size"] == candidate["font_size"]:
                        title_parts.append(el["text"])
                    else:
                        break
                title = " ".join(title_parts).strip()
                # Remove title elements
                all_text_elements = [el for el in all_text_elements if el["text"] not in title_parts or el["page"] != 1]
        
        # Step 5: Collect headings (relaxed filters)
        candidates = []
        for el in all_text_elements:
            if (
                el["font_size"] in heading_level_map
                and (el["is_bold"] or el["font_size"] > body_font_size * 1.2)  # Allow non-bold if large
                and el["x0"] < 150  # Relaxed left-align
                and len(el["text"]) < 150  # Relaxed length
            ):
                level = heading_level_map[el["font_size"]]
                candidates.append({
                    "level": level,
                    "text": el["text"],
                    "page": el["page"]
                })
        
        # Step 6: Deduplicate and sort by page + y0 (top to bottom)
        seen = set()
        unique_outline = []
        for entry in sorted(candidates, key=lambda x: (x["page"], all_text_elements[0]["y0"] if "y0" in all_text_elements[0] else 0)):
            key = (entry["level"], entry["text"], entry["page"])
            if key not in seen:
                unique_outline.append(entry)
                seen.add(key)
        
        return {"title": title, "outline": unique_outline}
    
    except Exception as e:
        return {"title": "Processing Failed", "outline": [], "error": str(e)}

# Main execution for Docker: Process all PDFs in /app/input
INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")

def process_pdfs_in_directory():
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