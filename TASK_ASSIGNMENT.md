# Kisan Call Centre Query Assistant — Task Assignment (3 Members)

Use this to divide work among 3 team members. Each person owns their files and deliverables; integrate together before demo.

---

## **MEMBER 1 — Data pipeline & embeddings**

**Role:** Prepare and index the KCC dataset so the app can do semantic search.

### Tasks
1. **Data preprocessing**
   - Maintain and run `scripts/data_preprocessing.py`.
   - Define/agree on format of `data/raw_kcc.csv` (columns: `query`, `answer` or equivalent).
   - Ensure output: `data/clean_kcc.csv` and `data/kcc_qa_pairs.json` (no duplicates, clean text).

2. **Embeddings & FAISS index**
   - Maintain and run `scripts/build_embeddings_faiss.py`.
   - Use Sentence Transformer `all-MiniLM-L6-v2` to generate embeddings from cleaned Q&A.
   - Build and save FAISS index + metadata so retrieval can run (outputs: `kcc_embeddings.pkl`, `kcc_faiss.index`, `meta.pkl` in `data/`).

3. **Data ownership**
   - Add/update `data/raw_kcc.csv` with real or extended KCC-style Q&A.
   - Document in README how to add new data and re-run the pipeline (preprocess → build embeddings/FAISS).

### Deliverables
- [ ] `scripts/data_preprocessing.py` working and documented  
- [ ] `scripts/build_embeddings_faiss.py` working and documented  
- [ ] `data/raw_kcc.csv` (and optionally more sample data)  
- [ ] Short README section: “How to update data and rebuild index”

### Files to own / edit
- `scripts/data_preprocessing.py`
- `scripts/build_embeddings_faiss.py`
- `data/raw_kcc.csv` (and cleaned outputs in `data/`)

---

## **MEMBER 2 — Backend, retrieval & APIs**

**Role:** Implement search logic, Watson chatbot, and Firebase storage so the app has answers and persistence.

### Tasks
1. **Semantic retrieval (offline answer)**
   - Maintain `retrieval.py`: load FAISS index and metadata, embed user query, run top-k search, format offline answer from retrieved Q&A.
   - Keep interface: `get_offline_answer(query, top_k)` → returns (results list, formatted offline answer string).

2. **IBM Watson (online mode / chatbot)**
   - In `retrieval.py`, implement `get_online_answer(query, offline_context)`.
   - Call IBM Watsonx text-generation API with correct model and prompt; parse response and return text.
   - Handle errors (no API key, network, rate limits) and return clear messages for the UI.

3. **Firebase storage**
   - Maintain `firebase_helper.py`: save each conversation (query, offline_answer, online_answer, timestamp) to Firebase Realtime Database at `/conversations`.
   - Use REST API; support config via env (e.g. `FIREBASE_DATABASE_URL`, `FIREBASE_API_KEY`).
   - Ensure `config.py` has all needed env vars (Watson, Firebase, paths, model name, TOP_K).

4. **Configuration**
   - Maintain `config.py`: paths, embedding model name, TOP_K, Watson URL/model, Firebase URL and any auth.

### Deliverables
- [ ] `retrieval.py`: `get_offline_answer()` and `get_online_answer()` working  
- [ ] `firebase_helper.py`: `save_to_firebase()` working with env config  
- [ ] `config.py` up to date and documented (which env vars are required/optional)  
- [ ] `.env.example` updated with Watson and Firebase variables (can coordinate with Member 3)

### Files to own / edit
- `retrieval.py`
- `firebase_helper.py`
- `config.py`
- `.env.example` (backend/API-related variables)

---

## **MEMBER 3 — UI, integration & documentation**

**Role:** Build the Streamlit app, connect to backend/Firebase, and document setup and usage for users and the team.

### Tasks
1. **Streamlit UI**
   - Maintain `app.py`: title, query input, “Get answer” button, offline/online mode toggle.
   - Display **Offline answer** (from Member 2’s retrieval) and **Online answer** (Watson) in clear, readable boxes.
   - Show loading states and errors (e.g. “Run build pipeline first”, “Set Watson/Firebase in .env”).

2. **Firebase & API key UX**
   - In sidebar (or settings): inputs for Firebase Database URL and optional API key; “Use these credentials” to apply for the session.
   - Optional: show a short message when a conversation is saved to Firebase (“Saved to Firebase”) or when save fails.

3. **Watson setup guidance**
   - In-app expander or help: “How to get Watson API for free” (trial / free tier links) and “How to set WATSONX_* in .env”.
   - Keep links and steps up to date (e.g. Watson free trial, Free Toolbox).

4. **Integration**
   - Ensure app calls Member 2’s functions: `get_offline_answer()`, `get_online_answer()`, `save_to_firebase()` with correct arguments.
   - Ensure `requirements.txt` has all dependencies (Streamlit, sentence-transformers, faiss-cpu, requests, python-dotenv, etc.).

5. **Documentation**
   - Maintain `README.md`: project overview, features, tech stack, setup (install → data → build pipeline → Firebase → Watson → run app), usage, sample queries, project structure.
   - Add a “Task assignment” section or link to this file so all 3 members know who does what.

### Deliverables
- [ ] `app.py` complete and wired to retrieval + Firebase  
- [ ] Sidebar/settings for Firebase URL and API key (paste and use)  
- [ ] Watson free-tier and .env instructions in the app  
- [ ] `README.md` and `requirements.txt` updated  
- [ ] Optional: 1–2 sentence “How to run” in README for evaluators

### Files to own / edit
- `app.py`
- `README.md`
- `requirements.txt`
- `TASK_ASSIGNMENT.md` (this file)

---

## **Integration checklist (all 3)**

- [ ] Member 1: Pipeline produces `clean_kcc.csv`, `kcc_qa_pairs.json`, FAISS index + meta in `data/`.
- [ ] Member 2: `get_offline_answer()` and `get_online_answer()` work; `save_to_firebase()` works with Firebase URL (and optional key) from env.
- [ ] Member 3: App runs end-to-end: query → offline answer + optional online answer → save to Firebase; README has full setup and run instructions.
- [ ] One person runs: `data_preprocessing.py` → `build_embeddings_faiss.py` → `streamlit run app.py` and verifies one sample query with offline + online + Firebase save.

---

## **Quick reference — who does what**

| Area                 | Owner    | Main files                                      |
|----------------------|----------|-------------------------------------------------|
| Data & FAISS index   | Member 1 | `scripts/data_preprocessing.py`, `scripts/build_embeddings_faiss.py`, `data/raw_kcc.csv` |
| Retrieval & APIs     | Member 2 | `retrieval.py`, `firebase_helper.py`, `config.py`, `.env.example` |
| UI & docs            | Member 3 | `app.py`, `README.md`, `requirements.txt`, `TASK_ASSIGNMENT.md` |
