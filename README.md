# Serikali Yangu

A chat assistant that helps Kenyans find answers about government services, laws, and policies. Drop a PDF in, ask a question, get an answer with source citations.

Built with FastAPI, Ollama for local language models, ChromaDB for semantic search, and a React frontend.

## What's in here

```
backend/        FastAPI app, RAG pipeline, translation services
frontend/       Vite + React chat UI
mobile/         React Native scaffold (not wired up yet)
data/           PDFs go here, along with the vector database
docs/           Architecture notes, API docs, setup guide
deployment/     Docker, Kubernetes, nginx configs
```

## Quick Start

1. Read `docs/SETUP.md` for the full setup guide.
2. Drop some Kenyan government PDFs into `data/raw/`.
3. Ingest them:
   ```bash
   cd backend
   python scripts/ingest_documents.py --reset --directory ../data/raw
   ```
4. Pull an Ollama model (works on CPU):
   ```bash
   ollama pull llama3.2:1b
   ```
5. Run backend and frontend:
   ```bash
   # terminal 1
   cd backend && uvicorn app.main:app --reload --port 8001

   # terminal 2
   cd frontend && npm run dev
   ```
6. Open `http://localhost:5173` and start asking questions.

## Two Modes

- **Serikali Yangu** – general civic questions (business registration, land titles, taxes, constitution)
- **AfyaTranslate** – healthcare translation for clinician-patient conversations (English ↔ Swahili with medical terms)

Toggle between them in the top bar of the UI.

## Config

Set these in `.env` if needed:

| Variable | Default | Notes |
|----------|---------|-------|
| `OLLAMA_MODEL` | `llama3.2:1b` | CPU-friendly. Use larger models if you have GPU. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | |
| `OLLAMA_GPU_LAYERS` | `0` | Set higher on GPU servers |

## Testing

```bash
cd backend && python -m pytest
```

## Status

Active development. The core RAG pipeline works. AfyaTranslate is partially built out with translation memory and telecom hooks (Africa's Talking, Twilio) but not fully integrated.

## Contributing

