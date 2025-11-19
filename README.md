# Serikali Yangu – Kenyan Government Assistant

Serikali Yangu is a Retrieval-Augmented Generation (RAG) assistant that answers questions about Kenyan government services, laws, permits, and policies. It combines a FastAPI backend, Ollama-powered language models, a Chroma vector database, and a Vite React chat interface.

## Repository Layout
- `backend/` – FastAPI app, RAG/translation services, ingestion scripts.
- `frontend/` – Vite + React chat interface.
- `mobile/` – React Native scaffold (optional for MVP).
- `data/` – Raw PDFs, processed chunks, vector database.
- `docs/` – Architecture, API, setup, deployment notes.
- `deployment/` – Docker, Kubernetes, nginx, and systemd assets.

## Quick Start
1. Follow the detailed environment guide in `docs/SETUP.md`.
2. Ingest documents so the vector store is ready:
   ```
   cd /home/ralan/personal-projects/kenyan-gov-assistant/backend
   python scripts/ingest_documents.py --reset --directory ../data/raw
   ```
3. Pull the Ollama model sized for 12 GB RAM tiers: `ollama pull llama3.1:8b` (set `OLLAMA_GPU_LAYERS=0` if you don’t have a GPU).
4. Start services:
   - Backend: `uvicorn app.main:app --reload`
   - Frontend: `npm run dev` (inside `frontend/`)
5. Open the chat UI on `http://localhost:5173`, ask questions, and review cited sources.

## Status
This repository is under active development toward an MVP in 5 days. Priorities include solidifying the ingestion pipeline, translation services, and polishing the chat UX. Contributions and issues are welcome.

### Suggested Hosting
- Minimum for smooth RAG + Ollama: 6 vCPUs / 12 GB RAM / 100 GB NVMe (e.g., VPS-3 tier).
- Configure `OLLAMA_MODEL=llama3.1:8b` and `OLLAMA_GPU_LAYERS=0` on CPU-only servers.
- Mount `data/vector_db` on persistent storage so redeployments keep embeddings intact.
# kenyan-gov-assist
