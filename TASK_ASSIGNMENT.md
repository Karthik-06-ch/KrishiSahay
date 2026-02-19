# KrishiSahay — Simple Task Split (3 Members)

Use this to divide work and to answer when the evaluator asks what you did.

---

## MEMBER 1 — Data & Search Index

**In one line:** I prepare the farmer Q&A data and build the search index so the app can find similar questions.

### What I do (3 steps)
1. **Clean the data** — Run `data_preprocessing.py`. It reads `raw_kcc.csv`, removes duplicates and bad rows, and saves `clean_kcc.csv` and `kcc_qa_pairs.json`.
2. **Build the search index** — Run `build_embeddings_faiss.py`. It converts each Q&A into a vector (number list) using a small AI model, then builds a FAISS index so we can quickly find similar questions.
3. **Keep the data file** — Add or update farmer questions and answers in `data/raw_kcc.csv` (columns: query, answer).

### My files
- `scripts/data_preprocessing.py`
- `scripts/build_embeddings_faiss.py`
- `data/raw_kcc.csv`

### When the evaluator asks
- **“What did you do?”** — “I handled the data pipeline. I clean the KCC dataset and build the FAISS index so when a farmer types a question, we can find the closest matching Q&A from the database.”
- **“How does it work?”** — “We use a sentence transformer to turn each question-answer into a vector. FAISS then finds the top similar ones when the user asks something new.”
- **“How do you run it?”** — “First run `python scripts/data_preprocessing.py`, then `python scripts/build_embeddings_faiss.py`. After that the app can use the index.”

---

## MEMBER 2 — Backend: Search, Watson & Firebase

**In one line:** I do the search (offline answer), call IBM Watson for the chatbot answer, and save every conversation to Firebase.

### What I do (3 steps)
1. **Offline answer** — In `retrieval.py`, when the user asks something, I load the FAISS index, convert their question to a vector, get the top matching Q&A from the dataset, and return that as the “offline answer.”
2. **Online answer (chatbot)** — In `retrieval.py`, I call the IBM Watsonx API with the user’s question and the offline answer as context. Watson returns a natural-language reply; I send that back as the “online answer.”
3. **Save to Firebase** — In `firebase_helper.py`, after we have both answers, I save the query, offline answer, online answer, and timestamp to the Firebase Realtime Database so we keep a history.

### My files
- `retrieval.py` (search + Watson)
- `firebase_helper.py` (save to Firebase)
- `config.py` (all URLs and API keys in one place)
- `.env.example` (template for Firebase and Watson keys)

### When the evaluator asks
- **“What did you do?”** — “I built the backend. I do the FAISS search for the offline answer, call IBM Watson for the chatbot answer, and save each conversation to Firebase.”
- **“How does the search work?”** — “We embed the user’s question with the same model we used for the dataset, then FAISS returns the most similar stored Q&A. That becomes the offline answer.”
- **“How does Watson come in?”** — “When online mode is on, we send the user’s question and the offline answer to Watson’s API. Watson generates a clearer, conversational reply.”
- **“Why Firebase?”** — “To store every query and answer so we have a history. We use the Firebase REST API; the URL and optional API key go in `.env` or the app sidebar.”

---

## MEMBER 3 — UI & Documentation

**In one line:** I built the Streamlit screen, connected it to the backend, and wrote the README so anyone can run the project.

### What I do (3 steps)
1. **Build the screen** — In `app.py`, I added the title, the text box for the query, the “Get answer” button, and the boxes that show the offline and online answers. I also added the sidebar where users can paste their Firebase URL and API key.
2. **Connect to the backend** — When the user clicks “Get answer,” the app calls Member 2’s functions: get the offline answer, then (if online mode is on) get the Watson answer, then save to Firebase. I show loading and errors (e.g. “Run the build scripts first,” “Set Watson keys in .env”).
3. **Document everything** — In `README.md` I wrote how to install, how to run the two scripts, how to set Firebase and Watson, and how to run the app. I also keep `requirements.txt` and this task file updated.

### My files
- `app.py` (Streamlit UI)
- `README.md`
- `requirements.txt`
- `TASK_ASSIGNMENT.md` (this file)

### When the evaluator asks
- **“What did you do?”** — “I did the frontend and docs. I built the Streamlit screen, wired it to the backend so it shows offline and online answers and saves to Firebase, and wrote the README so the team and evaluators can run the project.”
- **“How does the user interact?”** — “They type a question, click ‘Get answer.’ They always see the offline answer from our dataset. If they check ‘Use online mode’ and Watson is set up, they also see the Watson reply. Every conversation is saved to Firebase.”
- **“How do we run the full project?”** — “Install with `pip install -r requirements.txt`, run the two scripts in `scripts/` to build the index, then run `streamlit run app.py`. Firebase and Watson keys can be set in `.env` or pasted in the sidebar.”

---

## Quick summary for evaluator

| Member   | Role in one line |
|----------|-------------------|
| **Member 1** | Data: clean KCC data and build FAISS search index. |
| **Member 2** | Backend: FAISS search (offline answer), Watson API (online answer), Firebase save. |
| **Member 3** | UI and docs: Streamlit app + README and how to run. |

---

## Before demo — all 3 check

- [ ] Member 1: Run `data_preprocessing.py` then `build_embeddings_faiss.py` so the index exists.
- [ ] Member 2: `.env` has Firebase URL (and Watson keys if you want to show online mode).
- [ ] Member 3: Run `streamlit run app.py`, type a question, get offline answer and (if Watson is set) online answer, and see “Saved to Firebase.”
