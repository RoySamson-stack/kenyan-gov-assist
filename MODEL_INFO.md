# Kenyan Gov Assist - Project Structure

## Models Available (Ready to Use)

### 1. **kenyan-assistant** ✅ Installed
- **Base:** Llama 3.2 1B
- **Parameters:** ~1 billion
- **Size:** 1.3 GB
- **Method:** Modelfile (system prompt only)
- **Status:** Ready now
- **Quality:** Basic Kenyan language support

### 2. **llama3.2:1b** ✅ Installed  
- **Parameters:** ~1 billion
- **Size:** 1.3 GB
- **Method:** Base model (no customization)
- **Status:** Fallback option

---

## Models to Create (Run Scripts)

### 3. **kenyan-assistant** 📝 Script Ready
- **Script:** `bash scripts/create_kenyan_model.sh`
- **Base:** Llama 3.2 1B
- **Parameters:** ~1 billion
- **Will be:** Better system prompt + few-shot examples

### 4. **kenyan-deepseek** 📝 Script Ready
- **Script:** `bash scripts/create_all_models.sh`
- **Base:** DeepSeek-R1 1.5B
- **Parameters:** ~1.5 billion
- **Will be:** Better for reasoning

---

## Fine-Tuned Model (After Training with More Data)

### 5. **kenyan-gov-finetuned** 🔬 Needs Training
- **Method:** QLoRA Fine-tuning
- **Base:** llama3.2:1b or DeepSeek-R1 1.5B
- **Parameters trained:** Only 1-2 million (0.1% of base)
- **Training data needed:** 1000+ examples (we have 328 now)
- **Script:** `scripts/finetune/train.py`
- **Quality:** ⭐⭐⭐⭐⭐ Excellent

---

## Current Training Data Status

| Dataset | Examples | Quality |
|----------|---------|----------|
| Translation memories | 83 | Good |
| Generated phrases | 54 pairs | Basic |
| General QA pairs | 6 | Basic |
| **Total** | **328** | **Too few for QLoRA** |

**Collect more data, then run:**
```bash
# When you have 1000+ examples:
cd scripts/finetune
python3 train.py
```

---

## Project Structure (Clean)

```
kenyan-gov-assist/
├── models/              # Model files (Modelfiles)
│   ├── Modelfile           (Llama-based)
│   └── Modelfile.deepseek  (DeepSeek-based)
├── scripts/
│   ├── create_kenyan_model.sh      # Creates kenyan-assistant
│   ├── create_all_models.sh       # Creates all models
│   └── finetune/                  # QLoRA training scripts
│       ├── train.py               # QLoRA training
│       ├── prepare_data.py
│       └── merge_and_export.py
├── backend/             # FastAPI backend
├── frontend/            # React frontend
└── data/                # Training data (can be hidden)
    └── finetune/           # Training datasets
```

---

## Quick Start (Use What You Have NOW)

```bash
# 1. Test existing model
ollama run kenyan-assistant "Habari? Nawezaje kukusaidia?"

# 2. Create better model (Modelfile-based)
bash scripts/create_kenyan_model.sh

# 3. Start the app
ollama serve  # Terminal 1
cd backend && python3 -m uvicorn app.main:app  # Terminal 2
cd frontend && npm run dev  # Terminal 3
```

**Your `kenyan-assistant` works NOW** - start using it while collecting more data for QLoRA training! 🚀
