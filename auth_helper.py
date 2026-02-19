"""
Simple login and registration using Firebase Realtime Database.
Stores users under /users with hashed passwords (for demo only; use Firebase Auth in production).
"""
import hashlib
import os
import re
from typing import Optional, Tuple

import requests

from firebase_helper import get_firebase_config


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _firebase_key_for_email(email: str) -> str:
    return re.sub(r"[.#$\[\]]", "_", email.strip().lower())


def register_user(name: str, email: str, password: str) -> Tuple[bool, str]:
    """
    Register a new user: store name, email, hashed password in Firebase /users.
    Returns (success, message).
    """
    name = (name or "").strip()
    email = (email or "").strip().lower()
    if not name or not email or not password:
        return False, "Name, email and password are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if "@" not in email:
        return False, "Please enter a valid email."

    url, key = get_firebase_config()
    if not url:
        return False, "Firebase not configured. Set FIREBASE_DATABASE_URL in Settings."

    path = f"{url}/users/{_firebase_key_for_email(email)}.json"
    params = {"auth": key} if key else None
    # Check if user already exists
    try:
        r = requests.get(path, params=params, timeout=10)
        if r.status_code == 200 and r.json() is not None:
            return False, "This email is already registered. Please login."
    except Exception:
        pass

    payload = {
        "name": name,
        "email": email,
        "password_hash": _hash_password(password),
    }
    try:
        r = requests.put(path, json=payload, params=params, timeout=10)
        r.raise_for_status()
        return True, "Registration successful. Please login."
    except Exception as e:
        return False, f"Could not register: {e}"


def login_user(email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Login: fetch user from Firebase, compare password hash.
    Returns (success, message, user_dict with name and email if success).
    """
    email = (email or "").strip().lower()
    if not email or not password:
        return False, "Email and password are required.", None

    url, key = get_firebase_config()
    if not url:
        return False, "Firebase not configured. Set FIREBASE_DATABASE_URL in Settings.", None

    path = f"{url}/users/{_firebase_key_for_email(email)}.json"
    params = {"auth": key} if key else None
    try:
        r = requests.get(path, params=params, timeout=10)
        if r.status_code != 200:
            return False, "Login failed. Check email and password.", None
        data = r.json()
        if not data or not isinstance(data, dict):
            return False, "No account found with this email. Please register.", None
        stored_hash = data.get("password_hash") or ""
        if stored_hash != _hash_password(password):
            return False, "Incorrect password.", None
        return True, "Welcome!", {"name": data.get("name") or email, "email": data.get("email") or email}
    except Exception as e:
        return False, f"Login failed: {e}", None
