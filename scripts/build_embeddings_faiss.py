"""
Steps 2 & 3: Embedding generation and FAISS index creation.
Uses Sentence Transformer (all-MiniLM-L6-v2), saves kcc_embeddings.pkl and FAISS index + meta.pkl.
"""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import faiss

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    DATA_DIR,
    CLEAN_CSV,
    EMBEDDING_MODEL,
    EMBEDDINGS_PKL,
    FAISS_INDEX,
    META_PKL,
)


def main():
    from sentence_transformers import SentenceTransformer

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CLEAN_CSV.exists():
        print("Run data_preprocessing.py first to create clean_kcc.csv")
        sys.exit(1)

    df = pd.read_csv(CLEAN_CSV)
    if "query" not in df.columns or "answer" not in df.columns:
        df = pd.read_csv(CLEAN_CSV)
        df.columns = ["query", "answer"]
    texts = (df["query"] + " " + df["answer"]).tolist()

    print(f"Loading model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    with open(EMBEDDINGS_PKL, "wb") as f:
        pickle.dump(embeddings, f)
    print(f"Saved embeddings to {EMBEDDINGS_PKL}")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    faiss.write_index(index, str(FAISS_INDEX))
    print(f"Saved FAISS index to {FAISS_INDEX}")

    meta = {
        "queries": df["query"].tolist(),
        "answers": df["answer"].tolist(),
        "dim": embeddings.shape[1],
    }
    with open(META_PKL, "wb") as f:
        pickle.dump(meta, f)
    print(f"Saved metadata to {META_PKL}")


if __name__ == "__main__":
    main()
