# Development stages and validation

## Phase 1 — foundation

Started with only the original repository README. Added Streamlit upload/previews, TXT/PDF/CSV parsing, bounded inputs, error handling, three synthetic sample documents, requirements, .gitignore and Windows startup instructions. Sixteen parsing/startup tests passed. Preserved as commit 7064a61.

## Extraction, reconciliation and review

Added validated facts, evidence checks, template Demo Mode, private vLLM adapter, deterministic comparisons, missing-data behavior, status calculation, resolution history, corrected-view validation and report downloads. Live integration tests use HTTPX MockTransport; they do not claim a running language model or AMD hardware. The 27-case synthetic set includes 81 parsed files and independent intent/evidence labels.

## Initial local validation (historical)

64 tests passed on Windows / Python 3.12.4. Pytest exercises the Streamlit sample-to-extraction-to-HOLD flow, recording all required resolutions to reach READY, clearing stale state when inputs change, and error handling across parser/schema/API boundaries. `pip check` found no broken requirements. The actual evaluation is saved in results/demo_evaluation.json. The local HTTP Streamlit service was started and browser inspection confirmed real rendered controls and extracted facts.

At this initial stage AMD requests, public deployment and merging were pending. Later milestones below supersede those initial limitations. Docker build/runtime validation is still incomplete.

## Hosted integration and final repository preparation

AMD Token Factory MiMo-V2.6-Flash has processed real requests from the hosted Streamlit app. The three-document synthetic hoodie upload passed independent template/source checks and produced all three intended HOLD findings; its actual summary is in results/hosted_live_smoke.json. Hosted Demo Mode upload, correction, export and failed-PDF checks also passed. The test suite grew to 86 passing tests, with GitHub Linux CI passing.

The final repository preparation adds a top-level examples folder with individual TXT/PDF/CSV files, expected results and a ZIP; a sidebar download; an eight-slide pitch PDF; a cover; and current submission descriptions. Review and merge completion is tracked by GitHub PR #1.

Remaining: record the real demo video and complete the event submission. Broader model evaluation, independent GPU telemetry, production access controls and durable auditing are separate future validation work.
