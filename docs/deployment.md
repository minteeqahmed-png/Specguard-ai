# Local deployment

The supported demonstration is a Windows Python 3.12 Streamlit application, with optional AMD inference reached through an SSH tunnel. No paid resources were provisioned during development.

```powershell
git clone https://github.com/minteeqahmed-png/Specguard-ai.git
cd Specguard-ai
git switch codex/specguard-mvp
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

Streamlit binds to 127.0.0.1:8501 by default. Keep this local during the demo. Do not open firewall ports for Streamlit or vLLM. On Linux/macOS use `.venv/bin/python` in place of `.\.venv\Scripts\python`.

The tested Windows environment is captured in `requirements-lock.txt`. To reproduce its exact packages use `python -m pip install -r requirements-lock.txt` in a fresh environment. `requirements.txt` pins the tested top-level versions. The lock is a Windows snapshot, not a cross-platform hardware inference environment.

For Live Mode, follow `amd_setup.md`, copy `.env.example` to `.env`, set the private server key and `SPECGUARD_MODE=live`, then restart Streamlit. The base URL includes `/v1`. Live uploads are sent to that endpoint only when extraction is requested. Never upload private customer information to an untrusted service.

The optional Dockerfile packages the local app; Docker build/run was not tested on this machine. Bind it locally:

```bash
docker build -t specguard-ai .
docker run --rm -p 127.0.0.1:8501:8501 specguard-ai
```

The container example runs Demo Mode. A local host SSH tunnel is not automatically reachable as `127.0.0.1` inside a container; run the native app for the documented live architecture. Hosted Streamlit and public URLs are intentionally not supplied. Public hosting requires a separately designed authenticated service boundary and transport security.

Stop local Streamlit using Ctrl+C in its terminal. Stop cloud containers and release resources using the provider console instructions in `amd_setup.md`; stopping the browser does not stop GPU billing.
