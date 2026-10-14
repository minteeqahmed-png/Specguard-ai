from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import streamlit as st

from specguard.ai_client import ExtractionError, ModelClient
from specguard.config import load_config
from specguard.parser import DocumentError, parse_document
from specguard.pipeline import analyze
from specguard.reconciliation import correction_checks, order_status, resolve_issue
from specguard.reporting import clarification_text, conflict_csv, full_report, json_report
from specguard.ui import render_header, render_sidebar

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="SpecGuard AI", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
render_header()
try:
    config = load_config()
except ValueError as exc:
    st.error(str(exc))
    st.stop()
client = ModelClient(config)
if config.mode == "demo":
    st.warning("DEMO MODE — AMD inference not active")
    st.caption("Deterministic extraction for labeled sample templates. This is not general AI document understanding.")
else:
    st.info("LIVE MODE — documents will be sent to your configured model endpoint when you extract facts.")
    st.caption("AMD execution requires separate hardware evidence; an API response alone cannot verify GPU identity.")
    if st.button("Check model connection"):
        try:
            st.session_state.connection = client.check_connection()
        except ExtractionError as exc:
            st.session_state.connection = str(exc)
    st.caption(st.session_state.get("connection", "Connection not checked in this session."))

st.header("1 · Document Upload")
source = st.radio("Document source", ["Synthetic sample", "Upload documents"], horizontal=True)
inputs = []
if source == "Synthetic sample":
    choices = ["Initial quantity and color conflict"] + [p.name for p in sorted((ROOT / "sample_data/cases").glob("*")) if p.is_dir()]
    sample = st.selectbox("Choose a synthetic order", choices)
    folder = ROOT / "sample_data/initial" if sample == choices[0] else ROOT / "sample_data/cases" / sample
    inputs = [(p.name, p.read_bytes()) for p in sorted(folder.iterdir()) if p.suffix in {".txt", ".csv", ".pdf"}]
    columns = st.columns(3)
    for index, (name, data) in enumerate(inputs):
        columns[index % 3].download_button(f"Download {name}", data, file_name=name, key=f"sample_{name}")
else:
    files = st.file_uploader("Add TXT, text-based PDF and CSV documents", type=["txt", "pdf", "csv"], accept_multiple_files=True)
    inputs = [(f.name, f.getvalue()) for f in files]
    st.caption("UTF-8 TXT/CSV · 10 MB per file · 50 PDF pages · 12 files and 30 MB total · OCR is not supported")
if len(inputs) > 12 or sum(len(data) for _, data in inputs) > 30 * 1024 * 1024:
    st.error("Limit this order to 12 documents and 30 MB total.")
    st.stop()
if len({name for name, _ in inputs}) != len(inputs):
    st.error("Rename duplicate filenames so every evidence reference is unambiguous.")
    st.stop()
fingerprint = hashlib.sha256(repr([(name, hashlib.sha256(data).hexdigest()) for name, data in inputs] + [(config.mode, config.base_url, config.model, config.timeout, hashlib.sha256(config.api_key.encode()).hexdigest())]).encode()).hexdigest()
if st.session_state.get("fingerprint") != fingerprint:
    for key in ("analysis", "resolutions", "review", "compared"):
        st.session_state.pop(key, None)
    st.session_state.fingerprint = fingerprint
    st.session_state.resolutions = []

for name, data in inputs:
    with st.expander(name):
        try:
            doc = parse_document(name, data)
            st.caption(f"{doc.kind.upper()} · {len(data):,} bytes · {len(doc.segments)} source segments")
            for warning in doc.warnings:
                st.warning(warning)
            if doc.rows:
                st.dataframe(doc.rows, width="stretch")
            else:
                st.text(doc.text[:12000])
                if len(doc.text) > 12000:
                    st.caption("Preview limited to 12,000 characters; parsing retains the complete accepted document.")
        except DocumentError as exc:
            st.error(str(exc))

st.header("2 · Extraction Preview")
if st.button("Extract facts", type="primary", disabled=not inputs):
    bar = st.progress(0, text="Parsing documents and extracting supported facts…")
    with st.spinner("Extracting facts…"):
        st.session_state.analysis = analyze(inputs, client, lambda fraction: bar.progress(fraction))
    st.session_state.resolutions = []
    st.session_state.pop("review", None)
    st.session_state.compared = False
result = st.session_state.get("analysis")
if result:
    for error in result["errors"]:
        st.error(f"{error['source']}: {error['message']}")
    for extraction in result["extractions"]:
        with st.expander(f"{extraction.source} · {len(extraction.facts)} extracted facts", expanded=True):
            st.caption("Source template verified" if extraction.verification == "template_verified" else "Source review required · completeness unverified")
            st.dataframe([{"Field": f.field, "Value": json.dumps(f.value) if isinstance(f.value, dict) else str(f.value), "Evidence": f.quote, "Location": f.location} for f in extraction.facts], width="stretch", hide_index=True)
    st.caption(f"Processed {len(result['extractions'])}/{len(inputs)} documents in {result['elapsed']:.2f} seconds. Timing includes local processing and any network requests.")
else:
    st.info("Add documents, then extract facts to see their values and source evidence.")

st.header("3 · Analyze Order")
if st.button("Compare requirements", disabled=result is None):
    st.session_state.compared = True
render_sidebar(config.mode)
if not result or not st.session_state.get("compared"):
    st.stop()
issues = result["issues"]
resolutions = st.session_state.resolutions
status = order_status(issues, resolutions, complete=result["complete"], extractions=result["extractions"])
resolved = {r.issue_id for r in resolutions}
st.header("4 · Conflict Summary")
columns = st.columns(4)
columns[0].metric("Order status", status)
columns[1].metric("Direct conflicts", sum(i.kind == "conflict" for i in issues))
columns[2].metric("Missing requirements", sum(i.kind == "missing" for i in issues))
columns[3].metric("Open issues", sum(i.id not in resolved for i in issues))
if status == "HOLD":
    st.error("HOLD · Resolve critical contradictions before proceeding.")
elif status == "REVIEW":
    st.warning("REVIEW · Required information, document processing or discrepancies need attention.")
else:
    st.success("READY · No unresolved blocking findings under the configured rules. Independent human production approval is required.")

st.header("5 · Evidence and Resolutions")
if resolutions:
    checks = correction_checks(result["extractions"], issues, resolutions)
    if checks:
        st.warning("The order still needs attention after applying the recorded corrections. Update the relevant resolutions or source documents.")
        for finding in checks:
            st.write(f"Correction check · {finding.title}: {finding.question}")
for issue in issues:
    done = issue.id in resolved
    with st.container(border=True):
        st.subheader(f"{issue.title} · {issue.severity}")
        st.caption("Resolved by reviewer" if done else "Awaiting review")
        for observation in issue.evidence:
            st.write(f"{observation.source} · {observation.fact.location}")
            st.code(str(observation.fact.value), language=None)
            st.text(observation.fact.quote)
        st.write(issue.question)
        if done:
            latest = next(r for r in reversed(resolutions) if r.issue_id == issue.id)
            st.write(f"Corrected value: {latest.corrected_value}")
            st.write(f"{latest.reviewer}: {latest.note}")
            st.caption(latest.created_at.isoformat())
        with st.expander("Update resolution" if done else "Record resolution"):
            suffix = fingerprint + issue.id
            with st.form("resolve_" + suffix):
                correction = st.text_input("Corrected value", key="value_" + suffix)
                note = st.text_area("Resolution note / confirmation reference", key="note_" + suffix)
                reviewer = st.text_input("Reviewer", key="reviewer_" + suffix)
                if st.form_submit_button("Save resolution"):
                    try:
                        record = resolve_issue(issue, correction, note, reviewer)
                        st.session_state.resolutions.append(record)
                        st.session_state.pop("review", None)
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
if not issues:
    st.write("No discrepancy found by the configured comparisons. Review the source documents before authorizing production.")
with st.form("human_review_" + fingerprint):
    reviewer_name = st.text_input("Final reviewer name")
    review_note = st.text_area("Review note")
    reviewed = st.checkbox("I have reviewed the source documents, extracted facts and resolutions.")
    if st.form_submit_button("Record human review"):
        if reviewed and reviewer_name.strip() and review_note.strip():
            st.session_state.review = {"reviewer": reviewer_name.strip(), "note": review_note.strip(), "at": datetime.now(timezone.utc).isoformat(), "status_at_review": status}
            st.success("Human review recorded. This does not override unresolved findings or authorize production.")
        else:
            st.error("Provide a reviewer name, note and review confirmation.")
if st.session_state.get("review"):
    st.caption(f"Human review recorded by {st.session_state.review['reviewer']}.")

st.header("6 · Export Results")
report = full_report(result["extractions"], issues, resolutions, result["errors"], result["complete"], result["elapsed"], st.session_state.get("review"))
export_issues = issues + (correction_checks(result["extractions"], issues, resolutions) if resolutions else [])
columns = st.columns(4)
columns[0].download_button("Extraction JSON", json_report({"mode": config.mode, "extractions": report["extractions"], "errors": result["errors"]}), "extraction.json", "application/json")
columns[1].download_button("Conflict CSV", conflict_csv(export_issues, resolutions), "conflicts.csv", "text/csv")
columns[2].download_button("Full analysis JSON", json_report(report), "analysis.json", "application/json")
columns[3].download_button("Clarification TXT", clarification_text(export_issues, resolutions, result["errors"]), "clarification.txt", "text/plain")
st.caption("Reports contain source evidence and review notes. Store them with the order record. Closing this session clears its in-memory state.")
