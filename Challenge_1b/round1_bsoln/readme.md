## Adobe Hackathon Challenge – Round 1B

### 🚀 Project: Persona-Driven PDF Intelligence

This tool extracts and ranks the most relevant sections from a set of PDFs based on a given persona and their job-to-be-done.

---

### 📂 Folder Structure

- `/app/input/`: Place PDFs and `persona.json` here
- `/app/output/`: Resulting `output.json` will be generated here
- `main.py`: Main processing script

---

### 🐳 Docker Build & Run

```bash
docker build --platform linux/amd64 -t pdf-intel:round1b .
docker run --rm -v $(pwd)/app/input:/app/input -v $(pwd)/app/output:/app/output --network none pdf-intel:round1b