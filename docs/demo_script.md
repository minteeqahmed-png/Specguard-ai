# Five-minute demonstration

Before recording: run tests, launch Streamlit, choose the initial synthetic order, and confirm the mode banner. Use the actual running app, never fabricated screenshots or benchmark slides.

**0:00–0:40 — Problem.** A manufacturer receives one order in several formats. The buyer asks for 500 navy jerseys, while the technical PDF says 450 in royal blue. Manual comparison can miss a discrepancy before fabric is cut.

**0:40–1:10 — Solution.** SpecGuard AI connects each extracted requirement to its source and applies deterministic comparisons. A person resolves uncertainty before authorizing production.

**1:10–3:10 — Demonstration.** Download the three sample documents, switch to Upload documents and upload the TXT, PDF and CSV. Extract facts, inspect quantity/color evidence and click Compare requirements. Show HOLD, the 500/450 discrepancy, royal/navy mismatch and size sum of 500. Show the clarification draft. Record synthetic buyer confirmation: quantity 500, color navy blue, size quantities `{"S":100,"M":150,"L":150,"XL":100}`. Explain the immutable original facts, reviewer notes and corrected-view recheck. Show READY and its separate human production-approval requirement. Export the full JSON audit.

**3:10–4:00 — AMD.** If actual inference is available, show the live mode, model connection, server process, MI300X telemetry and measured request timings alongside an end-to-end result. Otherwise say explicitly: “This demonstration uses deterministic template extraction. The AMD adapter is implemented, but GPU integration is pending.” Never imply demo timings are GPU timings.

**4:00–4:40 — Evaluation.** Open the actual `results/demo_evaluation.json`. Explain that 27 deliberately constructed orders test deterministic behavior. Separate rule precision/recall, field values and document success from live model quality. These templates do not establish real-world accuracy or savings.

**4:40–5:00 — Close.** Expected benefits include clearer customer communication, traceable decisions and fewer avoidable specification errors. Next validate on independently labeled manufacturing documents, and measure real AMD inference.

Recording, pitch-slide production, AMD evidence capture and final submission remain human follow-up work; no video or external submission has been fabricated.
