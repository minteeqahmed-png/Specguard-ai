"""Static presentation helpers. Uploaded content never enters these HTML templates."""
from pathlib import Path

import streamlit as st


def render_header():
    css = (Path(__file__).with_name("assets") / "theme.css").read_text(encoding="utf-8")
    st.html(f"<style>{css}</style>")
    st.html('''
    <section class="sg-hero" aria-label="SpecGuard AI introduction">
      <div class="sg-hero-copy">
        <div class="sg-eyebrow"><span></span> MANUFACTURING ORDER INTELLIGENCE</div>
        <h1>Clarity before<br><span>production.</span></h1>
        <p>SpecGuard AI connects every requirement to its evidence,<br class="sg-wide-break"> so your next decision is a confident one.</p>
        <div class="sg-hero-footer">DOCUMENTS <b>→</b> EVIDENCE <b>→</b> HUMAN REVIEW</div>
      </div>
      <div class="sg-art" aria-hidden="true">
        <div class="sg-orbit"></div>
        <div class="sg-sheet sg-sheet-back"></div>
        <div class="sg-sheet sg-sheet-middle"></div>
        <div class="sg-sheet sg-sheet-front">
          <div class="sg-sheet-top"><span></span><i></i><i></i></div>
          <div class="sg-shield">S<span>G</span></div>
          <div class="sg-paper-line"></div><div class="sg-paper-line short"></div>
        </div>
        <div class="sg-ground"></div>
      </div>
    </section>
    ''')


def render_sidebar(mode):
    mode_label = "DEMO WORKSPACE" if mode == "demo" else "LIVE WORKSPACE"
    with st.sidebar:
        st.html('''
        <div class="sg-brand"><div class="sg-brand-mark">S<span>G</span></div>
          <div><strong>SpecGuard<span>AI</span></strong><small>ORDER INTELLIGENCE</small></div>
        </div>
        <div class="sg-sidebar-intro"><h2>Your order.<br>Every detail.</h2><p>A clear path from documents<br>to a reviewed decision.</p></div>
        <div class="sg-nav-label">ORDER WORKSPACE</div>
        <nav class="sg-nav" aria-label="Order workflow">
          <a href="#1-document-upload" target="_self"><span>01</span><div>Documents<small>Add your order files</small></div><b>↗</b></a>
          <a href="#2-extraction-preview" target="_self"><span>02</span><div>Extraction<small>Inspect the source facts</small></div><b>↗</b></a>
          <a href="#3-analyze-order" target="_self"><span>03</span><div>Analysis<small>Compare requirements</small></div><b>↗</b></a>
        </nav>
        ''')
        # These sections exist only after the user compares the current order.
        if st.session_state.get("compared") and st.session_state.get("analysis"):
            st.html('''<nav class="sg-nav sg-nav-continuation" aria-label="Order results">
              <a href="#5-evidence-and-resolutions" target="_self"><span>04</span><div>Review<small>Resolve with evidence</small></div><b>↗</b></a>
              <a href="#6-export-results" target="_self"><span>05</span><div>Export<small>Keep your audit trail</small></div><b>↗</b></a>
            </nav>''')
        st.download_button(
            "Download example documents",
            (Path(__file__).resolve().parents[1] / "examples" / "SpecGuard-Example-Documents.zip").read_bytes(),
            file_name="SpecGuard-Example-Documents.zip",
            mime="application/zip",
            help="Three synthetic TXT, PDF and CSV files with upload instructions and expected findings.",
            key="example_documents",
            width="stretch",
        )
        st.caption("TXT + PDF + CSV · synthetic order with deliberate conflicts")
        st.html(f'''<div class="sg-mode"><span></span>{mode_label}</div>
        <div class="sg-review-note"><div class="sg-note-symbol">◎</div><strong>Human judgment comes first.</strong><p>One order. One product. Review the evidence before authorizing production.</p></div>
        <div class="sg-sidebar-foot">Your files stay in this session.<br>Export your reports before leaving.</div>''')
