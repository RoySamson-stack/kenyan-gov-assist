## Platform Architecture – Serikali Yangu + AfyaTranslate

This document captures how the civic (Serikali Yangu) and healthcare (AfyaTranslate) capabilities share one language/translation backbone while exposing domain-specific experiences across web, mobile, voice, SMS, and USSD channels.

---

### 1. High-Level Topology
- **Shared AI Core**
  - Ollama-hosted `llama3.2:1b` (CPU-friendly) fine-tuned via lightweight adapters.
  - Retrieval layer (Chroma DB + sentence-transformers) houses both civic and medical corpora with domain tags.
  - Translation memory + medical glossary stored in `data/translations/`.
- **Domain Pods**
  - *Serikali Yangu Pod*: Routes civic questions, government services, policy docs.
  - *AfyaTranslate Pod*: Routes clinical encounters, symptom descriptions, medical instructions.
  - Pods share the same model but supply different system prompts, safety rails, and knowledge bases.
- **Experience Layer**
  - Web clinician console + citizen chat (React/Vite).
  - Mobile/PWA front ends for patients.
  - Voice/SMS/USSD adapters via Africa’s Talking + Twilio.

---

### 2. Unified Language Model Strategy
1. **Single Base Model**
   - Ollama `llama3.2:1b` pulled once; `OLLAMA_MODEL` remains globally configurable.
   - `OLLAMA_GPU_LAYERS=0` ensures CPU compatibility.
2. **Domain Conditioning**
   - System prompts (`models/system_prompts/*.txt`) encode persona + compliance rules for each pod.
   - Retrieval pipeline filters documents by `domain` metadata (`civic`, `health`) before constructing context windows.
3. **Terminology Layers**
   - Medical dictionary (500 terms MVP, expanding) maintained as JSON/SQLite for deterministic replacements pre/post LLM call.
   - Civic glossary handles legal acronyms, ministry names, etc.
4. **Fine-Tuning Roadmap**
   - Phase 1: Prompt + RAG only.
   - Phase 2: LoRA adapters (one per domain) applied on top of base model; swapped dynamically via Ollama Modelfiles.
   - Phase 3: Optional custom NLLB-200 based translator for low-resource local languages, still exposed through the same API.

---

### 3. Data & Training Pipeline
1. **Ingestion**
   - `scripts/ingest_documents.py` tags sources with `domain`, `language`, `subject`, `reading_level`.
   - Medical corpus: clinic workflows, symptom phrases, prescription templates, Kenya MoH guidelines.
   - Civic corpus: constitution, permits, FAQs, policies.
2. **Chunking & Embeddings**
   - SentenceTransformers (MiniLM) → Chroma DB, namespaced per domain but stored in one DB (`collection=civic` / `collection=health`).
3. **Translation Memory**
   - Stored under `data/translations/<language>/medical.json` & `civic.json`.
   - Accessed by translation service before/after LLM calls for consistency.
4. **Evaluation**
   - Shared `tests/translation.py` extended with fixtures for civic + medical phrases.
   - Domain-specific regression suites (e.g., `tests/health/test_triage_flow.py` to be added).

---

### 4. API & Service Layer
- **FastAPI Modules**
  - `app/api/routes/chat.py`: main chat endpoint, accepts `domain` parameter (`civic` default, `health` for Afya).
  - `app/services/rag_service.py`: fetches domain-scoped context.
  - `app/services/translation_service.py`: orchestrates speech-to-text, translation memory, LLM call, text-to-speech.
  - `app/services/voice_gateway.py` (to be added): handles webhook traffic from Africa’s Talking/Twilio.
- **Session Orchestration**
  - Each session stores `domain`, `language_pair`, `channel (web, voice, sms, ussd)`, `feedback`.
  - Domain-specific safety filters applied before delivering responses.

---

### 5. Communication Channels
#### Africa’s Talking (Primary)
- **Voice API**
  - Clinic hotline numbers → AT voice webhook → `voice_gateway` → ASR (Whisper) → LLM → TTS → AT response.
  - Call flow logic stored in `deployment/at_voice_flow.json`.
- **SMS API**
  - Prescription or follow-up instructions pushed via `POST /sms/send`.
  - Supports local language templates; falls back to translation service.
- **USSD**
  - `*XYZ#` menu exposing triage, health tips, or civic FAQs.
  - Backend exposes `/ussd/inbound` for AT to invoke; responses pulled from offline phrase packs when needed.
- **Airtime/Payments**
  - Incentivize research participants in Phase 1; prep for future M-Pesa billing.

#### Twilio (Secondary/Scaling)
- **Programmable Voice**
  - Redundant call routing + international reach.
  - Twilio Studio flows for IVR experiments.
- **Verify API**
  - Patient/clinician identity verification via OTP SMS before sharing sensitive data.

---

### 6. Offline & Low-Bandwidth Design
- **Phrase Packs**
  - SQLite DB embedded in mobile/PWA with 200+ common medical phrases (MVP) and civic FAQs.
- **Sync Strategy**
  - Service workers handle delta sync when connectivity resumes.
  - Audio snippets (TTS) cached for critical instructions (dosage, follow-up).
- **Edge Execution**
  - Future: run distilled ASR/TTS models on edge devices in clinics; still rely on central LLM for nuanced translation when online.

---

### 7. Nice-to-Have / Future Enhancements
- **AI Symptom Checker**
  - Rule-based triage + LLM reasoning; requires clinical sign-off.
- **M-Pesa Integration**
  - Use Africa’s Talking or Safaricom Daraja for consultation payments + airtime rewards.
- **Telemedicine Video w/ Live Subtitles**
  - WebRTC widget; subtitles generated by ASR → translation → TTS/closed captions.
- **Health Education Content**
  - Push multimedia campaigns (audio + text) in local languages via SMS/WhatsApp/USSD.
- **Voice Biometrics**
  - Integrate speaker verification for patient identity in Phase 2.

---

### 8. Implementation Next Steps
1. Finalize shared `translation_service.py` with domain-aware prompts + glossary hooks.
2. Create `voice_gateway` module handling Africa’s Talking + Twilio webhooks.
3. Extend data ingestion to tag documents with `domain`.
4. Update frontend to allow domain selection (Serikali vs Afya) while reusing chat components.
5. Build USSD menu definitions and simulator tests.
6. Define LoRA fine-tune pipeline once 2k+ domain sentences per language accrue.

This architecture ensures both initiatives benefit from a single, efficiently hosted language base while honoring the unique safety, terminology, and workflow needs of civic and healthcare scenarios.
