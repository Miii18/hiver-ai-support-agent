from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.app import app


def test_api_root() -> None:
    client = TestClient(app)
    r = client.get('/')
    assert r.status_code == 200
    data = r.json()
    assert 'name' in data and 'version' in data


def test_health_endpoint() -> None:
    client = TestClient(app)
    r = client.get('/health')
    assert r.status_code == 200
    data = r.json()
    assert data.get('status') == 'healthy'
    assert 'retriever_loaded' in data


def test_intents_endpoint() -> None:
    client = TestClient(app)
    r = client.get('/intents')
    assert r.status_code == 200
    data = r.json()
    assert 'intents' in data or isinstance(data, list)


def test_chat_and_reset() -> None:
    client = TestClient(app)
    r = client.post('/chat', json={'query': 'where is my order?', 'top_k': 3})
    assert r.status_code == 200
    data = r.json()
    assert 'answer' in data and 'detected_intent' in data

    r2 = client.post('/reset')
    assert r2.status_code == 200
    assert r2.json().get('status') == 'memory_reset'
