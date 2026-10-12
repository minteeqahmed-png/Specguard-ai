# Development stages and validation

## Phase 1 — foundation

Started with only the original repository README. Added Streamlit upload/previews, TXT/PDF/CSV parsing, bounded inputs, error handling, three synthetic sample documents, requirements, .gitignore and Windows startup instructions. Sixteen parsing/startup tests passed. Preserved as commit 7064a61.

## Extraction, reconciliation and review

Added validated facts, evidence checks, template Demo Mode, private vLLM adapter, deterministic comparisons, missing-data behavior, status calculation, resolution history, corrected-view validation and report downloads. Live integration tests use HTTPX MockTransport; they do not claim a running language model or AMD hardware. The 27-case synthetic set includes 81 parsed files and independent intent/evidence labels.

## Final local validation

64 tests passed on Windows / Python 3.12.4. Pytest exercises the Streamlit sample-to-extraction-to-HOLD flow, recording all required resolutions to reach READY, clearing stale state when inputs change, and error handling across parser/schema/API boundaries. `pip check` found no broken requirements. The actual evaluation is saved in results/demo_evaluation.json. The local HTTP Streamlit service was started and browser inspection confirmed real rendered controls and extracted facts.

No real AMD cloud resource was provisioned, no GPU model request was tested, no public deployment was made, and no changes were merged into main. Docker and Linux CI execution are distinct from the completed Windows checks and require their own verification.

Next: obtain approved AMD access, follow docs/amd_setup.md, run the live synthetic evaluation, inspect extraction errors, record GPU/process evidence and measured request latency, then record the five-minute demo and finalize slides for submission.
