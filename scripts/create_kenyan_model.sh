#!/bin/bash
# Create custom Ollama model for Kenyan languages
# This script creates "kenyan-assistant" model

set -e

MODEL_NAME="kenyan-assistant"
MODELFILE_PATH="$(dirname "$0")/../models/Modelfile"

echo "=== Creating Kenyan Language Model ==="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama not found. Install from https://ollama.com"
    exit 1
fi

# Check if base model exists
echo "Checking base model (llama3.2:1b)..."
if ! ollama list | grep -q "llama3.2:1b"; then
    echo "Pulling base model (llama3.2:1b) - this may take a while..."
    ollama pull llama3.2:1b
fi

# Create the custom model
echo ""
echo "Creating custom model: $MODEL_NAME"
echo "Using Modelfile: $MODELFILE_PATH"
echo ""

ollama create "$MODEL_NAME" -f "$MODELFILE_PATH"

echo ""
echo "=== Model Created Successfully! ==="
echo ""
echo "To use the model:"
echo "  ollama run $MODEL_NAME"
echo ""
echo "To test:"
echo "  ollama run $MODEL_NAME 'Habari? Niulize kuhusu huduma za serikali'"
echo ""
echo "To use in the app, update backend/app/config.py:"
echo "  OLLAMA_MODEL: str = \"$MODEL_NAME\""
echo ""

# Test the model
echo "Testing the model..."
ollama run "$MODEL_NAME" "Hello, can you introduce yourself in Swahili?" --no-done 2>&1 | head -20
