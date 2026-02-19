"""
Semantic query handling and optional IBM Watsonx Granite LLM integration.
Step 4: FAISS retrieval; Step 5: Online LLM (Watsonx) when enabled.
"""
import pickle
from pathlib import Path

import numpy as np
import faiss

from config import (
    EMBEDDING_MODEL,
    FAISS_INDEX,
    META_PKL,
    TOP_K,
    MIN_SIMILARITY,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)


def _get_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def _load_faiss_and_meta():
    index = faiss.read_index(str(FAISS_INDEX))
    with open(META_PKL, "rb") as f:
        meta = pickle.load(f)
    return index, meta


def _format_simple_for_farmer(answer: str) -> str:
    """Break answer into short, clear lines so farmers can read easily."""
    if not answer or not answer.strip():
        return answer
    # Split by period or newline, trim, keep non-empty
    parts = []
    for part in answer.replace("\n", ". ").split("."):
        part = part.strip()
        if part:
            parts.append(part + "." if not part.endswith(".") else part)
    if not parts:
        return answer.strip()
    return "\n".join(f"• {p}" for p in parts)


def get_offline_answer(query: str, top_k: int = TOP_K) -> tuple[list[dict], str]:
    """
    Embed query, run FAISS search, return list of {query, answer} and a simple, clean offline answer for farmers.
    Only shows answers above MIN_SIMILARITY; formats in short bullet points.
    """
    index, meta = _load_faiss_and_meta()
    model = _get_embedder()
    q_emb = model.encode([query], normalize_embeddings=True)
    q_emb = np.array(q_emb, dtype=np.float32)
    scores, indices = index.search(q_emb, min(top_k, index.ntotal))
    seen = set()
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or score < MIN_SIMILARITY:
            continue
        q = meta["queries"][idx]
        a = meta["answers"][idx]
        key = (q, a)
        if key in seen:
            continue
        seen.add(key)
        results.append({"query": q, "answer": a, "score": float(score)})
    # Sort by score (best first), take up to 3 to keep answer clean
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:3]
    if not results:
        offline_answer = (
            "हमें इस सवाल का सही जवाब डेटाबेस में नहीं मिला। "
            "कृपया सवाल थोड़ा अलग शब्दों में पूछें, या अपने क्षेत्र के कृषि अधिकारी से संपर्क करें.\n\n"
            "We could not find a close match for this question. Try asking in different words or contact your local agriculture office."
        )
        return [], offline_answer
    # One main answer, formatted simply; add more only if we have 2+ and they add value
    main = results[0]["answer"]
    offline_answer = _format_simple_for_farmer(main)
    if len(results) > 1 and results[1]["answer"].strip() != main.strip():
        other = results[1]["answer"].strip()
        if other and other[:50] != main[:50]:  # avoid duplicate
            offline_answer += "\n\nअधिक जानकारी (More):\n" + _format_simple_for_farmer(other)
    return results, offline_answer


def get_available_models(base_url: str = OLLAMA_BASE_URL) -> list[str]:
    """Fetch list of available models from Ollama."""
    try:
        import requests
        url = f"{base_url.rstrip('/')}/api/tags"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            return models
    except Exception:
        pass
    return []


def get_online_answer(query: str, offline_context: str, response_language: str = "English", model_name: str = OLLAMA_MODEL) -> str:
    """
    Call Ollama (local LLM) with query + offline context; return generated answer.
    response_language: e.g. "English", "Hindi", "Tamil", "Telugu", "Kannada" — answer will be in this language.
    model_name: specific model to use (e.g. "llama3", "granite4:micro").
    Returns error message if API not configured or request fails.
    """
    if not OLLAMA_BASE_URL:
        return "Online mode requires OLLAMA_BASE_URL in config.py"

    lang_instruction = f"Respond ONLY in {response_language}. Use simple words so farmers can understand."

    prompt = f"""You are a friendly agricultural expert helping Indian farmers. Your answer must be SIMPLE and CLEAR so that farmers with little formal education can understand.

RULES:
- Use very simple words. Avoid technical jargon; if you must use a term (e.g. pesticide name), explain in one short phrase.
- Write short sentences. One idea per line. Use bullet points (•) or numbers for steps.
- Base your answer ONLY on the reference below. Do not invent facts. If the reference does not fully cover the question, say so and give only the part that matches.
- Be correct and actionable: what to do, how much, when, and any caution.
- {lang_instruction}

Reference from Kisan Call Centre database:
{offline_context}

Farmer's question (they may have asked in their own language): {query}

Give a short, simple, correct answer that a farmer can follow easily:"""

    try:
        import requests
        url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
            }
        }
        
        # Short timeout for connection, longer for generation
        resp = requests.post(url, json=payload, timeout=120)
        
        if resp.status_code == 404:
             return f"Error: Model '{model_name}' not found. Run 'ollama pull {model_name}'"
             
        resp.raise_for_status()
        data = resp.json()
        
        if "response" in data:
            return data["response"].strip()
            
        return "Error: No response from Ollama."
        
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure it is running (e.g. 'ollama serve')."
    except Exception as e:
        return f"Online LLM error: {e}"
