from streamlit.testing.v1 import AppTest
from pathlib import Path


def test_initial_app_starts():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
    assert not app.exception
    assert any("AMD inference not active" in item.value for item in app.warning)
