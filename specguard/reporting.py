import csv
import io
import json
from datetime import datetime, timezone

from specguard.reconciliation import correction_checks, order_status


def full_report(extractions, issues, resolutions, errors, complete, elapsed, review=None):
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": extractions[0].mode if extractions else "unavailable",
        "status": order_status(issues, resolutions, complete=complete, extractions=extractions),
        "correction_checks": [i.model_dump(mode="json") for i in correction_checks(extractions, issues, resolutions)] if resolutions else [],
        "production_approval": "Not provided by this application; independent human authorization required.",
        "human_review": review,
        "complete": complete,
        "processing_seconds": elapsed,
        "inference_request_seconds": sum(e.inference_seconds or 0 for e in extractions) if any(e.mode == "live" for e in extractions) else None,
        "amd_hardware_verified": False,
        "extractions": [e.model_dump(mode="json") for e in extractions],
        "issues": [i.model_dump(mode="json") for i in issues],
        "resolution_history": [r.model_dump(mode="json") for r in resolutions],
        "errors": errors,
    }


def json_report(data):
    return json.dumps(data, indent=2, ensure_ascii=False)


def csv_cell(value):
    # Neutralize spreadsheet formulas from untrusted document content/review notes.
    text = str(value)
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else text


def conflict_csv(issues, resolutions):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["issue_id", "kind", "severity", "field", "title", "status", "source_evidence", "corrected_value", "reviewer", "resolution_note", "resolved_at"])
    latest = {r.issue_id: r for r in resolutions}
    for issue in issues:
        resolution = latest.get(issue.id)
        row = [issue.id, issue.kind, issue.severity, issue.field, issue.title, "resolved" if resolution else "open", json_report([e.model_dump(mode="json") for e in issue.evidence]), resolution.corrected_value if resolution else "", resolution.reviewer if resolution else "", resolution.note if resolution else "", resolution.created_at.isoformat() if resolution else ""]
        writer.writerow([csv_cell(value) for value in row])
    return output.getvalue()


def clarification_text(issues, resolutions, errors):
    resolved = {r.issue_id for r in resolutions}
    lines = ["Customer clarification draft — review before sending", ""]
    for issue in issues:
        if issue.id not in resolved:
            sources = sorted({o.source for o in issue.evidence})
            lines.append(f"- {issue.question}" + (f" Sources: {', '.join(sources)}." if sources else ""))
    if errors:
        lines.append("- Please provide readable, complete documents for any failed or incomplete inputs.")
    if len(lines) == 2:
        lines.append("No unresolved clarification questions. Independent human production approval is still required.")
    return "\n".join(lines)
