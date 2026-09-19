from __future__ import annotations

import os
from typing import Any

import requests

API_BASE_URL = os.getenv("HIVER_API_BASE_URL", "http://127.0.0.1:8000")


def _request(method: str, path: str, **kwargs: Any) -> requests.Response:
    url = f"{API_BASE_URL.rstrip('/')}{path}"
    return requests.request(method, url, timeout=20, **kwargs)


def health_check() -> bool:
    try:
        response = _request("GET", "/health")
        response.raise_for_status()
        payload = response.json()
        return bool(payload.get("status") == "healthy")
    except Exception:
        return False


def fetch_intents() -> list[dict[str, Any]]:
    try:
        response = _request("GET", "/intents")
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return list(payload.get("intents", []))
        return list(payload)
    except Exception:
        return []


def chat(query: str, top_k: int = 5) -> dict[str, Any]:
    try:
        response = _request(
            "POST",
            "/chat",
            json={"query": query, "top_k": top_k},
        )
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # pragma: no cover - client side failure handling
        return {"error": str(exc), "answer": "The API is unavailable right now. Please try again later."}


def reset_memory() -> bool:
    try:
        response = _request("POST", "/reset")
        response.raise_for_status()
        payload = response.json()
        return payload.get("status") == "memory_reset"
    except Exception:
        return False
