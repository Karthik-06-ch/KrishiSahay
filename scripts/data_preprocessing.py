"""
Step 1: Data Preprocessing for Kisan Call Centre Query Assistant.
Loads raw_kcc.csv, cleans and standardizes Q&A pairs, saves clean_kcc.csv and kcc_qa_pairs.json.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR, RAW_CSV, CLEAN_CSV, QA_JSON


def normalize_text(text: str) -> str:
    """Clean and normalize text: strip, collapse whitespace, remove nulls."""
    if not text or (isinstance(text, float) and pd.isna(text)):
        return ""
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def detect_qa_columns(df: pd.DataFrame) -> tuple[str, str]:
    """Detect question and answer column names (case-insensitive)."""
    cols = [c.lower() for c in df.columns]
    q_candidates = ["query", "question", "q", "queries", "faq_question"]
    a_candidates = ["answer", "response", "a", "ans", "faq_answer", "solution"]
    q_col = None
    a_col = None
    for q in q_candidates:
        for i, c in enumerate(df.columns):
            if c.lower() == q or q in c.lower():
                q_col = df.columns[i]
                break
        if q_col is not None:
            break
    if q_col is None and len(df.columns) >= 1:
        q_col = df.columns[0]
    for a in a_candidates:
        for i, c in enumerate(df.columns):
            if c.lower() == a or a in c.lower():
                a_col = df.columns[i]
                break
        if a_col is not None:
            break
    if a_col is None and len(df.columns) >= 2:
        a_col = df.columns[1]
    return q_col or df.columns[0], a_col or df.columns[-1]


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RAW_CSV.exists():
        print(f"Raw data not found: {RAW_CSV}")
        print("Please add raw_kcc.csv with columns: query (or question), answer")
        sys.exit(1)

    df = pd.read_csv(RAW_CSV)
    q_col, a_col = detect_qa_columns(df)
    print(f"Using columns: question='{q_col}', answer='{a_col}'")

    df["query"] = df[q_col].map(normalize_text)
    df["answer"] = df[a_col].map(normalize_text)
    df = df[["query", "answer"]]

    # Drop empty or duplicate rows
    df = df[(df["query"].str.len() > 0) & (df["answer"].str.len() > 0)]
    df = df.drop_duplicates(subset=["query", "answer"])
    df = df.reset_index(drop=True)

    df.to_csv(CLEAN_CSV, index=False)
    qa_pairs = [{"query": r["query"], "answer": r["answer"]} for _, r in df.iterrows()]
    with open(QA_JSON, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)

    print(f"Cleaned {len(df)} Q&A pairs. Saved to {CLEAN_CSV} and {QA_JSON}")


if __name__ == "__main__":
    main()
