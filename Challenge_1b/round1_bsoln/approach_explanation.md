### Approach Explanation – Round 1B

**Objective**: Build a persona-driven document intelligence tool that identifies and ranks relevant content for a given persona and task across multiple PDFs.

---

### 💡 Methodology

1. **Input Parsing**: PDFs and a `persona.json` file are loaded from `/app/input`.
2. **Context Embedding**: The persona and their job-to-be-done are encoded into a dense vector using `all-MiniLM-L6-v2` (under 100MB).
3. **Document Segmentation**: PDFs are processed using `PyMuPDF`, extracting per-page text.
4. **Semantic Ranking**: Each page's text is embedded and scored against the persona context using cosine similarity.
5. **Result Generation**:
   - Top 5 sections are selected and ranked.
   - Subsection analysis pulls key text snippets.
6. **Output**: A JSON is written to `/app/output/output.json` with metadata, ranked sections, and refined text.

---

### ⚙️ Tech Stack

- `PyMuPDF`: Lightweight and accurate PDF parsing
- `sentence-transformers`: For embedding and similarity comparison
- `Docker`: Platform portability (AMD64, no internet, CPU only)

---

### 🚫 Constraints Handled

- ✅ Model Size < 1 GB
- ✅ CPU Only, No Internet
- ✅ Execution Time < 60s (on 3–5 PDFs)
- ✅ Docker-ready, works offline