"""
Save conversation data (query + answers) to Firebase Realtime Database.
Uses REST API; no Firebase SDK required.
"""
import os
from datetime import datetime, timezone
from typing import Optional

import requests


DEFAULT_FIREBASE_URL = "https://kishanagent-d81dc-default-rtdb.asia-southeast1.firebasedatabase.app"


def get_firebase_config():
    """Read from env or use default Firebase URL (e.g. from Streamlit session)."""
    url = (os.getenv("FIREBASE_DATABASE_URL") or "").strip().rstrip("/")
    if not url:
        url = DEFAULT_FIREBASE_URL
    key = (os.getenv("FIREBASE_API_KEY") or "").strip()
    return url or None, key or None


def save_to_firebase(
    query: str,
    offline_answer: str,
    online_answer: Optional[str] = None,
    *,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> bool:
    """
    Save one conversation entry to Firebase Realtime Database at /conversations.
    Uses base_url and api_key from env if not provided.
    Returns True if saved successfully.
    """
    url, key = get_firebase_config()
    if base_url is not None:
        url = (base_url or "").rstrip("/")
    if api_key is not None:
        key = api_key or None
    if not url:
        return False

    payload = {
        "query": query,
        "offline_answer": offline_answer,
        "online_answer": online_answer or "",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }

    path = f"{url}/conversations.json"
    params = {}
    if key:
        params["auth"] = key

    try:
        r = requests.post(path, json=payload, params=params or None, timeout=10)
        r.raise_for_status()
        return True
    except Exception:
        return False
