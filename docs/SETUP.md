## Setup Guide

### 1. Install Dependencies
- Backend: `cd /home/ralan/personal-projects/kenyan-gov-assistant/backend && pip install -r requirements.txt`
- Frontend: `cd /home/ralan/personal-projects/kenyan-gov-assistant/frontend && npm install`
- (Optional) Mobile: `cd /home/ralan/personal-projects/kenyan-gov-assistant/mobile && npm install`

### 2. Configure Environment
Create `/home/ralan/personal-projects/kenyan-gov-assistant/backend/.env` with:
```
APP_NAME=Serikali Yangu
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
VECTOR_DB_PATH=../data/vector_db/chroma
RAW_DOCS_PATH=../data/raw
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### 3. Prepare Ollama
- Install Ollama locally.
- Pull the model: `ollama pull llama3.1:8b` (matches `OLLAMA_MODEL`).
- On CPU-only hosts or small VPS tiers, set `OLLAMA_GPU_LAYERS=0` to prevent GPU errors.
- Start the daemon (`ollama serve`) before running the backend.

### 4. Ingest Documents (Required)
This step populates ChromaDB with Kenyan government PDFs.
```
cd /home/ralan/personal-projects/kenyan-gov-assistant/backend
python scripts/ingest_documents.py --reset --directory ../data/raw
```
What happens:
- PDFs under `data/raw` are chunked and saved to `data/processed`.
- Embeddings are written to `data/vector_db/chroma`.
- The pipeline runs automatic smoke searches and verifies the vector store.

Re-run the command whenever you add or update PDFs. Use `--file path/to/doc.pdf` for a single document.

### 5. Run Services
Start backend:
```
cd /home/ralan/personal-projects/kenyan-gov-assistant/backend
uvicorn app.main:app --reload
```
Start frontend:
```
cd /home/ralan/personal-projects/kenyan-gov-assistant/frontend
npm run dev
```

### 6. Health Checks
- Visit `http://localhost:8000/api/health` to confirm backend.
- `GET /api/chat/stats` should return `status: "healthy"` once ingestion succeeds.

### 7. Troubleshooting
- `Vector store is empty` → rerun ingestion; ensure PDFs exist.
- `Failed to load embedding model` → install `sentence-transformers` and ensure internet access for model download.
- Ollama errors → confirm the daemon is running and matches `OLLAMA_MODEL`.
