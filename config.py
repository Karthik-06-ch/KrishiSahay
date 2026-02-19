"""Configuration for Kisan Call Centre Query Assistant."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_CSV = DATA_DIR / "raw_kcc.csv"
CLEAN_CSV = DATA_DIR / "clean_kcc.csv"
QA_JSON = DATA_DIR / "kcc_qa_pairs.json"
EMBEDDINGS_PKL = DATA_DIR / "kcc_embeddings.pkl"
FAISS_INDEX = DATA_DIR / "kcc_faiss.index"
META_PKL = DATA_DIR / "meta.pkl"

# Embedding model (Sentence Transformer)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# FAISS search
TOP_K = 5

# IBM Watsonx (online mode / chatbot)
WATSONX_APIKEY = os.getenv("WATSONX_APIKEY")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2024-05-31")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_MODEL = "ibm/granite-3-8b-instruct"

# Firebase Realtime Database (for storing query/answer data)
FIREBASE_DATABASE_URL = os.getenv(
    "FIREBASE_DATABASE_URL",
    "https://kishanagent-d81dc-default-rtdb.asia-southeast1.firebasedatabase.app",
).rstrip("/")
# Optional: API key or auth token for secured rules (paste from Firebase Console)
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
