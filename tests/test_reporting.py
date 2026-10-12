import csv
import io

from specguard.reporting import clarification_text, conflict_csv, full_report
from specguard.schemas import Issue
from specguard.reconciliation import resolve_issue


def test_exports_and_formula_safety():
    issue = Issue(id="missing:color", field="color", kind="missing", severity="MAJOR", title="Missing color", question="Please provide color.")
    resolution = resolve_issue(issue, "navy blue", "=unsafe()", "Reviewer")
    row = list(csv.DictReader(io.StringIO(conflict_csv([issue], [resolution]))))[0]
    assert row["resolution_note"] == "'=unsafe()"
    assert row["status"] == "resolved"
    assert "Please provide color" in clarification_text([issue], [], [])
    report = full_report([], [issue], [], [], False, 0.1)
    assert report["status"] == "REVIEW"
    assert report["amd_hardware_verified"] is False
