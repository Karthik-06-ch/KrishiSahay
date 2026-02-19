import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from retrieval import get_online_answer
from firebase_helper import save_to_firebase
from config import OLLAMA_MODEL

def test_ollama():
    print(f"Testing Ollama with model: {OLLAMA_MODEL}...")
    query = "How to grow tomatoes?"
    context = "Tomatoes need sun and water."
    try:
        answer = get_online_answer(query, context, "English")
        print("\n--- Ollama Response ---")
        print(answer)
        print("-----------------------")
        if "Error" in answer:
            print("❌ Ollama verification failed.")
        else:
            print("✅ Ollama verification successful.")
    except Exception as e:
        print(f"❌ Ollama test crashed: {e}")

def test_firebase():
    print("\nTesting Firebase...")
    try:
        success = save_to_firebase("TEST_QUERY", "TEST_OFFLINE", "TEST_ONLINE_OLLAMA")
        if success:
            print("✅ Firebase save successful.")
        else:
            print("❌ Firebase save failed (check URL/Permissions).")
    except Exception as e:
        print(f"❌ Firebase test crashed: {e}")

if __name__ == "__main__":
    test_ollama()
    test_firebase()
