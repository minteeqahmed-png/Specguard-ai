"""Deterministic comparisons. Missing information is not a contradiction."""
import json
from collections import defaultdict

from specguard.schemas import Extraction, Issue, Observation, Resolution, Fact

MANDATORY = ("product", "quantity", "unit", "color", "material", "printing")
SYNONYMS = {"unit": {"pcs": "pieces", "piece": "pieces"}, "printing": {"dye sublimation": "sublimation", "screen-printing": "screen printing"}}


def normalize(field, value):
    if isinstance(value, dict):
        return json.dumps({k.strip().casefold(): v for k, v in sorted(value.items(), key=lambda item: item[0].casefold())}, sort_keys=True)
    if isinstance(value, str):
        value = " ".join(value.casefold().split())
        return SYNONYMS.get(field, {}).get(value, value)
    return value


def reconcile(extractions: list[Extraction]) -> list[Issue]:
    observations = defaultdict(list)
    for extraction in extractions:
        for fact in extraction.facts:
            observations[fact.field].append(Observation(source=extraction.source, sha256=extraction.sha256, fact=fact))
    issues = []
    for field in MANDATORY:
        if not observations[field]:
            issues.append(Issue(id=f"missing:{field}", field=field, kind="missing", severity="MAJOR", title=f"Missing required {field}", question=f"Please provide the required {field.replace('_', ' ')} for this order."))
    for field, items in observations.items():
        if field in {"instructions", "category"}:
            continue
        values = {normalize(field, item.fact.value) for item in items}
        if len(values) > 1:
            severity = "CRITICAL" if field in {"quantity", "product", "unit", "size_quantities"} else "MAJOR"
            choices = "; ".join(sorted(str(value) for value in values))
            issues.append(Issue(id=f"conflict:{field}", field=field, kind="conflict", severity=severity, title=f"{field.replace('_', ' ').title()} mismatch", evidence=items, question=f"Please confirm the correct {field.replace('_', ' ')} ({choices}) before production begins."))
    # Check every size table against its own stated total, or all order totals if absent.
    for index, size_obs in enumerate(observations["size_quantities"]):
        total = sum(size_obs.fact.value.values())
        targets = [o for o in observations["quantity"] if o.sha256 == size_obs.sha256 and o.source == size_obs.source] or observations["quantity"]
        mismatches = [o for o in targets if o.fact.value != total]
        if mismatches:
            issues.append(Issue(id=f"size_total:{index}", field="size_quantities", kind="conflict", severity="CRITICAL", title=f"Size total {total} differs from stated order quantity", evidence=[size_obs, *mismatches], question=f"Please reconcile the size-table total of {total} with the stated order quantity."))
    return issues


def resolve_issue(issue: Issue, corrected_value: str, note: str, reviewer: str) -> Resolution:
    # Validate corrections using the same field types without modifying any original fact.
    value = corrected_value.strip()
    try:
        typed = int(value) if issue.field == "quantity" else json.loads(value) if issue.field == "size_quantities" else value
        Fact(field=issue.field, value=typed, quote="Human resolution", location="review")
    except (ValueError, TypeError) as exc:
        raise ValueError("Enter a valid corrected value. Quantities use integers; size quantities use a JSON object such as {\"S\": 100}.") from exc
    return Resolution(issue_id=issue.id, corrected_value=value, note=note, reviewer=reviewer)


def correction_checks(extractions, issues, resolutions):
    """Recheck a separate view of reviewer-selected values; original records stay intact."""
    latest = {r.issue_id: r for r in resolutions}
    fields = {i.id: i.field for i in issues}
    corrections = []
    overridden = set()
    for issue_id, resolution in latest.items():
        if issue_id not in fields:
            continue
        field = fields[issue_id]
        value = resolution.corrected_value
        typed = int(value) if field == "quantity" else json.loads(value) if field == "size_quantities" else value
        fact = Fact(field=field, value=typed, quote=resolution.note, location="human review")
        corrections.append(Extraction(source=f"Human resolution: {resolution.reviewer}", sha256="human-review", mode="demo", facts=(fact,)))
        overridden.add(field)
    effective = [e.model_copy(update={"facts": tuple(f for f in e.facts if f.field not in overridden)}) for e in extractions]
    return [i.model_copy(update={"id": "correction:" + i.id}) for i in reconcile(effective + corrections)]


def order_status(issues: list[Issue], resolutions: list[Resolution], *, complete: bool, extractions=None) -> str:
    resolved = {r.issue_id for r in resolutions}
    unresolved = [issue for issue in issues if issue.id not in resolved]
    if resolutions and extractions is not None:
        unresolved += correction_checks(extractions, issues, resolutions)
    if any(issue.severity == "CRITICAL" for issue in unresolved):
        return "HOLD"
    if not complete or any(issue.severity == "MAJOR" for issue in unresolved):
        return "REVIEW"
    return "READY"
