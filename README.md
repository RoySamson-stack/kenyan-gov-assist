# Kenyan Gov Assist - Serikali Yangu

> AI-powered assistant for Kenyan government services, healthcare, and civic information with **realtime voice translation** for Kenyan languages.

![CI/CD](https://github.com/RoySamson-stack/kenyan-gov-assist/actions/workflows/ci-cd.yml/badge.svg)
![Docker Build](https://github.com/RoySamson-stack/kenyan-gov-assist/actions/workflows/ci-cd.yml/badge.svg)
![Coverage](https://codecov.io/gh/RoySamson-stack/kenyan-gov-assist/branch/main/graph/badge.svg)

## Features

- **Multi-Language Support**: English, Kiswahili, Gĩkũyũ, Dholuo, Kikamba, Kalenjin, Luhya, Somali, Kisii, Meru
- **Realtime Voice Translation**: WebSocket + REST endpoints for voice-to-voice translation
- **Speech-to-Text**: Whisper integration for voice input
- **Text-to-Speech**: Coqui TTS + pyttsx3 for voice output
- **Document Processing**: PDF, Word, Excel, ePub, HTML support
- **Custom Kenyan Models**: `kenyan-gov:latest` (1B params), `kenyan-assitant`, `kenyan-deepseek` (1.5B)
- **RAG Pipeline**: Retrieval-Augmented Generation using ChromaDB
- **Translation Memory**: Phrase-level caching for common terms
- **Production Ready**: Docker, CI/CD, Rate Limiting, Auth (coming soon)

## Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR: Python 3.12+, Node.js 20+, Ollama

### Option 1: Docker (Recommended)
```bash
git clone https://github.com/RoySamson-stack/kenyan-gov-assist.git
cd kenyan-gov-assist

# Create Kenyan language models
bash scripts/create_kenyan_model.sh

# Start all services
docker-compose up -d

# Access the app
open http://localhost:3000
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
bash install_dependencies.sh

# 2. Create Kenyan language models
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
| `kenyan-gov:latest` | 1B | 1.3GB | **Ready now** - General use |
| `kenyan-assitant` | 1B | 1.3GB | Better few-shot examples |
| `kenyan-deepseek` | 1.5B | 1.8GB | Reasoning tasks |
| `llama3.2:1b` | 1B | 1.3GB | Fallback option |

**Create custom models:**
```bash
bash scripts/create_kenyan_model.sh          # Llama-based
bash scripts/create_all_models.sh          # All models
```

## API Endpoints

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/chat` | POST | Chat with AI |
| `/api/translate` | POST | Text translation |
| `/api/voice/transcribe` | POST | Speech-to-text |
| `/api/voice/synthesize` | POST | Text-to-speech |
| `/api/ws/translate` | WebSocket | Realtime voice translation |
| `/api/documents/upload` | POST | Upload documents |

## Project Structure

```
kenyan-gov-assist/
├── backend/          # FastAPI backend
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

- [x] Basic chat + translation
- [x] Voice input/output
- [x] 10 Kenyan languages
- [ ] Authentication & rate limiting
- [ ] 80%+ test coverage
- [ ] QLoRA fine-tuning (1000+ examples)
- [ ] 60+ Kenyan languages
- [ ] Mobile app (React Native)
- [ ] PWA support
