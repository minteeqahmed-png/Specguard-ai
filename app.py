from pathlib import Path

import streamlit as st

from specguard.parser import DocumentError, parse_document

st.set_page_config(page_title="SpecGuard AI", page_icon="🛡️", layout="wide")
st.title("SpecGuard AI")
st.caption("Manufacturing Order Intelligence")
st.warning("DEMO MODE — AMD inference not active")
st.header("1 · Document Upload")
files = st.file_uploader("Upload documents for one order", type=["txt", "pdf", "csv"], accept_multiple_files=True)
samples = st.checkbox("Use synthetic sample order", value=not bool(files))
inputs = [(f.name, f.getvalue()) for f in files]
if samples:
    inputs += [(p.name, p.read_bytes()) for p in sorted(Path("sample_data/initial").glob("*"))]
st.header("2 · Document Preview")
for name, data in inputs:
    try:
        document = parse_document(name, data)
        with st.expander(f"{name} · {document.kind.upper()} · parsed", expanded=True):
            for warning in document.warnings:
                st.warning(warning)
            if document.rows:
                st.dataframe(document.rows, use_container_width=True)
            else:
                st.text(document.text)
    except DocumentError as exc:
        st.error(f"{name}: {exc}")
st.info("Phase 1 parses documents locally. Structured extraction and order verification are the next stage. Human review is required before production.")
