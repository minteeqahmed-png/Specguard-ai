# Synthetic evaluation data

All documents are invented. No real customer information is included.

`initial/` contains a buyer message for 500 navy jerseys, a PDF for 450 royal-blue jerseys, and a size CSV totaling 500. Expected findings: quantity mismatch, color mismatch, and size total versus PDF quantity mismatch.

`cases/` contains 27 three-document orders (81 documents): 6 consistent, 5 quantity mismatches, 4 color mismatches, 3 material mismatches, 3 printing mismatches, 3 missing-information cases and 3 multi-conflict cases. Products rotate through football jerseys, basketball uniforms, sports trousers, custom hoodies, embroidered shirts and team tracksuits.

`01_consistent` intentionally uses PCS/pieces, DYE SUBLIMATION/sublimation and case/whitespace variation without contradiction. Missing cases omit the same required field from both text documents; they require REVIEW without a direct conflict.

Run `python scripts/generate_dataset.py` to regenerate. The generator chooses deliberate mutations and writes intended issue IDs, status, field values, quotes and locations to each `ground_truth.json`. It does not call the reconciliation engine. Evaluation parses and extracts from actual TXT/PDF/CSV bytes before comparing with these labels.

This is a small template-based regression set, not a held-out benchmark. The deterministic demo extractor and fixtures share a defined input format. Perfect results measure implementation consistency, not general language understanding, model quality or manufacturing performance. Real-world assessment needs diverse independent documents, independent annotation, ambiguity cases, multi-item orders, extraction omissions and adversarial examples. PDF files are text-based and do not test OCR or complex table layout.
