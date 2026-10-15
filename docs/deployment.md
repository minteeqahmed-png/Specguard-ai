# Deployment

## Free demo on Streamlit Community Cloud

**[Open SpecGuard AI Demo](https://specguard-ai-dev.streamlit.app/)** — public Demo Mode deployment. The owner confirmed that it loads on October 15, 2026; the complete hosted workflow has not been independently verified.

Use [Streamlit Community Cloud](https://share.streamlit.io/) for the public demonstration. Choose Community Cloud, not the separate Snowflake trial. Account sign-in and GitHub authorization are completed by the repository owner. The steps below describe how to reproduce the deployment.

1. Sign in with GitHub and choose **Create app**, then **Yup, I have an app** (or the equivalent existing GitHub app option).
2. Select repository `minteeqahmed-png/Specguard-ai`.
3. Select branch `codex/specguard-mvp`. The implementation is on this review branch; main does not yet contain the app.
4. Set the main file path to `app.py`.
5. In **Advanced settings**, choose **Python 3.12** and leave **Secrets empty**. The app defaults to Demo Mode without credentials.
6. Optionally choose an available subdomain, then click **Deploy**. Wait for dependency installation and app startup. Streamlit supplies the actual `*.streamlit.app` URL; do not assume a particular name is available.
7. Verify the deployed app shows **DEMO MODE — AMD inference not active**. Extract the initial synthetic order and compare requirements. Expect **HOLD**, quantity and color conflicts, and a size-total conflict. Export the full JSON and check the reported mode is demo. Select `01_consistent`, extract and compare again; expect READY under the configured rules, with independent human production approval still required.

The repository includes `requirements.txt` and the theme. The shared config deliberately does not force a server address; Community Cloud controls network routing. `.env` and `.streamlit/secrets.toml` are excluded from Git and Docker build contexts. No AMD key is needed or uploaded for the public demo. This demo uses labeled templates; it is not live AMD inference. Use synthetic documents for public demonstrations.

[Official deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) describe repository selection, Python version and the Secrets form. Hosting changes pushed to the selected branch trigger updates. Free hosting has resource limits and is not a production availability guarantee.

## Live hosted access

Keep the initial public deployment in Demo Mode. Before exposing shared AMD inference, configure and verify viewer access restrictions. Store keys in the host's secret settings, never GitHub or a public file. The current app has no built-in login and review state is session-only. The AMD Token Factory trial supports development rather than production workloads; hosting the UI does not change those terms or shared API quotas. See [AMD setup](amd_setup.md) and [reliability boundaries](reliability-fixes.md).

## Local Windows / Python 3.12

```powershell
git clone https://github.com/minteeqahmed-png/Specguard-ai.git
cd Specguard-ai
git switch codex/specguard-mvp
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py --server.address=127.0.0.1
```

The explicit address keeps this local at http://localhost:8501. On Linux/macOS use `.venv/bin/python`. For an existing local `.env`, the configured mode is preserved; no secrets are needed for Demo Mode. Use port 8502 with `--server.port=8502` if 8501 is occupied. Stop the server with Ctrl+C.

The tested Windows environment is captured in `requirements-lock.txt`. It is a Windows snapshot, not a GPU inference environment. For Live Mode, follow [AMD setup](amd_setup.md), configure the private `.env` and restart Streamlit. Uploaded text is sent to the configured model endpoint when live extraction is requested.

## Optional Docker

Docker packaging has not passed a local build/runtime check. The default container runs Demo Mode. Bind it locally:

```bash
docker build -t specguard-ai .
docker run --rm -p 127.0.0.1:8501:8501 specguard-ai
```

A host SSH tunnel is not automatically reachable at localhost inside a container. The HTTPS Token Factory endpoint is independent of that optional tunnel setup. Do not bake credentials into an image.
