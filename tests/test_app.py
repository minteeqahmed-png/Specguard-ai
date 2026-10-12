from streamlit.testing.v1 import AppTest
from pathlib import Path


def test_initial_app_starts():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
    assert not app.exception
    assert any("AMD inference not active" in item.value for item in app.warning)


def test_dashboard_extraction_and_comparison():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
    next(b for b in app.button if b.label == "Extract facts").click().run(timeout=30)
    assert not app.exception
    next(b for b in app.button if b.label == "Compare requirements").click().run(timeout=30)
    assert not app.exception
    assert app.metric[0].value == "HOLD"
    assert any("Quantity mismatch" in s.value for s in app.subheader)
    app.radio[0].set_value("Upload documents").run(timeout=30)
    assert not app.exception
    assert not app.metric
    assert next(b for b in app.button if b.label == "Compare requirements").disabled


def test_resolution_workflow():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
    next(b for b in app.button if b.label == "Extract facts").click().run(timeout=30)
    next(b for b in app.button if b.label == "Compare requirements").click().run(timeout=30)
    for issue, value in [("conflict:quantity", "500"), ("conflict:color", "navy blue"), ("size_total:0", '{"S":100,"M":150,"L":150,"XL":100}')]:
        next(x for x in app.text_input if x.key and x.key.startswith("value_") and x.key.endswith(issue)).set_value(value)
        next(x for x in app.text_input if x.key and x.key.startswith("reviewer_") and x.key.endswith(issue)).set_value("Demo reviewer")
        next(x for x in app.text_area if x.key and x.key.startswith("note_") and x.key.endswith(issue)).set_value("Synthetic buyer confirmation")
        # Forms remain in issue order; choose by their generated key.
        button = next(b for b in app.button if b.label == "Save resolution" and issue in b.key)
        button.click().run(timeout=30)
        assert not app.exception
    assert app.metric[0].value == "READY"
