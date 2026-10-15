# Pitch content and speaker notes

The completed [eight-slide PDF](../presentation/SpecGuard-AI-Pitch.pdf) and [cover](../presentation/cover.png) are included in the repository. Regenerate the PDF and vector cover with `python scripts/build_presentation.py`.

1. **Clarity before production.** Introduce SpecGuard AI as a review assistant for manufacturing order coordinators. Show the working hosted URL.
2. **One order, three sources.** The synthetic buyer asks for 300 black hoodies; the technical PDF says 280 charcoal hoodies; the size CSV totals 300. Explain the three intended conflicts.
3. **The product.** Upload, inspect source facts, compare, record corrections and export the evidence/review record.
4. **AMD's role.** MiMo-V2.6-Flash via AMD Token Factory performs live fact extraction. Python parses inputs, Pydantic and source checks validate output, deterministic rules compare values, and people decide what to confirm.
5. **Boundaries.** HOLD for critical conflicts; REVIEW for missing data, incomplete processing or unverified completeness; READY only under configured rules. Independent human production approval remains necessary.
6. **Evidence.** 86 tests, 27 deterministic synthetic cases and a hosted AMD smoke test. The live three-document hoodie example took 20.44 seconds once. Do not present template results as model accuracy or one smoke test as production reliability.
7. **Business potential.** Expected benefits are less manual comparison and better traceability. Pilot measurements, pricing and savings are not yet validated.
8. **Try it.** Point judges to the hosted app, top-level examples folder, source code and verification records.

The project brief targets Reinvent Commerce; Intelligent Industry is also relevant to manufacturing quality. Select the appropriate challenge in the actual submission form. The final recording and event submission still require completion.
