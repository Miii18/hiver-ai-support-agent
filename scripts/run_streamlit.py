from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _already_in_streamlit() -> bool:
    try:
        import streamlit.runtime
        return streamlit.runtime.exists()
    except Exception:
        return False


def main() -> int:
    if _already_in_streamlit():
        # Running inside `streamlit run scripts/run_streamlit.py` — delegate to the real app.
        import runpy
        app_path = PROJECT_ROOT / "src" / "ui" / "streamlit_app.py"
        runpy.run_path(str(app_path), run_name="__main__")
        return 0
    app_path = PROJECT_ROOT / "src" / "ui" / "streamlit_app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", "8501", "--server.address", "0.0.0.0"]
    return subprocess.call(cmd, cwd=str(PROJECT_ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
