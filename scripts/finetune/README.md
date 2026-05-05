# Fine-tuning Requirements

## Hardware Requirements
- **Minimum**: 8GB VRAM (RTX 3070 or equivalent)
- **Recommended**: 16GB+ VRAM (RTX 4080, A4000, A100)

## Software Requirements
- Python 3.10+
- CUDA 11.8+ / 12.1+
- 20GB+ free disk space

## Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install training dependencies
pip install bitsandbytes peft transformers accelerate datasets trl scipy

# Install unsloth for optimized 4-bit loading
pip install unsloth
```

## Quick Start

```bash
cd scripts/finetune

# 1. Prepare training data from existing chunks
python prepare_data.py --chunks-dir ../../data/processed/chunks --output-dir ../../data/finetune

# 2. Train the model (takes 1-4 hours depending on GPU)
python train.py

# 3. Merge weights and export to Ollama
python merge_and_export.py

# 4. Create Ollama model
cd ../../models/kenyan-gov-merged
ollama create kenyan-gov-assist -f Modelfile

# 5. Update your .env to use the new model
echo "OLLAMA_MODEL=kenyan-gov-assist" >> ../../backend/.env
```

## Training Configuration

### For 1B model (CPU-friendly, ~4GB VRAM)
- Batch size: 4
- Epochs: 3
- Training time: ~2-4 hours

### For 3B model (requires 8GB+ VRAM)
```python
# In train.py, change:
BASE_MODEL = "unsloth/llama3.2-3b-bnb-4bit"
```

### Hyperparameters
- Learning rate: 2e-4
- LoRA r: 16
- LoRA alpha: 32
- Warmup steps: 10
- Max sequence length: 512

## Adding More Training Data

Place additional JSON files with chunks in `data/processed/chunks/`. The prepare script will automatically include them.

Format for custom chunks:
```json
[
  {
    "chunk_id": "doc1_0",
    "content": "Your document content here...",
    "metadata": {
      "source": "document.pdf",
      "domain": "civic"
    }
  }
]
```
