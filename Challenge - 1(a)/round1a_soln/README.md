# Adobe India Hackathon – Round 1(a): PDF Outline Extraction

## 🧩 Problem Statement

Extract a structured **document outline** from PDFs of diverse formats including forms, flyers, brochures, reports, etc. The output should include:
- The **title** of the document.
- A list of headings structured by levels: `H1`, `H2`, `H3`, and `H4`.

---

## 🛠️ Approach

1. **PDF Parsing**:  
   We use [`PyMuPDF`](https://pymupdf.readthedocs.io/) (`fitz`) to read PDF files and extract layout blocks, spans, and font metadata.

2. **Heading Detection**:  
   - Headings are inferred based on **font size**, **boldness flags**, and **text characteristics**.
   - A hierarchical level is assigned (H1–H4) using dynamic font size thresholds.

3. **Text Cleaning**:
   - Removes artifacts like repeated phrases, line numbers, footers, and broken spans.
   - Filters out lines with excessive punctuation, low character count, or known junk fragments.

4. **Title Extraction**:
   - Extracts the largest, most prominent line(s) from the first page using font size and position heuristics.
   - Deduplicates and joins lines if needed.

5. **Parser Logic**:
   - Orchestrates heading and title extraction for each PDF.
   - Writes clean JSON outputs to the `/output` folder.

---

## 🧠 Libraries & Tools Used

- `fitz` (PyMuPDF) – PDF parsing
- `re` – Regular expressions for filtering text
- `os`, `json`, `math` – Native Python modules
- Lightweight Python environment, no GPU or large models needed

---

## 📦 Project Structure
round1a_soln/
├── extractor/
│   ├── heading_extractor.py
│   ├── parser.py
│   ├── pdf_type_detector.py
│   ├── runner.py
│   └── text_cleaner.py
├── input/            # Drop your PDFs here
├── output/           # Extracted output JSONs go here
├── main.py
├── Dockerfile
├── requirements.txt
└── .env

---

## 🐳 Docker Setup

A Dockerfile is provided to make the solution portable and reproducible.

### 🔧 Build the Docker Image

```bash
docker build -t adobe-round1a round1a_soln/

Run the Solution
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  adobe-round1a

### Output Format
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Section Heading",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Subheading",
      "page": 1
    }
  ]
}
