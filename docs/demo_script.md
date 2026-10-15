# Five-minute demonstration

Before recording: run tests, launch Streamlit, download the top-level examples ZIP, and confirm the mode banner. Use the actual running app, never fabricated screenshots or benchmark slides.

**0:00–0:40 — Problem.** A manufacturer receives one order in several formats. The buyer asks for 300 black hoodies, while the technical PDF says 280 in charcoal. Manual comparison can miss a discrepancy before fabric is cut.

**0:40–1:10 — Solution.** SpecGuard AI connects each extracted requirement to its source and applies deterministic comparisons. A person resolves uncertainty before authorizing production.

**1:10–3:10 — Demonstration.** Download the three documents from the examples ZIP, switch to Upload documents and upload the TXT, PDF and CSV. Extract facts, inspect quantity/color evidence and click Compare requirements. Show HOLD, the 300/280 discrepancy, charcoal/black mismatch and size sum of 300. Show the clarification draft. Record synthetic buyer confirmation: quantity 300, color black, size quantities `{"S":75,"M":100,"L":75,"XL":50}`. Explain the immutable original facts, reviewer notes and corrected-view recheck. Show READY and its separate human production-approval requirement. Export the full JSON audit.

**3:10–4:00 — AMD.** For the Token Factory route, show Live Mode, the configured provider/model, the connection check and a genuine end-to-end synthetic result with measured request timings. Hide the API key. Explain that this uses the AMD-hosted API; do not claim independent GPU telemetry. If quota prevents inference, show the explicit error and label any prior recorded result with its date. Demo Mode must be called deterministic template extraction. MI300X telemetry is relevant only if actually using the optional self-hosted route.

**4:00–4:40 — Evaluation.** Open the actual `results/demo_evaluation.json`. Explain that 27 deliberately constructed orders test deterministic behavior. Separate rule precision/recall, field values and document success from live model quality. These templates do not establish real-world accuracy or savings.

**4:40–5:00 — Close.** Expected benefits include clearer customer communication, traceable decisions and fewer avoidable specification errors. Next validate on independently labeled manufacturing documents, and expand live AMD inference evaluation within the available quota.

The pitch PDF, cover and hosted AMD verification are available in the repository. Recording and final event submission remain outstanding; this script is not a recorded video.
