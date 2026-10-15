# Example order for judges

These files are entirely synthetic. They demonstrate one custom hoodie order in three formats. They are provided individually here and together in [Download all example documents](SpecGuard-Example-Documents.zip?raw=true).

| File | Contents | Download |
| --- | --- | --- |
| [buyer_order.txt](buyer_order.txt) | Buyer requests 300 black hoodies | [TXT](https://raw.githubusercontent.com/minteeqahmed-png/Specguard-ai/main/examples/buyer_order.txt) |
| [tech_pack.pdf](tech_pack.pdf) | Technical specification states 280 charcoal hoodies | [PDF](https://raw.githubusercontent.com/minteeqahmed-png/Specguard-ai/main/examples/tech_pack.pdf) |
| [size_quantities.csv](size_quantities.csv) | S: 75, M: 100, L: 75, XL: 50; total 300 | [CSV](https://raw.githubusercontent.com/minteeqahmed-png/Specguard-ai/main/examples/size_quantities.csv) |

## Run the example

1. Open [SpecGuard AI](https://specguard-ai-dev.streamlit.app/). The hosted app uses AMD Token Factory Live Mode; local runs default to deterministic Demo Mode.
2. Download and extract the ZIP, or download the three files separately. Choose **Upload documents** in the app.
3. Upload the TXT, PDF and CSV together. Do not upload the ZIP or this README.
4. Click **Extract facts**, inspect the evidence, then **Compare requirements**.
5. Expect **HOLD**, with the three findings below. Download **Full analysis JSON** to inspect the mode, model, quotes, locations and errors.

| Expected finding | Buyer / size CSV | Technical PDF | Severity |
| --- | --- | --- | --- |
| Quantity mismatch | 300 | 280 | CRITICAL |
| Color mismatch | black | charcoal | MAJOR |
| Size total mismatch | 300 | 280 | CRITICAL |

These expected results were verified locally and through a hosted AMD live request. Live model responses can fail validation or hit shared API quotas; those failures must stay explicit and block READY. See [hosted verification](../results/hosted_live_smoke.json).

## Try a human correction

Use synthetic confirmation notes only:

| Finding | Corrected value |
| --- | --- |
| Quantity | `300` |
| Color | `black` |
| Size quantities | `{"S":75,"M":100,"L":75,"XL":50}` |

Record a reviewer and note for each resolution. After all three corrections, expect READY under the configured rules. Original evidence remains unchanged; the exported report contains a separate correction history. READY does not authorize production.

For a case with no deliberate contradiction, choose **Synthetic sample -> 01_consistent** in the app. The full [27-case dataset](../sample_data/cases) also includes missing-data and material/printing conflicts.
