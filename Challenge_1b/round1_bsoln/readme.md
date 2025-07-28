# 📄 Adobe Hackathon Round 1(b) – Semantic Document Retrieval

This repository contains the solution for **Challenge 1(b)** of the Adobe India Hackathon. The goal is to extract and rank the most relevant PDF sections given a **persona** and a **job-to-be-done** context.

---

## 🗂️ Project Structure
round1_bsoln/
├── app/
│   ├── input/                  # Contains PDFs and persona JSON
│   ├── output/                 # Generated output.json written here
│   └── main.py                 # Entry-point script
│
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition
└── readme.md                   # This file

## ⚙️ Approach Summary

The solution works by:

1. Parsing PDFs in the `input/` directory using **PyMuPDF (fitz)**
2. Generating a combined **context string** using `persona` and `job_to_be_done` from the provided JSON
3. Encoding both context and all extracted PDF page sections using **`all-MiniLM-L6-v2`** from `sentence-transformers`
4. Ranking top relevant sections using cosine similarity
5. Returning a structured output in `output/output.json`

---

## 📥 Input Requirements

Place the following in the `app/input/` directory:

- 3 to 10 `.pdf` files (semantic source documents)
- A single `persona.json` file, with the following structure:

```json
{
  "persona": "Procurement manager at a government organization",
  "job_to_be_done": "Wants to evaluate if document suits procurement regulation guidelines"
}

OUTPUT
{
  "metadata": {
    "input_documents": ["file1.pdf", "file2.pdf"],
    "persona": "...",
    "job_to_be_done": "...",
    "processing_timestamp": "..."
  },
  "extracted_sections": [
    {
      "document": "file1.pdf",
      "section_title": "Introduction to Procurement",
      "importance_rank": 1,
      "page_number": 2
    }
  ],
  "subsection_analysis": [
    {
      "document": "file1.pdf",
      "refined_text": "Full relevant section text...",
      "page_number": 2
    }
  ]
}
{
  "metadata": {
    "input_documents": ["file1.pdf", "file2.pdf"],
    "persona": "...",
    "job_to_be_done": "...",
    "processing_timestamp": "..."
  },
  "extracted_sections": [
    {
      "document": "file1.pdf",
      "section_title": "Introduction to Procurement",
      "importance_rank": 1,
      "page_number": 2
    }
  ],
  "subsection_analysis": [
    {
      "document": "file1.pdf",
      "refined_text": "Full relevant section text...",
      "page_number": 2
    }
  ]
}
##{
  "metadata": {
    "input_documents": ["file1.pdf", "file2.pdf"],
    "persona": "...",
    "job_to_be_done": "...",
    "processing_timestamp": "..."
  },
  "extracted_sections": [
    {
      "document": "file1.pdf",
      "section_title": "Introduction to Procurement",
      "importance_rank": 1,
      "page_number": 2
    }
  ],
  "subsection_analysis": [
    {
      "document": "file1.pdf",
      "refined_text": "Full relevant section text...",
      "page_number": 2
    }
  ]
}
##{
  "metadata": {
    "input_documents": ["file1.pdf", "file2.pdf"],
    "persona": "...",
    "job_to_be_done": "...",
    "processing_timestamp": "..."
  },
  "extracted_sections": [
    {
      "document": "file1.pdf",
      "section_title": "Introduction to Procurement",
      "importance_rank": 1,
      "page_number": 2
    }
  ],
  "subsection_analysis": [
    {
      "document": "file1.pdf",
      "refined_text": "Full relevant section text...",
      "page_number": 2
    }
  ]
}{
  "metadata": {
    "input_documents": ["file1.pdf", "file2.pdf"],
    "persona": "...",
    "job_to_be_done": "...",
    "processing_timestamp": "..."
  },
  "extracted_sections": [
    {
      "document": "file1.pdf",
      "section_title": "Introduction to Procurement",
      "importance_rank": 1,
      "page_number": 2
    }
  ],
  "subsection_analysis": [
    {
      "document": "file1.pdf",
      "refined_text": "Full relevant section text...",
      "page_number": 2
    }
  ]
}
###Build the Docker Page
docker build -t adobe_round1b .


### Run the Container
docker run --rm -v $PWD/app:/app adobe_round1b

All dependencies are listed in requirements.txt:
fitz  # via PyMuPDF
sentence-transformers
torch



