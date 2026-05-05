#!/bin/bash
# Install dependencies for Kenyan Gov Assist with Voice Translation
set -e

echo "=== Kenyan Gov Assist - Dependency Installer ==="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not installed."
    exit 1
fi

echo "Python version: $(python3 --version)"

# Create virtual environment (optional but recommended)
if [ "$1" == "--venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment activated."
fi

# Install Python backend dependencies
echo ""
echo "Installing Python backend dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Install Whisper (may take a while)
echo ""
echo "Installing Whisper for speech recognition..."
pip install openai-whisper

# Install Coqui TTS for text-to-speech
echo ""
echo "Installing Coqui TTS for speech synthesis..."
pip install TTS

cd ..

# Install Ollama (if not installed)
if ! command -v ollama &> /dev/null; then
    echo ""
    echo "Installing Ollama for local LLM..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed."
fi

# Pull default model
echo ""
echo "Pulling default LLM model (llama3.2:1b)..."
ollama pull llama3.2:1b || echo "Warning: Could not pull model. Ensure Ollama is running."

# Install Node.js dependencies for frontend
if command -v npm &> /dev/null; then
    echo ""
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    echo ""
    echo "Installing Vercel frontend dependencies (optional)..."
    if [ -d "vercel-frontend" ]; then
        cd vercel-frontend
        npm install
        cd ..
    fi
else
    echo "WARNING: npm not found. Skipping frontend installation."
fi

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "Creating .env file..."
    cat > backend/.env << EOL
APP_NAME=Serikali Yangu - Kenyan Language AI
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
WHISPER_MODEL=base
TTS_ENABLED=true
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
EOL
    echo ".env file created at backend/.env"
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p data/translations/{swahili,kikuyu,luo,kamba,kalenjin,luhya,somali,kisii,meru}
mkdir -p data/vector_db
mkdir -p data/processed/chunks

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Next steps:"
echo "1. Start Ollama: ollama serve"
echo "2. Start backend: cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Open http://localhost:5173 in your browser"
echo ""
echo "For voice features, ensure microphone permissions are granted in browser."
