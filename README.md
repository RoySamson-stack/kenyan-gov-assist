# Serikali Yangu – Kenyan Government Assistant

Serikali Yangu is a Retrieval-Augmented Generation (RAG) assistant that answers questions about Kenyan government services, laws, permits, and policies. It combines a FastAPI backend, Ollama-powered language models, a Chroma vector database, and a Vite React chat interface.

### Repository Layout
- `backend/` – FastAPI app, RAG/translation services, ingestion scripts.
- `frontend/` – Vite + React chat interface.
- `mobile/` – React Native scaffold (optional for MVP).
- `data/` – Raw PDFs, processed chunks, translation packs, vector database.
- `docs/` – Architecture, API, setup, deployment notes.
- `deployment/` – Docker, Kubernetes, nginx, and systemd assets.

### Quick Start
1. Follow the detailed environment guide in `docs/SETUP.md`.
2. Ingest documents so the vector store is ready:  
   ```
   cd /home/ralan/ai-models/kenyan-gov-assitant/backend
   python scripts/ingest_documents.py --reset --directory ../data/raw
   ```
3. Pull the CPU-first Ollama model (fits 8–12 GB RAM tiers):  
   ```
   ollama pull llama3.2:1b
   ```
4. Start services:  
   - Backend: `uvicorn app.main:app --reload`  
   - Frontend: `npm run dev` (inside `frontend/`)
5. Open the chat UI on `http://localhost:5173`, ask questions, and review cited sources.

### Status & Hosting
- Active development toward an expanded civic + health assistant.
- Minimum footprint: 4 vCPUs / 8 GB RAM / 80 GB NVMe.
- Configure `OLLAMA_MODEL` (defaults to `llama3.2:1b`) and set `OLLAMA_GPU_LAYERS=0` on CPU-only servers.
- Mount `data/vector_db` on persistent storage to keep embeddings across deploys.

---

## AfyaTranslate AI – Healthcare Extension

AfyaTranslate AI augments Serikali Yangu with a healthcare-specific translation layer that bridges English, Swahili, and priority local languages so clinicians and patients can communicate clearly—even offline. The full strategic roadmap lives in `docs/AFYATRANSLATE_PLAN.md`.

### Why it Matters
- Kenya’s 60+ languages cause misdiagnosis, poor adherence, and inequity.
- Existing translators miss medical nuance and local vernacular.
- Rural clinics require offline-first, low-cost solutions.

### Must-Have (MVP)
- Real-time English ↔ Swahili speech translation with medical terminology boosts.
- Africa’s Talking Voice API for phone triage and doctor routing.
- SMS prescription delivery in native language.
- Web clinician console + mobile-responsive patient interface.
- 500-term medical dictionary, 200 offline phrase pairs, thumbs up/down feedback.

### Should-Have (Phase 2)
- Add Kikuyu, USSD menus, voice biometrics, KenyaEMR integration, doctor dashboard w/ translation history, audio QA recordings.

### Nice-to-Have (Future)
- AI symptom checker, M-Pesa consultation payments, telemedicine video with subtitles, localized health education content.

### Technical Highlights
- **Model Strategy**: Default `llama3.2:1b` for CPU deployments; override via `OLLAMA_MODEL` if GPU resources exist.
- **Speech Stack**: Whisper small for Swahili ASR, Wav2Vec2 fine-tuning for Kikuyu, gTTS/Google Cloud TTS + Coqui for custom voices.
- **Translation Layer**: Hybrid of Google Translate API + medical glossary overrides today, migrating to NLLB-200/LoRA fine-tunes as data matures.
- **Offline Mode**: SQLite phrase packs + audio snippets, PWA caching, low-bandwidth sync tiers.
- **Integrations**: Africa’s Talking (voice, SMS, USSD, airtime incentives) as primary channel; Twilio for advanced IVR/Verify fallback.

### Roadmap Snapshot
- **Phase 1 (Weeks 1‑4)**: Field research (Kiambu, Nyeri, Kisumu), phrase taxonomy, 200‑300 Swahili medical phrases, Kikuyu partnership groundwork.
- **Phase 2 (Weeks 5‑8)**: Architecture + integrations, standing up Africa’s Talking/Twilio pipelines, EMR hooks.
- **Phase 3 (Weeks 9‑16)**: Speech/TTS/NMT enhancements, offline tiering, QA telemetry, scaling playbooks.

### Testing
- Backend: `cd backend && venv/bin/python -m pytest` (recreate `backend/venv` and install requirements if the bundled venv path is stale).
- Frontend: `npm test` (Jest/Vitest once configured).

### Contributing
Focus on Kenyan clinical realities, data privacy (Kenya Data Protection Act), and inclusive UX. See `docs/AFYATRANSLATE_PLAN.md` for detailed tasks, research prompts, and immediate next steps.
