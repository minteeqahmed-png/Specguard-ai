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


def test_document_and_reviewer_content_is_displayed_as_literal_text(monkeypatch):
    from specguard.ai_client import ModelClient
    from specguard.config import Config
    from specguard.pipeline import analyze

    marker = "![audit](https://example.invalid/audit-pixel)"
    filename = marker + ".txt"
    common = "Product: Hoodie\nQuantity: 10\nUnit: pieces\nMaterial: cotton\nPrinting: screen printing\n"
    result = analyze([(filename, (common + "Color: " + marker).encode()),
                      ("technical.txt", (common + "Color: black").encode())], ModelClient(Config()))
    result["errors"].append({"source": filename, "message": marker})
    result["complete"] = False
    monkeypatch.setattr("specguard.config.load_config", lambda: Config())
    monkeypatch.setattr("specguard.pipeline.analyze", lambda *args: result)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
    next(b for b in app.button if b.label == "Extract facts").click().run(timeout=30)
    next(b for b in app.button if b.label == "Compare requirements").click().run(timeout=30)
    question = next(i.question for i in result["issues"] if i.id == "conflict:color")
    assert question in [element.value for element in app.text]
    next(x for x in app.text_input if x.key and x.key.startswith("value_")).set_value(marker)
    next(x for x in app.text_input if x.key and x.key.startswith("reviewer_")).set_value(marker)
    next(x for x in app.text_area if x.key and x.key.startswith("note_")).set_value(marker)
    next(b for b in app.button if b.label == "Save resolution").click().run(timeout=30)
    next(x for x in app.text_input if x.label == "Final reviewer name").set_value(marker)
    next(x for x in app.text_area if x.label == "Review note").set_value(marker)
    app.checkbox[0].check()
    next(b for b in app.button if b.label == "Record human review").click().run(timeout=30)
    assert not app.exception
    assert any(marker in element.value for element in app.text)
    assert all(marker not in element.value for elements in (app.markdown, app.caption, app.error) for element in elements)
    assert all(marker not in element.label for element in app.expander)
