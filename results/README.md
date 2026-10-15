# Evaluation results

`demo_evaluation.json` is an actual local execution of `scripts/evaluate.py`, not a hand-authored benchmark. It records its mode, UTC timestamp, environment, per-case findings, status, errors and processing duration.

Run `python scripts/evaluate.py --output results/local_evaluation.json` to produce a fresh file. Files beginning `local_` are ignored to avoid committing private live outputs accidentally. For actual model evaluation, configure Live Mode and run `python scripts/evaluate.py --mode live --output results/local_amd_evaluation.json`.

Conflict precision = matched conflict IDs / predicted conflict IDs; recall = matched conflict IDs / expected conflict IDs; F1 is their harmonic mean. Conflict IDs distinguish fields and size-total rules within a case. Missing-information findings are excluded from conflict precision/recall. Their behavior is reflected in per-case issues and expected-status accuracy. This is issue-level rather than pairwise value-level scoring.

Field accuracy compares normalized field/value pairs per document. Its denominator includes every expected fact plus unmatched predicted facts, so missing fields, wrong values and extras are penalized. Evidence-location validity is enforced before results are accepted; quote semantics still require human review. Successfully processed documents count validated extractions, including partial orders with other failed inputs. Parsing failures remain in the report. Timing includes local parsing, extraction and reconciliation, with HTTP request duration listed separately in Live Mode.

This 27-case set deliberately shares the demo extractor's template format. Its perfect result is a regression result, not evidence of unseen-document accuracy, manufacturing savings or AMD performance. Live mode reports cannot independently prove GPU identity: correlate them with redacted server logs, container/model revisions and hardware telemetry.

Live evaluation stops after HTTP 401, 403 or 429 and still saves a partial report. `case_count` counts the cases checked, `dataset_case_count` counts all dataset cases, `not_run_cases` identifies those skipped, and `stopped_http_status` records the provider failure. `expected_documents` covers the whole dataset; field/conflict metrics cover only checked cases and must not be presented as full-dataset results when `not_run_cases` is nonempty.


## Hosted verification records

- `hosted_live_smoke.json`: one synthetic TXT/PDF/CSV order through the hosted app and AMD Token Factory, with model, verification status, expected conflicts and observed time. This is live inference evidence for the application, not independent GPU telemetry or a general benchmark.
- `hosted_demo_workflows.json`: browser checks of the conflicting and consistent sample orders, JSON downloads and state reset in Demo Mode.
- `hosted_upload_review.json`: synthetic uploads, all four exports, human corrections preserving original facts, and corrupt-PDF blocking in hosted Demo Mode.

UTC timestamps are recorded in the JSON. All files are synthetic check summaries with no credentials or private customer documents.
