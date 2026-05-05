#!/bin/bash
# Create custom Ollama models for Kenyan languages
# Creates both Llama-based and DeepSeek-based models

set -e

echo "=== Creating Kenyan Language Models ==="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama not found. Install from https://ollama.com"
    exit 1
fi

# Function to check and pull model
check_and_pull() {
    local model=$1
    echo "Checking $model..."
    if ! ollama list | grep -q "$model"; then
        echo "Pulling $model - this may take a while..."
        ollama pull "$model"
    else
        echo "$model already exists"
    fi
}

# Create Llama-based model
echo "=== Creating Llama-based model ==="
check_and_pull "llama3.2:1b"

echo ""
echo "Creating kenyan-assistant (Llama-based)..."
ollama create kenyan-assistant -f models/Modelfile

# Create DeepSeek-based model (optional, uncomment to enable)
echo ""
echo "=== Creating DeepSeek-based model ==="
check_and_pull "deepseek-r1:1.5b"

echo ""
echo "Creating kenyan-deepseek..."
ollama create kenyan-deepseek -f models/Modelfile.deepseek

echo ""
echo "=== Models Created Successfully! ==="
echo ""
echo "Available models:"
ollama list | grep -E "kenyan|llama3.2|deepseek"
echo ""
echo "To use Llama-based model:"
echo "  ollama run kenyan-assistant"
echo ""
echo "To use DeepSeek-based model:"
echo "  ollama run kenyan-deepseek"
echo ""
echo "To test:"
echo "  ollama run kenyan-assistant 'Habari? Niulize kuhusu huduma za serikali'"
echo ""
echo "To update the app config, edit backend/app/config.py:"
echo "  OLLAMA_MODEL: str = 'kenyan-assistant'  # or 'kenyan-deepseek'"
echo ""

# Test the models
echo "Testing kenyan-assistant model..."
ollama run kenyan-assistant "Hello! Who are you and what languages do you speak?" --no-done 2>&1 | head -15

echo ""
echo "Done! Your Kenyan language models are ready."
