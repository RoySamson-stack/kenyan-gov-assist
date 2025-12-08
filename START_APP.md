# How to Run the Application

## Prerequisites

1. **Ollama must be installed and running locally**
   ```bash
   # Check if Ollama is installed
   ollama --version
   
   # Start Ollama (if not already running)
   ollama serve
   
   # Pull the required model (if not already pulled)
   ollama pull llama3.2:1b
   ```

2. **Python virtual environment** (backend)
   ```bash
   cd /home/ralan/ai-models/kenyan-gov-assitant/backend
   source venv/bin/activate  # or create one: python -m venv venv
   pip install -r requirements.txt
   ```

3. **Node.js dependencies** (frontend)
   ```bash
   cd /home/ralan/ai-models/kenyan-gov-assitant/frontend
   npm install
   ```

## Running the Application

### Option 1: Manual Start (3 Terminal Windows)

**Terminal 1 - Ollama (if not already running):**
```bash
ollama serve
```

**Terminal 2 - Backend:**
```bash
cd /home/ralan/ai-models/kenyan-gov-assitant/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 3 - Frontend:**
```bash
cd /home/ralan/ai-models/kenyan-gov-assitant/frontend
npm run dev
```

### Option 2: Using the Start Script

```bash
cd /home/ralan/ai-models/kenyan-gov-assitant
chmod +x start_app.sh
./start_app.sh
```

## Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8001
- **Backend Health Check**: http://localhost:8001/api/health
- **API Docs**: http://localhost:8001/docs

## Verify Everything is Working

1. **Check Ollama:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Check Backend:**
   ```bash
   curl http://localhost:8001/api/health
   ```

3. **Test Chat API:**
   ```bash
   curl -X POST http://localhost:8001/api/chat \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What are my rights as a Kenyan citizen?",
       "language": "english",
       "domain": "civic",
       "use_rag": true
     }'
   ```

## Troubleshooting

### Backend won't start
- Ensure Ollama is running: `ollama serve`
- Check if port 8001 is available: `lsof -i :8001`
- Verify virtual environment is activated
- Check backend logs for errors

### Frontend can't connect to backend
- Verify backend is running on port 8001
- Check CORS settings in `backend/app/main.py`
- Ensure frontend is using correct API URL: `http://localhost:8001`

### Ollama connection errors
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check model is pulled: `ollama list`
- Pull model if missing: `ollama pull llama3.2:1b`

### Vector store is empty
- Run document ingestion:
  ```bash
  cd /home/ralan/ai-models/kenyan-gov-assitant/backend
  source venv/bin/activate
  python scripts/ingest_documents.py --reset --directory ../data/raw
  ```

## Docker Containers

**Note**: Currently, there are no Docker containers configured for this project. Ollama runs locally, and the backend/frontend run directly on your machine.

If you want to containerize later:
- Ollama can run in Docker: `docker run -d -p 11434:11434 ollama/ollama`
- Backend can be containerized using `backend/Dockerfile` (when configured)
- Frontend can be containerized with a simple nginx Dockerfile

