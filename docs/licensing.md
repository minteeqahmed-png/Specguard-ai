# Licensing

SpecGuard AI project code is licensed under MIT; see `LICENSE`. Copyright 2026 SpecGuard AI contributors. This revision replaces PyMuPDF with pypdf for extraction and ReportLab for synthetic PDF generation. PyMuPDF is no longer a dependency. Earlier revisions retain their published license.

The event requires original, MIT-compliant submissions: [AMD ACT III requirements](https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-iii). Removing the AGPL PDF dependency addresses that project licensing blocker; it does not certify event eligibility or replace submission review.

Third-party distributions retain their own licenses and notices. Do not relabel them MIT or strip their license files when redistributing an environment or container:

| Dependency | License / source |
| --- | --- |
| pypdf | BSD-3-Clause; [project license](https://github.com/py-pdf/pypdf/blob/main/LICENSE) |
| ReportLab open-source toolkit | BSD; [developer FAQ](https://docs.reportlab.com/developerfaqs/) |
| Streamlit, PyArrow, Requests | Apache-2.0 |
| Pydantic, Pytest | MIT |
| HTTPX, python-dotenv | BSD-3-Clause in the pinned distributions |
| certifi (transitive) | MPL-2.0; its unmodified certificate bundle remains under its own license |

`requirements-lock.txt` records the checked dependency versions. Their installed distributions include upstream notices, including bundled component notices. Model weights, hosted API services and any self-hosted GPU image have separate terms and are not relicensed by this repository. No model weights or API credentials are distributed here.
