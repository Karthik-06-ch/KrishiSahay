# Kisan Call Centre Query Assistant

An AI-powered agricultural helpdesk: **Firebase** for storing data, **IBM Watsonx** for the chatbot (LLM), and **FAISS** for offline KCC retrieval. Answers farmers' queries on crops, pests, fertilizers, and government schemes.

## Features

- **Data storage** – Conversation data (query + answers) saved to **Firebase Realtime Database**
- **Chatbot** – **IBM Watsonx** Granite LLM for natural-language answers (online mode)
- **Offline answers** – FAISS + KCC dataset when Watson is not used
- **Copy-paste setup** – Paste your Firebase URL and API key in the app sidebar or in `.env`

## Tech Stack

- **Firebase Realtime Database** – Store query/answer history
- **IBM Watsonx** – Chatbot (Granite LLM)
- **FAISS** + **sentence-transformers** – Offline semantic search over KCC data
- **Streamlit** – UI

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Data

Place your KCC data as `data/raw_kcc.csv` with columns `query` (or `question`) and `answer`. A sample file is included.

### 3. Build pipeline (one-time)

```bash
# Step 1: Clean data → clean_kcc.csv, kcc_qa_pairs.json
python scripts/data_preprocessing.py

# Step 2: Embeddings + FAISS index → kcc_embeddings.pkl, kcc_faiss.index, meta.pkl
python scripts/build_embeddings_faiss.py
```

### 4. Firebase (data storage)

- Default Firebase URL is pre-filled: `https://kishanagent-d81dc-default-rtdb.asia-southeast1.firebasedatabase.app`
- In the app sidebar, open **⚙️ Firebase & API keys** and paste your **Firebase Database URL** and optional **API Key**, then click **Use these credentials**. Or set `FIREBASE_DATABASE_URL` and `FIREBASE_API_KEY` in `.env`.
- Each query/answer is saved under `/conversations` in your Firebase DB.

### 5. Optional: IBM Watson (chatbot / online mode)

**Get Watson API for free:** [Try watsonx.ai](https://www.ibm.com/products/watsonx-ai/info/trial) (30-day trial) or [Free Toolbox](https://www.ibm.com/watsonx/get-started) (~300k tokens/month).

1. Sign up → create a project → get **Project ID** and **API key**.
2. Copy `.env.example` to `.env` and set `WATSONX_APIKEY`, `WATSONX_PROJECT_ID`, and `WATSONX_URL`.

### 6. Run the app

```bash
streamlit run app.py
```

## Usage

1. Enter an agricultural query (e.g. *How to control aphids in mustard?*).
2. Click **Get answer**.
3. **Offline answer** is always shown (from FAISS retrieval).
4. Check **Use online mode** to get Watson-generated answers (requires Watson API in `.env`).
5. Data is saved to Firebase automatically; paste your Firebase URL/API key in the sidebar if needed.

## Sample queries

- How to control aphids in mustard?
- What is the treatment for leaf spot in tomato?
- What fertilizer is recommended during flowering in wheat?
- How to apply for PM Kisan Samman Nidhi scheme?
- How to treat blight in potato crops?

## Project structure

```
hackathon/
├── app.py                 # Streamlit UI
├── config.py              # Paths and settings
├── retrieval.py           # FAISS retrieval + Watsonx LLM
├── firebase_helper.py     # Save conversations to Firebase
├── requirements.txt
├── data/
│   ├── raw_kcc.csv        # Input KCC Q&A (add your data)
│   ├── clean_kcc.csv      # After preprocessing
│   ├── kcc_qa_pairs.json
│   ├── kcc_embeddings.pkl
│   ├── kcc_faiss.index
│   └── meta.pkl
└── scripts/
    ├── data_preprocessing.py
    └── build_embeddings_faiss.py
```

## References

- Kisan Call Centre dataset: [data.gov.in](https://data.gov.in), [India Kisan Call Center](https://github.com/digitalagadvisory/india_kisan_call_center)
- IBM Watsonx: [watsonx.ai](https://www.ibm.com/watsonx), [Free trial](https://www.ibm.com/products/watsonx-ai/info/trial)
