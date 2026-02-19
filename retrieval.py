"""
Semantic query handling and optional IBM Watsonx Granite LLM integration.
Step 4: FAISS retrieval; Step 5: Online LLM (Watsonx) when enabled.
"""
import pickle
from pathlib import Path

import numpy as np
import faiss

from config import (
    BASE_DIR,
    DATA_DIR,
    EMBEDDING_MODEL,
    FAISS_INDEX,
    META_PKL,
    TOP_K,
    WATSONX_APIKEY,
    WATSONX_URL,
    WATSONX_PROJECT_ID,
    WATSONX_MODEL,
)


def _get_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def _load_faiss_and_meta():
    index = faiss.read_index(str(FAISS_INDEX))
    with open(META_PKL, "rb") as f:
        meta = pickle.load(f)
    return index, meta


def get_offline_answer(query: str, top_k: int = TOP_K) -> tuple[list[dict], str]:
    """
    Embed query, run FAISS search, return list of {query, answer} and formatted offline answer text.
    """
    index, meta = _load_faiss_and_meta()
    model = _get_embedder()
    q_emb = model.encode([query], normalize_embeddings=True)
    q_emb = np.array(q_emb, dtype=np.float32)
    scores, indices = index.search(q_emb, min(top_k, index.ntotal))
    seen = set()
    results = []
    for idx in indices[0]:
        if idx < 0:
            continue
        q = meta["queries"][idx]
        a = meta["answers"][idx]
        key = (q, a)
        if key in seen:
            continue
        seen.add(key)
        results.append({"query": q, "answer": a})
    lines = [f"• {r['answer']}" for r in results]
    offline_answer = "\n".join(lines) if lines else "No relevant answer found in the KCC database."
    return results, offline_answer


def get_online_answer(query: str, offline_context: str) -> str:
    """
    Call IBM Watsonx Granite LLM with query + offline context; return generated answer.
    Returns error message if API not configured or request fails.
    """
    if not WATSONX_APIKEY or not WATSONX_PROJECT_ID:
        return "Online mode requires WATSONX_APIKEY and WATSONX_PROJECT_ID in .env"

    prompt = f"""You are an agricultural expert helping Indian farmers. Use the following reference answers from the Kisan Call Centre database to give a clear, helpful reply. If the reference does not cover the question, say so and give brief general advice.

Reference answers from database:
{offline_context}

Farmer's question: {query}

Provide a concise, actionable answer in plain language:"""

    try:
        import requests
        url = WATSONX_URL.rstrip("?") if "?" in WATSONX_URL else WATSONX_URL + "?"
        if "version=" not in url:
            url = WATSONX_URL if "?" in WATSONX_URL else WATSONX_URL + "?version=2024-05-31"
        payload = {
            "model_id": WATSONX_MODEL,
            "input": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.2,
                "decoding_method": "greedy",
            },
            "project_id": WATSONX_PROJECT_ID,
        }
        headers = {
            "Authorization": f"Bearer {WATSONX_APIKEY}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # Watsonx text generation response structure
        if "results" in data and len(data["results"]) > 0:
            return data["results"][0].get("generated_text", "").strip()
        if "generated_text" in data:
            return str(data["generated_text"]).strip()
        return str(data)
    except Exception as e:
        return f"Online LLM error: {e}"
