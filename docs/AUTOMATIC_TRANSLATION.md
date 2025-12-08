# Automatic Document Translation System

## Overview

When you upload a document (PDF), the system **automatically translates every chunk** into all configured target languages using Ollama. This happens during ingestion, so translated content is immediately available for RAG queries.

## How It Works

### 1. **Document Upload & Processing**
   - PDF is processed into chunks (500 chars each, 50 char overlap)
   - Language is **auto-detected** from filename and content:
     - Filenames with "swahili", "kiswahili", "sw" → detected as Swahili
     - Content analysis checks for common Swahili words
     - Defaults to English if not detected

### 2. **Automatic Translation**
   - For each chunk, the system translates into **all target languages**:
     - Currently configured: `kikuyu`, `luo`
     - Add more languages in `backend/app/config.py` → `TRANSLATION_TARGET_LANGUAGES`
   
### 3. **Translation Process**
   - **First**: Checks JSON translation memory files for exact phrase matches (fast lookup)
   - **Then**: Uses Ollama (`llama3.2:1b`) to translate the **full chunk text**
   - Translations are stored in chunk metadata: `metadata["translations"]["kikuyu"]`, etc.

### 4. **Storage**
   - Original chunk stored with source language
   - All translations stored in `metadata["translations"]` dictionary
   - Vector DB stores everything together for fast retrieval

## Example

**Upload**: `Constitution_of_Kenya.pdf` (English)

**What Happens**:
1. Document split into ~200 chunks
2. Each chunk translated to Kikuyu and Luo
3. Total: ~400 translations (200 chunks × 2 languages)
4. Progress logged: `[1/400] Translating chunk 1/200 (english → kikuyu)...`

**Result**: 
- Query in English → returns English chunks
- Query in Kikuyu → returns **pre-translated Kikuyu chunks** (instant, no LLM call needed)
- Query in Luo → returns **pre-translated Luo chunks**

## Configuration

### Add More Target Languages

Edit `backend/app/config.py`:

```python
TRANSLATION_TARGET_LANGUAGES: List[str] = ["kikuyu", "luo", "luhya", "kalenjin", "kamba"]
```

### Translation Memory (JSON Files)

JSON files in `data/translations/` are used for **fast phrase lookups**:
- Format: `{source}-{target}[__{domain}].json`
- Example: `english-kikuyu__health.json`
- Contains common phrases: "Good morning" → "Uhoro wa ruciine"

**Note**: JSON is optional. If a phrase isn't in JSON, Ollama translates it anyway.

## Commands

### Ingest New Documents (with auto-translation)

```bash
cd backend
source venv/bin/activate
python scripts/ingest_documents.py --directory ../data/raw
```

### Backfill Translations for Existing Documents

If you have documents that were ingested before translation was added:

```bash
cd backend
source venv/bin/activate
python scripts/backfill_translations.py --processed-path ../data/processed
```

## Performance

- **Translation Speed**: ~2-5 seconds per chunk (depends on Ollama model speed)
- **Large Documents**: Constitution (~200 chunks) takes ~10-15 minutes for 2 languages
- **Progress Tracking**: Real-time logging shows translation progress

## Benefits

✅ **No manual translation needed** - Everything happens automatically  
✅ **Multi-language RAG** - Query in any language, get results in that language  
✅ **Offline-capable** - Pre-translated chunks work without LLM calls  
✅ **Domain-aware** - Health documents use health-specific translation prompts  
✅ **Source language flexible** - Works with English OR Swahili source documents  

## Current Status

- ✅ Auto-translation during ingestion
- ✅ Language detection (English/Swahili)
- ✅ Kikuyu + Luo target languages configured
- ✅ Translation memory integration
- ✅ Progress logging
- ⚠️ Existing documents need backfill (run backfill script)



