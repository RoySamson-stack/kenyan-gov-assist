## AfyaTranslate AI – Strategic Build Plan

### Executive Summary
AfyaTranslate AI eliminates Kenyan healthcare language barriers by combining speech recognition, neural translation, and text-to-speech tuned for English, Swahili, and prioritized local languages (Kikuyu first). It provides doctors and patients with clear, context-aware conversations, even in offline clinics. The project aligns with SDG 3 & 10 and Kenya’s AI for National Prosperity theme.

---

### Vision & Objectives
- Real-time translation between clinicians and patients across voice, SMS, and web/mobile touchpoints.
- Safety-first medical dictionary + translation memory to reduce misdiagnosis risk.
- Offline-first workflows so rural clinics stay functional without reliable internet.
- Continuous learning loop via ratings and audio QA.

---

### MVP Requirements (Must Have)
- English ↔ Swahili voice translation with medical terminology boosts (shared with Serikali Yangu base model).
- Africa’s Talking Voice API bridge for phone consultations.
- SMS prescription delivery in native language.
- Web clinician console + responsive patient view.
- 500-term medical dictionary + 200 offline phrase pairs.
- Offline-ready mode with SQLite packs.
- Feedback loop (thumbs up/down).

### Phase 2 Targets (Should Have)
- Add Kikuyu coverage, USSD interface, voice biometrics, KenyaEMR integration, doctor dashboard with translation history, audio recordings for QA.

### Future Enhancements (Nice to Have)
- AI-powered symptom checker, M-Pesa payments, telemedicine video with live subtitles, localized health education campaigns.

---

## Phased Delivery Plan

### Phase 1: Foundation (Weeks 1‑4)
1. **Problem Validation & Research**
   - Interview 10‑15 healthcare workers (Kiambu, Nyeri, Kisumu).
   - Capture top 3 use cases (triage, prescription, emergency intake).
   - Map clinic workflows end-to-end.
2. **Data Collection Strategy**
   - Create phrase taxonomy (symptoms, meds, instructions).
   - Curate 200‑300 English/Swahili medical phrases.
   - Partner with UoN/Kenyatta med students for Kikuyu translations.
   - Launch Google Form for crowdsourced translations + audio.
3. **Language Scope Decision**
   - MVP: English ↔ Swahili only.
   - Phase 2: Add Kikuyu; queue Luo, Luhya, Kalenjin, Kamba later.

### Phase 2: Technical Architecture (Weeks 5‑8)
4. **Shared Model & Integration Strategy**
   - Single Ollama model (`llama3.2:1b`) hosts civic + health adapters; domain routed by prompts + RAG filters.
   - Africa’s Talking = primary voice/SMS/USSD layer (cost-effective in Kenya, M-Pesa ready).
   - Twilio = backup + advanced workflows (Studio IVR, Verify, international reach).
   - Use cases: patient hotline bridging, prescription SMS, USSD health info menu, airtime incentives, civic hotline overflow.
5. **System Architecture**
   - FastAPI backend with domain-aware services (chat, translation, voice gateway).
   - Shared RAG layer (Chroma DB) storing civic + health corpora with metadata tags.
   - Web (React/Vite) + mobile/PWA frontends that let users switch between Serikali Yangu and AfyaTranslate contexts.

### Phase 3: Technical Components (Weeks 9‑16)
6. **Speech Stack**
   - ASR: Whisper small (Swahili), Wav2Vec2 fine-tune or keyword spotting for Kikuyu.
- **Kikuyu Expansion (In Progress)**: Bootstrap translation memory files under `data/translations/kikuyu/` using trusted community corpora (e.g., [Glosbe English‑Kikuyu dictionary](https://glosbe.com/en/ki)), expose `kikuyu` as a selectable language in the UI, and reuse the shared translation service for quick wins while native ASR/TTS models are collected.
- **Document Translation Pipeline**: The current RAG stack serves English/Swahili source PDFs. For Kikuyu or other languages, integrate an offline translation job that renders the chunk text into the desired language (with source metadata) so clinicians can read summaries without waiting for full-language copies. This should run as a background task after ingestion and cache outputs alongside the original chunks.
   - TTS: Google Cloud TTS/gTTS for Swahili; recorded Kikuyu phrases until Coqui TTS custom model.
   - NMT: Google Translate API with terminology overrides; scale to NLLB-200 or LoRA fine-tunes for local languages.
7. **Offline Capability**
   - Level 1: SQLite phrase packs (500 pairs + audio snippets).
   - Level 2: Low-bandwidth sync for new phrases/audio.
   - Level 3: Full online AI translation + speech synthesis.
   - Ship as Progressive Web App with background sync.

---

## Technical Recommendations
- **Model Strategy**: Default to `llama3.2:1b` (CPU-friendly) shared across domains; attach LoRA adapters or system prompts per domain. For richer translations, fine-tune NLLB-200 via LoRA once data matures.
- **Telemetry**: Capture translation ratings, latency, ASR confidence, and anonymized error tags.
- **Security & Privacy**: Encrypt data at rest, apply Kenya Data Protection Act guidelines, anonymize patient identifiers, and store sensitive audio locally unless consented.
- **Scalability**: Containerize FastAPI + Ollama, use asynchronous queues for speech jobs, leverage Africa’s Talking webhooks for call state.
- **Localization**: Maintain translation memory + medical glossary in `data/translations/`, versioned and reviewed by clinicians.

---

## Immediate Next Steps
1. Audit current datasets in `data/raw` and flag gaps for medical content.
2. Stand up Africa’s Talking sandbox credentials and stub webhook handlers.
3. Build phrase taxonomy spreadsheet + Google Form templates.
4. Repair Python virtualenv to ensure `pytest` and FastAPI smoke tests run.
5. Prototype offline phrase lookup API + front-end toggle.

This plan should be revisited after the initial research sprint to integrate real-world findings before committing to significant engineering investments.

