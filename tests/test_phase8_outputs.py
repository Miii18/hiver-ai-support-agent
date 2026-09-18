from fastapi.testclient import TestClient
from src.api.app import app


def test_chat_response_schema():
    client = TestClient(app)
    r = client.post('/chat', json={'query': 'Status of my refund', 'top_k': 2})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get('confidence'), float)
    assert isinstance(data.get('sources'), list)
from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_phase8_success_banner_exact(capsys, monkeypatch) -> None:
    root = PROJECT_ROOT
    spec = importlib.util.spec_from_file_location('phase8_runner', root / 'scripts' / 'run_phase8.py')
    runner = importlib.util.module_from_spec(spec)
    assert spec and spec.loader is not None
    spec.loader.exec_module(runner)

    monkeypatch.setattr(runner, 'pytest', type('P', (), {'main': staticmethod(lambda args: 0)}))
    exit_code = runner.run()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert '# ====================================================== PHASE 8 COMPLETED SUCCESSFULLY' in captured.out
