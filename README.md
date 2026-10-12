# SpecGuard AI

Manufacturing Order Intelligence: compare customer messages, technical specifications and quantity tables before manufacturing begins.

## Phase 1

Local Streamlit upload and parsing for UTF-8 TXT, text-based PDF and comma-separated CSV. Includes document previews, source locations, missing-value warnings and clear errors for corrupt, scanned, oversized or unsupported input. Uploads remain in session memory. No AI inference or production approval occurs in this stage.

## Run on Windows (Python 3.12)

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

Open http://localhost:8501. Select the synthetic sample order or upload your documents. Maximum 10 MB per file, 50 PDF pages and 100,000 extracted characters.

```powershell
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python scripts/generate_initial.py
```

On Linux/macOS replace `.\.venv\Scripts\python` with `.venv/bin/python`.

AMD integration is incomplete. No GPU, credentials or paid services are needed for the local demo. Next: validated extraction, deterministic comparisons, human resolutions and exports.
