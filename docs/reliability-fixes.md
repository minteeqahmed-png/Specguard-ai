# Reliability fixes — October 14, 2026

The original fault checks demonstrated two incorrect READY results: a model could return quantity 500 while quoting a genuine `Quantity: 450` line, or omit that conflicting line entirely. Schema validation and checking quote presence did not detect either error.

Live output now undergoes an independent comparison against every fact in supported labeled templates and exact `size,quantity` CSVs. The comparison checks values, source quotes, locations and coverage, including contradictory lines and individual size rows. Mismatches trigger the existing bounded retry; repeated failure leaves analysis incomplete. There is no substitution of deterministic facts for live output. Free-form or otherwise unsupported content retains its model extraction for inspection but blocks READY because coverage is unverified. The verification state is visible in the UI and exported JSON. Human review and issue resolutions do not override the gate.

This is verification of parsed template text, not a general semantic verifier, proof of PDF visual fidelity or production authorization. To proceed with an unsupported document, a reviewer must check its original contents and supply a supported template containing all relevant requirements. Keep the original with the order record.

PDF reading now uses pypdf 6.20.1; synthetic PDF generation uses ReportLab 5.0.1. The PyMuPDF dependency was removed and the sample PDFs regenerated. Project code is MIT, with third-party licenses retained separately. See [licensing](licensing.md).

## Verification performed

- `python -m pytest -q`: **86 passed**, Windows / Python 3.12.4. Includes both original false-READY paths, free-form omission, altered/omitted size rows, same-document contradiction, retry recovery, export gating, blank fields, encrypted PDFs, page limits and Streamlit workflows.
- The original nine controlled fault probes now all return REVIEW: wrong value with real quote, omitted quantity, timeout, HTTP 401/503/429, invalid JSON, truncated output and false quote. Both false-READY probes previously returned READY.
- Regenerated dataset: **27/27 expected statuses**, **81/81 documents**, **399/399 normalized field values**, no false-positive or false-negative conflicts. This is deterministic synthetic template testing, not a model accuracy benchmark. The measured run is in `results/demo_evaluation.json`.
- Fresh AMD Token Factory smoke test with `MiMo-V2.6-Flash`: all three initial synthetic documents verified; result **HOLD**, with `conflict:quantity`, `conflict:color` and `size_total:0`. No extraction errors. This tests one order, not production reliability.
- `pip check`: no broken requirements. `pip-audit` of the 51 pinned dependencies: no known vulnerabilities reported at audit time; this is not an OS/container security audit.

## Remaining boundaries

The supplied Token Factory trial terms are for development, with shared quotas and no production SLA. A prior longer live run stopped at HTTP 429; broader/repeated/adversarial live evaluation remains unfinished. Quota failures now explain the problem and keep analysis incomplete without automatic HTTP retries.

The app is a local prototype with in-memory review state and self-entered reviewer names. Team authentication, durable audit storage, production hosting and an appropriate production API agreement remain separate deployment work. Docker packaging has not passed a build/runtime check. The public URL and hosted AMD live smoke test were completed subsequently; see [verification record](../results/hosted_live_smoke.json). The recorded video, final presentation and event submission are still outstanding. These fixes do not claim production readiness or AMD acceptance.
