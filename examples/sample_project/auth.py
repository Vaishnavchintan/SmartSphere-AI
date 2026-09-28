"""
Authentication and session management module.
"""

import time
import hashlib
import os

SESSION_STORE = {}

def create_insecure_token(user_id):
    # Weak pseudo-random token generation with MD5
    timestamp = str(time.time())
    raw_str = f"{user_id}:{timestamp}"
    token = hashlib.md5(raw_str.encode('utf-8')).hexdigest()
    SESSION_STORE[token] = {
        "user_id": user_id,
        "created_at": time.time(),
        "expires_at": time.time() + 3600
    }
    return token

def validate_token(token):
    session = SESSION_STORE.get(token)
    if not session:
        return False
    if time.time() > session["expires_at"]:
        del SESSION_STORE[token]
        return False
    return True
