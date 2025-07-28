import os
import json
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
from datetime import datetime

# Dynamically resolve paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ensure output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")


def read_persona_json():
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".json"):
            with open(os.path.join(INPUT_DIR, file)) as f:
                print(f"✅ Loaded persona JSON: {file}")
                return json.load(f)
    raise FileNotFoundError("Persona JSON not found in input directory.")


def extract_sections_from_pdfs():
    sections = []
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".pdf"):
            path = os.path.join(INPUT_DIR, file)
            print(f"📄 Processing PDF: {file}")
            doc = fitz.open(path)
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text()
                if len(text.strip()) > 100:
                    sections.append({
                        "document": file,
                        "page_number": page_num,
                        "text": text.strip()
                    })
    print(f"✅ Extracted {len(sections)} sections from PDFs")
    return sections


def rank_sections(sections, query_embedding, top_n=5):
    scores = []
    for sec in sections:
        sec_emb = model.encode(sec["text"], convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(query_embedding, sec_emb).item()
        scores.append((similarity, sec))
    top_sections = sorted(scores, key=lambda x: x[0], reverse=True)[:top_n]
    return [s[1] for s in top_sections]


def build_output(persona, sections):
    timestamp = datetime.now().isoformat()
    extracted_sections = []
    subsection_analysis = []
    for idx, sec in enumerate(sections, start=1):
        extracted_sections.append({
            "document": sec["document"],
            "section_title": sec["text"].split("\n")[0][:100],
            "importance_rank": idx,
            "page_number": sec["page_number"]
        })
        subsection_analysis.append({
            "document": sec["document"],
            "refined_text": sec["text"][:1200],
            "page_number": sec["page_number"]
        })
    return {
        "metadata": {
            "input_documents": [f for f in os.listdir(INPUT_DIR) if f.endswith(".pdf")],
            "persona": persona["persona"],
            "job_to_be_done": persona["job_to_be_done"],
            "processing_timestamp": timestamp
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }


def main():
    persona_data = read_persona_json()
    context_str = f"{persona_data['persona']}. Task: {persona_data['job_to_be_done']}"
    context_emb = model.encode(context_str, convert_to_tensor=True)

    sections = extract_sections_from_pdfs()
    top_sections = rank_sections(sections, context_emb)
    output = build_output(persona_data, top_sections)

    output_path = os.path.join(OUTPUT_DIR, "output.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"✅ Output saved to {output_path}")


if __name__ == '__main__':
    main()
