import pytest

from specguard.ai_client import demo_extract
from specguard.parser import parse_document
from specguard.reconciliation import order_status, reconcile, resolve_issue

BASE = "Product: Football jersey\nQuantity: 500\nUnit: pieces\nColor: navy blue\nMaterial: polyester\nPrinting: sublimation\nDeadline: 2026-11-20"


def extract(text=BASE, name="buyer.txt"):
    return demo_extract(parse_document(name, text.encode()))


@pytest.mark.parametrize("old,new,field,severity", [
    ("500", "450", "quantity", "CRITICAL"),
    ("navy blue", "royal blue", "color", "MAJOR"),
    ("polyester", "cotton", "material", "MAJOR"),
    ("sublimation", "screen printing", "printing", "MAJOR"),
    ("Football jersey", "Custom hoodie", "product", "CRITICAL"),
    ("2026-11-20", "2026-11-21", "deadline", "MAJOR"),
    ("pieces", "sets", "unit", "CRITICAL"),
])
def test_conflicts(old, new, field, severity):
    issues = reconcile([extract(), extract(BASE.replace(old, new), "tech.txt")])
    issue = next(i for i in issues if i.field == field)
    assert issue.severity == severity
    assert len(issue.evidence) == 2
    assert order_status(issues, [], complete=True) == ("HOLD" if severity == "CRITICAL" else "REVIEW")


def test_size_total():
    good = demo_extract(parse_document("sizes.csv", b"size,quantity\nS,200\nM,300"))
    bad = demo_extract(parse_document("sizes.csv", b"size,quantity\nS,200\nM,200"))
    assert not reconcile([extract(), good])
    assert any(i.id.startswith("size_total") for i in reconcile([extract(), bad]))


def test_synonyms_and_case():
    other = BASE.replace("pieces", "PCS").replace("sublimation", "DYE SUBLIMATION").replace("navy blue", "NAVY   BLUE")
    assert not reconcile([extract(), extract(other, "tech.txt")])


def test_missing_not_contradictory():
    issues = reconcile([extract(BASE.replace("Material: polyester\n", ""))])
    assert [(i.kind, i.field) for i in issues] == [("missing", "material")]
    assert order_status(issues, [], complete=True) == "REVIEW"


def test_multiple_and_resolution_keeps_evidence():
    records = [extract(), extract(BASE.replace("500", "450").replace("navy blue", "royal blue"), "tech.txt")]
    original = [r.model_dump_json() for r in records]
    issues = reconcile(records)
    assert len(issues) == 2
    resolutions = [resolve_issue(i, "500" if i.field == "quantity" else "navy blue", "Buyer confirmed via reference A", "Reviewer") for i in issues]
    assert all(r.note for r in resolutions)
    assert [r.model_dump_json() for r in records] == original
    assert order_status(issues, resolutions, complete=True) == "READY"
    assert order_status(issues, resolutions, complete=False) == "REVIEW"
    with pytest.raises(ValueError):
        resolve_issue(issues[0], "500", " ", "Reviewer")


def test_failed_extraction_never_ready():
    assert order_status([], [], complete=False) == "REVIEW"
    assert order_status(reconcile([]), [], complete=False) == "REVIEW"


def test_correction_cannot_introduce_size_conflict():
    records = [extract(BASE.replace("Quantity: 500\n", "")), demo_extract(parse_document("sizes.csv", b"size,quantity\nS,200\nM,300"))]
    issues = reconcile(records)
    correction = resolve_issue(issues[0], "450", "Buyer says 450", "Reviewer")
    assert order_status(issues, [correction], complete=True, extractions=records) == "HOLD"
