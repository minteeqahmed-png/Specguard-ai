# SpecGuard AI

**Manufacturing Order Intelligence — evidence before production.**

SpecGuard AI compares customer messages, technical PDFs and size spreadsheets before manufacturing begins. It turns document requirements into validated facts, flags contradictions, shows their source evidence and records human decisions without rewriting the original facts.

**Working local MVP. AMD GPU integration is incomplete.** Demo Mode is deterministic template extraction and never claims to run AMD inference. Live Mode has a tested HTTP adapter but still needs an actual AMD-hosted model and execution evidence.

## Quick start — Windows / Python 3.12

```powershell
git clone https://github.com/minteeqahmed-png/Specguard-ai.git
cd Specguard-ai
git switch codex/specguard-mvp
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

Open http://localhost:8501. No account, API key, GPU or paid service is needed for Demo Mode. After the review branch is merged, use main instead of switching branches. On Linux/macOS replace `.\.venv\Scripts\python` with `.venv/bin/python`.

1. Select the initial synthetic sample or upload one order's documents.
2. Click **Extract facts** and inspect the values and source references.
3. Click **Compare requirements**. The initial example produces HOLD for quantity/size conflicts and flags navy versus royal blue.
4. Record corrected values, a reviewer and confirmation notes. Corrections are rechecked separately; original source values remain intact.
5. Record human review and download the reports before closing the session.

## What works

- Multiple UTF-8 TXT/CSV and digital PDF inputs, with previews and filename, line/page/record evidence.
- Errors for empty, corrupt, unsupported, oversized or incorrectly encoded input; warnings for missing CSV cells and unread PDF pages.
- Pydantic-validated extraction with evidence quote checks. Demo Mode supports labeled templates; Live Mode uses a private OpenAI-compatible vLLM endpoint.
- Deterministic quantity, size-total, product, unit, color, material, printing, embroidery, secondary-color and deadline comparisons.
- HOLD for unresolved critical conflicts; REVIEW for major findings, missing mandatory information or incomplete processing; READY only when configured checks clear. **READY never authorizes production.**
- Separate human corrections, reviewer notes, correction validation and review history.
- Extraction JSON, conflict CSV, full-analysis JSON and customer-clarification TXT downloads.
- 27 synthetic evaluation cases, Pytest coverage and GitHub Actions configuration.

## Configuration and AMD

Copy `.env.example` to `.env` only when configuring the live endpoint. The app reads `SPECGUARD_MODE`, `VLLM_BASE_URL`, `VLLM_API_KEY`, `VLLM_MODEL` and `REQUEST_TIMEOUT`. Use `SPECGUARD_MODE=live` to enable real requests; the base URL must include `/v1`. The intended model is `Qwen/Qwen2.5-7B-Instruct`.

[AMD setup](docs/amd_setup.md) covers MI300X, ROCm/vLLM, model serving, private SSH forwarding, test requests, telemetry and shutdown. API reachability alone does not prove AMD hardware execution. Timeouts, failed requests, invalid JSON/schema and unverifiable quotes remain explicit failures; the app never falls back silently to demo extraction.

## Testing and actual evaluation

```powershell
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m pip check
.\.venv\Scripts\python scripts/evaluate.py --output results/local_evaluation.json
```

Local validation on October 12, 2026: **64 tests passed** on Windows / Python 3.12.4; no broken package requirements. Includes parsing, invalid inputs, schema checks, conflicts, missing fields, correction safety, API mocks, exports and Streamlit extraction/comparison/resolution flows.

The checked-in [demo evaluation](results/demo_evaluation.json) processed **81/81 documents** across **27 cases**: conflict precision/recall/F1 1.0, zero false positives/negatives, 399/399 expected field values matched, and 27/27 expected statuses. The actual run took approximately 0.98 seconds. This is deterministic evaluation on a small constructed template set, **not real-world accuracy, AMD latency or a model benchmark**. The result file records the exact timing and mode.

[Evaluation methodology](results/README.md) explains metric denominators. [Dataset notes](sample_data/README.md) describe case construction and limitations. `requirements-lock.txt` records the tested Windows package environment.

## Architecture and files

Actual local Demo Mode screenshot (synthetic order, October 12, 2026):

![Quantity mismatch with source evidence](docs/screenshots/dashboard.png)

`app.py` is the Streamlit interface. `specguard/parser.py` parses inputs; `schemas.py` validates facts; `ai_client.py` handles demo/live extraction; `reconciliation.py` compares facts and corrected views; `pipeline.py` preserves failures; `reporting.py` builds exports; `config.py` loads settings. See the [architecture diagram and rules](docs/architecture.md).

The application holds uploaded documents and review state in memory. It does not silently save private files, send clarification messages or make production decisions. Changing inputs or re-extracting clears prior results and review state.

## Limits and remaining work

One product and one order per analysis. Maximum 12 documents / 30 MB total; 10 MB per file; 50 PDF pages; 100,000 extracted characters per file. Live extraction accepts at most 16,000 characters per document and fails rather than silently truncating. No OCR, XLSX, fuzzy color matching, unit conversion, multi-item reconciliation or persistent signed audit database. PDF table layout can be ambiguous. Matching a quote to the document does not prove the model selected every relevant fact or interpreted it correctly.

AMD serving, end-to-end GPU execution, model accuracy/latency and GPU utilization evidence remain untested. Docker packaging is supplied but has not been built here. Public hosting, a recorded video, final slides and the event submission are not completed.

## Documentation

- [Local deployment](docs/deployment.md)
- [AMD setup and evidence checklist](docs/amd_setup.md)
- [Architecture](docs/architecture.md)
- [Five-minute demo script](docs/demo_script.md)
- [Pitch content](docs/pitch.md)
- [Development stages](docs/development.md)

Expected business benefits include less manual comparison, clearer customer questions and better traceability. Savings and customer outcomes remain unmeasured. Future per-order or monthly subscription pricing is a hypothesis, not an implemented payment feature.

## License

GNU AGPL-3.0-only; see [LICENSE](LICENSE) and [licensing notes](docs/licensing.md). The requested PyMuPDF dependency uses AGPL or commercial licensing, so this application is not presented as MIT-only. Third-party packages and model weights retain their own licenses.
