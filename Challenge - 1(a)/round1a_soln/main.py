# main.py - Using PyMuPDF (Fitz) for PDF parsing

import os
import json
from pathlib import Path
import fitz  # PyMuPDF library
from typing import List, Dict, Any, Tuple
import math

print("DEBUG: Imports successful. (Using PyMuPDF)")

# --- Core PDF Parsing and Outline Extraction Function ---
def extract_outline_from_pdf(pdf_path: Path) -> Dict[str, Any]:
    """
    Extracts the document title and a hierarchical outline (H1, H2, H3)
    with text and page numbers from a given PDF file using PyMuPDF.

    This implementation uses heuristics based on font size, position, and bold status.
    Requires significant refinement for diverse PDF layouts.
    """
    title = "Untitled Document"
    outline_candidates: List[Dict[str, Any]] = []
    
    all_text_elements_with_metadata: List[Dict[str, Any]] = []
    text_size_counts = {} # Now using actual font 'size' from PyMuPDF
    
    # PyMuPDF is generally more robust, so debug_log might be empty, but keep for unhandled cases
    debug_log = [] 

    try:
        doc = fitz.open(pdf_path)
        
        for page_num, page in enumerate(doc):
            page_height = page.rect.height # Get page height for relative y-positioning
            
            # Extract text as a dictionary, which includes blocks, lines, and spans
            # Each span contains text, font, font size, and bbox
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if block["type"] == 0: # This means it's a text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if not text:
                                continue
                            
                            font_size = round(span["size"], 1) # Directly available in PyMuPDF!
                            x0 = round(span["bbox"][0], 2)
                            y0 = round(span["bbox"][1], 2) # PyMuPDF's y0 is top-left of bbox
                            
                            font_name_lower = span["font"].lower()
                            is_bold = "bold" in font_name_lower or "black" in font_name_lower or "demi" in font_name_lower
                            
                            all_text_elements_with_metadata.append({
                                "text": text,
                                "page": page_num + 1,
                                "font_size": font_size, # Directly using font_size now
                                "x0": x0,
                                "y0": y0,
                                "is_bold": is_bold,
                                "fontname": span["font"], # Actual font name
                                "width": round(span["bbox"][2] - span["bbox"][0], 2), # x1 - x0
                                "height": round(span["bbox"][3] - span["bbox"][1], 2) # y1 - y0
                            })
                            text_size_counts[font_size] = text_size_counts.get(font_size, 0) + 1
        
        doc.close()

        # --- Heuristics for Title and Heading Detection (Adjusted for font_size) ---

        if not all_text_elements_with_metadata:
            return {"title": "Empty Document or No Text Elements Processed", "outline": [], "debug_log": debug_log}

        # 1. Determine common font sizes and identify potential heading sizes
        sorted_font_sizes_by_freq = sorted(text_size_counts.items(), key=lambda item: item[1], reverse=True)
        unique_sorted_sizes = sorted(list(text_size_counts.keys()), reverse=True)
        
        body_font_size = sorted_font_sizes_by_freq[0][0] if sorted_font_sizes_by_freq else 0
        if len(sorted_font_sizes_by_freq) > 1 and sorted_font_sizes_by_freq[0][0] > sorted_font_sizes_by_freq[1][0] * 1.5:
             body_font_size = sorted_font_sizes_by_freq[1][0]

        potential_heading_sizes = sorted([s for s in unique_sorted_sizes if s > body_font_size * 1.05], reverse=True)

        heading_level_map: Dict[float, str] = {}
        if len(potential_heading_sizes) >= 1: heading_level_map[potential_heading_sizes[0]] = "H1"
        if len(potential_heading_sizes) >= 2: heading_level_map[potential_heading_sizes[1]] = "H2"
        if len(potential_heading_sizes) >= 3: heading_level_map[potential_heading_sizes[2]] = "H3"
        
        print(f"DEBUG_HEUR: PDF: {pdf_path.name}")
        print(f"DEBUG_HEUR: Font Size Counts: {text_size_counts}")
        print(f"DEBUG_HEUR: Unique Sorted Sizes: {unique_sorted_sizes}")
        print(f"DEBUG_HEUR: Detected Body Font Size: {body_font_size}")
        print(f"DEBUG_HEUR: Potential Heading Sizes: {potential_heading_sizes}")
        print(f"DEBUG_HEUR: Heading Level Map (Size -> Level): {heading_level_map}")


        # 2. Identify Title (using font_size and y0)
        page_1_elements = [el for el in all_text_elements_with_metadata if el["page"] == 1]
        
        if page_1_elements:
            # Sort by font_size (largest first), then y0 (smallest y0 means higher on the page in PDF coords)
            page_1_elements.sort(key=lambda x: (x["font_size"], x["y0"]), reverse=True)
            
            if page_1_elements[0]["font_size"] >= body_font_size * 1.8:
                 title_candidate = page_1_elements[0] # The largest/highest on page 1
                 # A more robust title check: typically large font, centered or left-aligned, near top
                 # You might also check if it's the *only* very large text block at the very top.
                 
                 # Basic title detection
                 title = title_candidate["text"]
                 
                 # Remove title elements from consideration for headings to avoid double-counting
                 all_text_elements_with_metadata = [
                     el for el in all_text_elements_with_metadata 
                     if not (el["text"] == title and el["page"] == 1 and el["font_size"] == title_candidate["font_size"])
                 ]
        
        # 3. Iterate through all text elements to build the outline
        # Sort elements by page then by y0 (ascending, as smaller y0 is higher on page in PyMuPDF's bbox)
        all_text_elements_with_metadata.sort(key=lambda x: (x["page"], x["y0"], x["x0"]))

        current_hierarchy: Dict[str, Any] = {"H1": None, "H2": None, "H3": None}
        
        for element in all_text_elements_with_metadata:
            level = None
            if element["font_size"] in heading_level_map:
                potential_level = heading_level_map[element["font_size"]]
                
                # Heuristics: Check for left alignment and boldness
                # Adjust x0 threshold based on document's typical left margin for headings
                is_left_aligned = element["x0"] < 150 # Refine this based on your PDF!

                # is_bold should be more reliable from PyMuPDF
                if is_left_aligned and element["is_bold"]: 
                    # Logical hierarchy enforcement:
                    if potential_level == "H1":
                        level = "H1"
                        current_hierarchy["H1"] = element
                        current_hierarchy["H2"] = None # Reset lower levels
                        current_hierarchy["H3"] = None
                    elif potential_level == "H2": # H2 must follow H1 or be a top-level H2 (e.g. if H1 is on prior page)
                        # More complex logic here: check if the H2's x0 is to the right of H1's or if no H1 on current page
                        if current_hierarchy["H1"] and element["x0"] > current_hierarchy["H1"]["x0"] - 10: # within tolerance of H1
                            level = "H2"
                        elif not current_hierarchy["H1"] or current_hierarchy["H1"]["page"] != element["page"]: # If no H1 on current page
                             level = "H2" # Assume it's a new H2 section
                        
                        if level == "H2":
                            current_hierarchy["H2"] = element
                            current_hierarchy["H3"] = None # Reset lower level
                    elif potential_level == "H3": # H3 must follow H2
                         if current_hierarchy["H2"] and element["x0"] > current_hierarchy["H2"]["x0"] - 10:
                            level = "H3"
                         elif not current_hierarchy["H2"] or current_hierarchy["H2"]["page"] != element["page"]: # If no H2 on current page
                             level = "H3" # Assume it's a new H3 section
                        
                         if level == "H3":
                            current_hierarchy["H3"] = element
            
            if level:
                outline_candidates.append({
                    "level": level, "text": element["text"], "page": element["page"]
                })
        
        # Final pass to ensure uniqueness and correct order
        unique_outline = []
        seen = set()
        for entry in outline_candidates:
            key = (entry["level"], entry["text"], entry["page"])
            if key not in seen:
                unique_outline.append(entry)
                seen.add(key)
        
        # Final sort by page, then by y-coordinate (higher up means smaller y0)
        # Assuming that the elements in all_text_elements_with_metadata were already sorted.
        # If not, you might need to add y0 to the outline_candidates and sort by (page, y0).
        unique_outline.sort(key=lambda x: (x["page"])) # For now, assuming internal order is mostly correct.

    except Exception as e:
        print(f"ERROR: Unhandled exception in extract_outline_from_pdf for {pdf_path}: {e}")
        return {"title": f"Processing Failed for {pdf_path.name}", "outline": [], "error": str(e), "debug_log": debug_log}

    return {
        "title": title,
        "outline": unique_outline,
        "debug_log": debug_log # Include this in the output for inspection
    }

# --- Main Execution Logic for Competition (Docker Environment) ---
INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")

print("DEBUG: Defining process_pdfs_in_directory function.")

def process_pdfs_in_directory():
    print("DEBUG: Inside process_pdfs_in_directory function.")
    if not INPUT_DIR.exists():
        print(f"ERROR: Input directory {INPUT_DIR} not found. Ensure it's mounted correctly via Docker.")
        exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"DEBUG: Ensuring output directory {OUTPUT_DIR} exists.")

    pdf_files_found = False
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_files_found = True
            pdf_path = INPUT_DIR / filename
            output_filename = filename.replace(".pdf", ".json")
            output_path = OUTPUT_DIR / output_filename

            print(f"DEBUG: Processing PDF: {filename} from {pdf_path}...")
            try:
                extracted_data = extract_outline_from_pdf(pdf_path)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(extracted_data, f, indent=2, ensure_ascii=False)
                print(f"DEBUG: Successfully saved outline for {filename} to {output_path}")
            except Exception as e:
                print(f"ERROR: Failed to process {filename}: {e}")
                error_output = {
                    "title": f"Processing Failed for {filename}",
                    "outline": [],
                    "error_details": str(e),
                    "original_pdf": filename,
                    "debug_log": []
                }
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(error_output, f, indent=2, ensure_ascii=False)

    if not pdf_files_found:
        print(f"DEBUG: No PDF files found in {INPUT_DIR}. Please ensure PDFs are placed in this directory.")
    else:
        print("DEBUG: All specified PDFs processed (or attempted to be processed).")


if __name__ == "__main__":
    print("DEBUG: Script starting (if __name__ == '__main__' block).")
    process_pdfs_in_directory()
    print("DEBUG: Process finished.")