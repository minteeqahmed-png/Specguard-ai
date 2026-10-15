# Submission copy

## Project title

SpecGuard AI — Evidence Before Production

## Short description

AMD-powered manufacturing order review that compares buyer messages, technical PDFs and size tables, flags conflicting facts and preserves human decisions.

## Long description

Manufacturers often receive one order in several formats: a buyer message, a technical PDF and a size spreadsheet. Differences in quantity, color or material can be missed during manual review. SpecGuard AI helps an order coordinator find and clarify these discrepancies before production.

The working Streamlit prototype accepts TXT, text-based PDF and CSV documents. AMD Token Factory's MiMo-V2.6-Flash extracts manufacturing facts with literal quotes and source locations. Pydantic validates the response, and independent checks verify values and coverage for supported labeled templates and size tables. Deterministic rules compare requirements and size totals. Failed processing and unverified completeness remain visible and block READY.

The dashboard links findings to their original evidence, drafts clarification questions and records human corrections in a separate history. A corrected view is reconciled again, so a correction cannot silently introduce a new inconsistency. Export formats include extraction JSON, conflict CSV, full analysis JSON and clarification TXT. READY is an assessment under configured rules, never automatic production authorization.

The hosted app has completed live AMD inference on a synthetic three-document order and correctly reported its quantity, color and size-total conflicts. The repository includes downloadable synthetic examples, source code, 86 automated tests, a 27-order deterministic regression set, verification records and MIT project licensing. The template regression results do not establish general model accuracy or customer savings.

Initial users are small and medium manufacturers' order coordinators. Expected benefits include less repetitive comparison, clearer customer questions and traceable decisions. The next stage is an independently labeled manufacturing pilot to measure review time and missed conflicts. Multi-item support, authenticated review, durable auditing and production API terms remain future work.

## Suggested submission selection

- Primary track from the project brief: **Reinvent Commerce** — manufacturing order intake and customer clarification.
- Related track: **Intelligent Industry** — specification quality before production.
- Confirm the selected challenge in your event form; this document does not change your event registration.

## Technology tags

AMD Token Factory, MiMo-V2.6-Flash, Python, Streamlit, Pydantic, HTTPX, pypdf, document extraction, manufacturing, human review.

## Links and files

- Application: https://specguard-ai-dev.streamlit.app/
- Repository: https://github.com/minteeqahmed-png/Specguard-ai
- Examples: https://github.com/minteeqahmed-png/Specguard-ai/tree/main/examples
- Pitch: [SpecGuard-AI-Pitch.pdf](../presentation/SpecGuard-AI-Pitch.pdf)
- Cover: [cover.png](../presentation/cover.png)
- Live evidence: [hosted_live_smoke.json](../results/hosted_live_smoke.json)
- Video: record the real workflow using [the demo script](demo_script.md), upload it to an allowed video host and add its real URL to the event form. No recording has been completed by this repository update.

Confirm participant/team registration, review the event form's current requirements and submit through the organizer portal. No event submission has been made automatically. [Official requirements](https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-iii)
