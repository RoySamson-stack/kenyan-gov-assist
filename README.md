# Universal Translation Assistant

> AI-powered translation platform for books, curriculum materials, documents, conversations, voice, and general text across multiple languages. It supports Kenyan languages and general multilingual translation workflows.

![CI/CD](https://github.com/RoySamson-stack/kenyan-gov-assist/actions/workflows/ci-cd.yml/badge.svg)
![Docker Build](https://github.com/RoySamson-stack/kenyan-gov-assist/actions/workflows/ci-cd.yml/badge.svg)
![Coverage](https://codecov.io/gh/RoySamson-stack/kenyan-gov-assist/branch/main/graph/badge.svg)

## Features

- **Universal Document Translation**: Translate books, curriculum content, PDFs, Word documents, Excel files, and other uploaded materials.
- **General Text Translation**: Translate free-form text for education, business, personal, and everyday use cases.
- **Multi-Language Support**: English, Kiswahili, Gĩkũyũ, Dholuo, Kikamba, Kalenjin, Luhya, Somali, Kisii, Meru, plus backend-supported translation targets.
- **Book-Style Translation Workflow**: Upload content, process it asynchronously, track translation status, and download translated output.
- **Realtime Voice Translation**: WebSocket + REST endpoints for voice-to-voice translation.
- **Speech-to-Text**: Whisper integration for voice input.
- **Text-to-Speech**: Coqui TTS + pyttsx3 for voice output.
- **Document Processing**: PDF, Word, Excel, ePub, HTML, text, and related formats.
- **Translation Memory**: Phrase-level caching for common terms.
- **RAG Pipeline**: Retrieval-Augmented Generation using ChromaDB.
- **Standalone Translation Backend**: Copied `Translation_Backend` service for full document/book translation workflows.
- **Production Ready**: Docker, CI/CD, Rate Limiting, Auth (coming soon).

## Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR: Python 3.12+, Node.js 20+, Ollama

### Option 1: Docker (Recommended)
```bash
git clone https://github.com/RoySamson-stack/kenyan-gov-assist.git
cd kenyan-gov-assist

# Create translation language models
bash scripts/create_kenyan_model.sh

# Start all services
docker-compose up -d

# Access the app
open http://localhost:3000

# Full document/book translation API
open http://localhost:8002/docs
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
bash install_dependencies.sh

# 2. Create translation language models
bash scripts/create_kenyan_model.sh

# 3. Start Ollama
ollama serve

# 4. Start backend (new terminal)
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 5. Start frontend (new terminal)
cd frontend
npm install && npm run dev

# 6. Open browser
open http://localhost:5173
```

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

## Model Information

| Model | Parameters | Size | Use Case |
|-------|-------------|------|----------|
| `kenyan-assistant` | 1B | 1.3GB | **Ready now** - General use |
| `kenyan-assitant` | 1B | 1.3GB | Better few-shot examples |
| `kenyan-deepseek` | 1.5B | 1.8GB | Reasoning tasks |
| `llama3.2:1b` | 1B | 1.3GB | Fallback option |

**Create custom models:**
```bash
bash scripts/create_kenyan_model.sh          # Llama-based
bash scripts/create_all_models.sh          # All models
```

## API Endpoints

### Main API

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/api/general` | GET | General check |
| `/api/chat` | POST | Chat with AI |
| `/api/translate` | POST | General text translation |
| `/api/voice/transcribe` | POST | Speech-to-text |
| `/api/voice/synthesize` | POST | Text-to-speech |
| `/api/ws/translate` | WebSocket | Realtime voice translation |
| `/api/documents/upload` | POST | Upload documents for the main assistant pipeline |

### Full Document Translation API

The copied translation backend runs separately on `http://localhost:8002` when Docker Compose is used. It provides the book/document translation workflow copied from `Translation_Backend`, including authentication, uploads, async translation jobs, status checks, and translated downloads.

| Endpoint Area | Description |
|---------------|-------------|
| `/auth/*` | Login, refresh tokens, and current user |
| `/admin/books/*` | Upload and manage books/documents |
| `/admin/exams/*` | Import and manage Excel-based exams/content |
| `/student/translate*` | Start translations, check status, fetch translations, download output |
| `/translations/*` | Shared translation listing and download routes |

Swagger docs are available at `http://localhost:8002/docs`, and the original copied API notes are in `curriculum_translation_backend/README.original.md`.

## Project Structure

```
kenyan-gov-assist/
├── backend/          # FastAPI backend
├── curriculum_translation_backend/ # Full document/book translation service
├── frontend/         # React + Vite frontend
├── models/          # Ollama Modelfiles
├── scripts/         # Training & setup scripts
├── data/            # Translation memories (hidden)
└── deployment/      # Docker & K8s configs
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file.

## Roadmap

- [x] Basic chat + text translation
- [x] Voice input/output
- [x] Full document/book translation backend
- [x] PDF, Word, and Excel translation workflow
- [x] 10 languages in the main assistant
- [ ] Unify frontend screens for text, voice, and full document translation
- [ ] Authentication & rate limiting
- [ ] 80%+ test coverage
- [ ] More language packs and translation engines
- [ ] Mobile app (React Native)
- [ ] PWA support
