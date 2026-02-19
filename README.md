# Kisan Call Centre Query Assistant

An AI-Powered Agricultural Helpdesk using **Ollama (Local AI)** and **FAISS**.

## Features
- **Offline Mode**: Semantic search using FAISS on KCC dataset.
- **Online Mode**: Generates simple, farmer-friendly answers using a local LLM via **Ollama**.
- **Multilingual**: Supports queries in any language (Google Translate / LLM capabilities).
- **Firebase Integration**: Logs conversation history to Firebase Realtime Database.

## Prerequisites
1. **Python 3.9+**
2. **Ollama**:
   - Download and install from [ollama.com](https://ollama.com).
   - Pull the model you want to use (default: `granite3-dense` or `llama3`).
     ```bash
     ollama pull granite3-dense:8b
     # OR
     ollama pull llama3
     ```
   - Start the server: `ollama serve`

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Create `.env` to override defaults:
   ```env
   # Default is http://localhost:11434
   OLLAMA_BASE_URL=http://localhost:11434
   # Default is granite3-dense:8b
   OLLAMA_MODEL=mistral
   
   # Firebase (if not using the default one in code)
   FIREBASE_DATABASE_URL=https://your-db.firebaseio.com
   ```

## Running the App
1. Initialize data (only need to do this once):
   ```bash
   python scripts/data_preprocessing.py
   python scripts/build_embeddings_faiss.py
   ```
   *(Note: valid `raw_kcc.csv` in `data/` is required)*

2. Run Streamlit:
   ```bash
   streamlit run app.py
   ```

## Troubleshooting
- **"Ollama not found"**: Ensure `ollama serve` is running in a separate terminal.
- **"Model not found"**: Run `ollama pull <model_name>` to download it.
