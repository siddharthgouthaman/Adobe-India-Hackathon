# 🎯 Adobe India Hackathon 2025 – Round 1 Submission

This repository contains the completed solutions for **Round 1** of the **Adobe India Hackathon 2025**, including both sub-challenges:

-  Challenge 1(a): Structured Outline Extraction from Diverse PDFs
-  Challenge 1(b): Semantic Document Section Retrieval based on Persona Context

---

## 📁 Repository Structure
├── Challenge - 1(a)/
│   ├── Datasets/               # Provided input PDFs
│   ├── round1a_soln/           # Complete solution for Challenge 1(a)
│   │   ├── extractor/          # Heading extraction logic
│   │   ├── input/              # Input PDFs
│   │   ├── output/             # Output JSONs
│   │   ├── main.py             # Main script
│   │   ├── Dockerfile          # Docker setup
│   │   └── requirements.txt
│   └── Dockerfile              # Root-level Dockerfile
│
├── Challenge_1b/
│   ├── Collection 1/2/3/       # Provided test input PDFs
│   └── round1_bsoln/           # Complete solution for Challenge 1(b)
│       ├── app/
│       │   ├── input/          # Persona JSON + PDFs
│       │   ├── output/         # Output JSON
│       │   └── main.py
│       ├── approach_explanation.md
│       ├── Dockerfile
│       ├── requirements.txt
│       └── readme.md
│
├── README.md                   # This root README file

---

##  Challenge 1(a): Structured Outline Extraction

**Goal:** Extract a structured table-of-contents-like outline from PDFs, handling diverse formats (flyers, forms, multi-column reports, etc.)

 Solution Location: `Challenge - 1(a)/round1a_soln/`

 Features:
- Lightweight pipeline using `PyMuPDF`, no heavy OCR
- Custom heading hierarchy using font size heuristics
- Cleans noisy or broken text artifacts
- Title aggregation using filtered headers
- Output as JSON in `output/`

📦 Run using Docker:
```bash
cd Challenge\ -\ 1$begin:math:text$a$end:math:text$/round1a_soln
docker build -t adobe_1a .
docker run --rm -v $(pwd):/app adobe_1a


## Challenge 1(b): Context-Aware Section Ranking

**Goal:** Given a persona and job-to-be-done, extract and rank relevant PDF sections semantically.

 **Solution Location:** `Challenge_1b/round1_bsoln/`

🔧 **Features:**
- Uses `sentence-transformers` with `all-MiniLM-L6-v2`
- Persona + Job → context embedding
- Computes cosine similarity between context and all page sections
- Extracts top 5 ranked segments with metadata
- Output: `output/output.json` with structured ranking and section highlights

 **Run using Docker:**
```bash
cd Challenge_1b/round1_bsoln
docker build -t adobe_1b .
docker run --rm -v $(pwd)/app:/app adobe_1b