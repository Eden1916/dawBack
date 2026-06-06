"""
Simple in-memory cache to avoid redundant OpenFDA and Translate API calls.
For production, swap this with Redis.
"""
import time

_store: dict = {}

DEFAULT_TTL = 60 * 60  # 1 hour


def get(key: str):
    entry = _store.get(key)
    if entry is None:
        return None
    if time.time() > entry["expires_at"]:
        del _store[key]
        return None
    return entry["value"]


def set(key: str, value, ttl: int = DEFAULT_TTL):
    _store[key] = {
        "value": value,
        "expires_at": time.time() + ttl,
    }


def clear():
    """Clear all cached entries — useful after a service change."""
    _store.clear()
