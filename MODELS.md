# Kenyan Gov Assist - Model Summary

## Model Options (Parameter Count)

### 1. **kenyan-assistant** (Recommended)
- **Base:** Llama 3.2 1B
- **Parameters:** ~1 billion
- **Size:** ~1.3GB
- **Speed:** Fast (CPU-compatible)
- **Best for:** General Kenyan language translation, translation support, general

### 2. **kenyan-deepseek**
- **Base:** DeepSeek-R1 1.5B
- **Parameters:** ~1.5 billion  
- **Size:** ~1.8GB
- **Speed:** Moderate (CPU-compatible)
- **Best for:** Reasoning, complex queries, step-by-step explanations

### 3. **llama3.2:1b** (Default/Fallback)
- **Parameters:** ~1 billion
- **Size:** ~1.3GB
- **Speed:** Fastest
- **Best for:** Testing, fallback option

---

## How to Create the Models

```bash
cd /home/unknwn/ai-models/kenyan-gov-assist

# Option 1: Create both models (recommended)
bash scripts/create_all_models.sh

# Option 2: Create only Llama-based model
bash scripts/create_kenyan_model.sh
```

The script will:
1. Check if Ollama is installed
2. Pull base models (llama3.2:1b, deepseek-r1:1.5b)
3. Create custom Kenyan language models
4. Test the models automatically

---

## Using the Models

### Test the model:
```bash
# Llama-based
ollama run kenyan-assistant "Habari? Niulize kuhusu huduma za serikali"

# DeepSeek-based  
ollama run kenyan-deepseek "Hello, what are the counties in Kenya?"
```

### The app is already configured to use `kenyan-assistant` by default.

To switch models, edit `backend/app/config.py`:
```python
OLLAMA_MODEL: str = "kenyan-deepseek"  # or "kenyan-assistant", "llama3.2:1b"
```

---

## Model Comparison

| Feature | kenyan-assistant | kenyan-deepseek | llama3.2:1b |
|---------|------------------|-----------------|---------------|
| Parameters | 1B | 1.5B | 1B |
| Speed | Fast | Moderate | Fastest |
| Kenyan Language Support | Excellent | Good | Basic |
| Reasoning | Good | Excellent | Basic |
| File Size | ~1.3GB | ~1.8GB | ~1.3GB |
| CPU Compatible | ✅ | ✅ | ✅ |

---

## Next Steps

After creating the models:

1. **Start Ollama service:**
   ```bash
   ollama serve
   ```

2. **Start the backend:**
   ```bash
   cd backend
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **Start the frontend:**
   ```bash
   cd frontend
   npm install && npm run dev
   ```

4. **Open browser:** http://localhost:5173

You now have a real-time voice translator for Kenyan languages! 🎉
