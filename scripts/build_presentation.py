"""Build the submission pitch PDF and vector cover from verified project facts."""
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "presentation"
OUT.mkdir(exist_ok=True)
W, H = 1600, 900
NAVY, PANEL, TEAL, WHITE, MUTED = "#102238", "#19364A", "#8EE0D3", "#F3F7FA", "#B5C8D4"
pdf = Canvas(str(OUT / "SpecGuard-AI-Pitch.pdf"), pagesize=(W, H), invariant=True)
pdf.setTitle("SpecGuard AI - Manufacturing Order Intelligence")
pdf.setAuthor("SpecGuard AI contributors")


def rect(x, y, w, h, color, radius=20):
    pdf.setFillColor(HexColor(color))
    pdf.roundRect(x, y, w, h, radius, stroke=0, fill=1)


def text(content, x, y, width=1300, size=27, color=WHITE, bold=False):
    style = ParagraphStyle("body", fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size,
                           leading=size * 1.35, textColor=HexColor(color))
    paragraph = Paragraph(content, style)
    _, height = paragraph.wrap(width, 700)
    paragraph.drawOn(pdf, x, y - height)
    return height


def slide(number, kicker, title, subtitle=""):
    pdf.setFillColor(HexColor(NAVY))
    pdf.rect(0, 0, W, H, stroke=0, fill=1)
    text("SPECGUARD AI / " + kicker.upper(), 80, 845, size=18, color=TEAL, bold=True)
    text(title, 80, 780, size=58, bold=True)
    if subtitle:
        text(subtitle, 80, 685, width=1420, size=25, color=MUTED)
    text("MANUFACTURING ORDER INTELLIGENCE", 80, 45, size=14, color=MUTED)
    pdf.setFillColor(HexColor(MUTED))
    pdf.setFont("Helvetica", 14)
    pdf.drawRightString(1520, 28, f"{number:02d} / 08")


def card(x, y, w, h, heading, body):
    rect(x + 7, y - 8, w, h, "#091827")
    rect(x, y, w, h, PANEL)
    text(heading, x + 28, y + h - 30, width=w - 56, size=29, color=TEAL, bold=True)
    text(body, x + 28, y + h - 92, width=w - 56, size=25)


slide(1, "AMD Developer Hackathon ACT III", "Clarity before production.",
      "SpecGuard AI compares manufacturing documents and connects each finding to its evidence.")
text("One order.<br/>Every detail.<br/>Human judgment.", 80, 565, width=800, size=64, bold=True)
for x, y, color in [(1130, 235, "#254B61"), (1095, 270, "#367A82"), (1060, 305, "#E8F3F5")]:
    rect(x + 8, y - 10, 310, 300, "#0A1B2B")
    rect(x, y, 310, 300, color)
text("SG", 1135, 535, width=180, size=75, color=NAVY, bold=True)
text("DOCUMENTS<br/>EVIDENCE<br/>REVIEW", 1100, 415, width=240, size=24, color=NAVY, bold=True)
text("Live inference via AMD Token Factory / MiMo-V2.6-Flash", 80, 125, size=23, color=TEAL)
pdf.showPage()

slide(2, "The problem", "One order. Three conflicting sources.",
      "An order coordinator needs to resolve differences before material is cut or printing begins.")
card(80, 280, 450, 330, "Buyer message", "Custom hoodie<br/><br/><b>300 pieces</b><br/>Color: <b>black</b>")
card(575, 280, 450, 330, "Technical PDF", "Custom hoodie<br/><br/><b>280 pieces</b><br/>Color: <b>charcoal</b>")
card(1070, 280, 450, 330, "Size spreadsheet", "S 75 / M 100<br/>L 75 / XL 50<br/><br/>Total: <b>300 pieces</b>")
text("Three deliberate findings: quantity, color and size total. Synthetic data only.", 80, 185, size=30, color=TEAL, bold=True)
pdf.showPage()

slide(3, "The product", "From documents to a reviewed decision.",
      "A working Streamlit interface for one product and one manufacturing order at a time.")
for x, heading, body in [(80, "01 / Upload", "TXT, text-based PDF<br/>and size CSV"),
                         (575, "02 / Inspect", "Extracted facts with<br/>quotes and locations"),
                         (1070, "03 / Compare", "Deterministic findings<br/>and clear questions")]:
    card(x, 360, 450, 240, heading, body)
card(80, 110, 700, 190, "04 / Review", "Record valid corrections and reviewer notes.<br/>Preserve original evidence.")
card(820, 110, 700, 190, "05 / Export", "Download JSON, CSV and clarification TXT.<br/>Keep the order's review record.")
pdf.showPage()

slide(4, "How AMD is used", "Live extraction. Independent checks.",
      "AMD Token Factory inference performs a meaningful part of the working document workflow.")
steps = [(80, 390, "Source parsing", "TXT / pypdf / CSV<br/>Retain line, page and record references"),
         (575, 390, "AMD Token Factory", "MiMo-V2.6-Flash<br/>Authenticated live model requests"),
         (1070, 390, "Validation", "Pydantic schema and evidence<br/>Template value / coverage checks"),
         (80, 100, "Reconciliation", "Compare quantities, sizes,<br/>colors and manufacturing details"),
         (575, 100, "Human decisions", "Immutable original facts<br/>Separate correction history"),
         (1070, 100, "Results", "HOLD / REVIEW / READY<br/>Evidence-linked reports")]
for x, y, heading, body in steps:
    card(x, y, 450, 240, heading, body)
pdf.showPage()

slide(5, "Boundaries", "Make uncertainty visible.",
      "The app supports review; independent human production approval remains required.")
card(80, 300, 450, 300, "HOLD", "Unresolved critical contradictions.<br/><br/>Example: 300 versus 280 pieces.")
card(575, 300, 450, 300, "REVIEW", "Missing data, failed processing or unverified extraction coverage.")
card(1070, 300, 450, 300, "READY", "No blocking findings under the configured rules after valid corrections.")
text("Free-form content cannot certify its own completeness. Unsupported layouts stay in REVIEW.<br/>No OCR, multi-item orders, login or persistent signed audit storage in this prototype.", 80, 220, width=1420, size=26, color=MUTED)
pdf.showPage()

slide(6, "Observed evidence", "Verified behavior, with a defined scope.",
      "The repository separates deterministic regression results from live model smoke tests.")
card(80, 350, 700, 250, "86 automated tests", "Parsing, schema and source checks, false-READY regressions, correction safety and Streamlit flows.")
card(820, 350, 700, 250, "27 synthetic orders", "81 documents / 399 expected field values.<br/>All expected statuses in deterministic Demo Mode.")
card(80, 70, 700, 230, "Hosted AMD smoke test", "3 live documents verified; expected HOLD conflicts.<br/>One observed order: 20.44 seconds end to end.")
card(820, 70, 700, 230, "Limits of this evidence", "Synthetic templates, not unseen-document accuracy.<br/>No customer savings or production SLA measured.")
pdf.showPage()

slide(7, "Business potential", "Help order coordinators catch conflicts earlier.",
      "Initial users: small and medium manufacturers receiving buyer messages, tech packs and size tables.")
card(80, 285, 700, 320, "Expected value", "Less repetitive comparison.<br/><br/>Clearer clarification questions.<br/><br/>Traceable reviewer decisions.")
card(820, 285, 700, 320, "Pilot measurement", "Compare review time and missed conflicts against manual work on independently labeled orders.")
text("A future per-order fee or subscription is a hypothesis. Pricing, savings and customer demand remain unvalidated.", 80, 200, width=1420, size=28, color=MUTED)
pdf.showPage()

slide(8, "Try the working app", "Upload the examples. Inspect the evidence.",
      "Suggested event track: Reinvent Commerce. Manufacturing quality also relates to Intelligent Industry.")
card(80, 325, 1440, 270, "Hosted application", "<b>https://specguard-ai-dev.streamlit.app/</b><br/><br/>Choose Upload documents. Add buyer_order.txt, tech_pack.pdf and size_quantities.csv.<br/>Extract and compare: expect HOLD with three deliberate conflicts.")
card(80, 80, 1440, 190, "Code, examples and validation", "https://github.com/minteeqahmed-png/Specguard-ai<br/>MIT project code / examples folder / reproducible local Demo Mode")
pdf.linkURL("https://specguard-ai-dev.streamlit.app/", (80, 325, 1520, 595))
pdf.linkURL("https://github.com/minteeqahmed-png/Specguard-ai", (80, 80, 1520, 270))
pdf.showPage()
pdf.save()

cover = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-label="SpecGuard AI: evidence before production">
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#102238"/><stop offset="1" stop-color="#1D4658"/></linearGradient><filter id="shadow"><feDropShadow dx="10" dy="18" stdDeviation="14" flood-opacity=".3"/></filter></defs>
<rect width="1600" height="900" fill="url(#bg)"/><circle cx="1300" cy="450" r="280" fill="none" stroke="#477786" opacity=".3"/><circle cx="1300" cy="450" r="350" fill="none" stroke="#477786" opacity=".2"/>
<g font-family="Arial,Helvetica,sans-serif"><text x="90" y="120" fill="#8EE0D3" font-size="23" letter-spacing="5">MANUFACTURING ORDER INTELLIGENCE</text>
<text x="85" y="300" fill="#F3F7FA" font-size="108" font-weight="700">SpecGuard AI</text>
<text x="90" y="445" fill="#F3F7FA" font-size="72" font-weight="700">Evidence before</text><text x="90" y="535" fill="#8EE0D3" font-size="72" font-weight="700">production.</text>
<text x="90" y="635" fill="#C1D5DF" font-size="30">Documents to source facts to human review.</text>
<text x="90" y="805" fill="#8EE0D3" font-size="24">LIVE INFERENCE VIA AMD TOKEN FACTORY</text>
<g transform="translate(1090 220) rotate(8 180 220)" filter="url(#shadow)"><rect x="60" y="60" width="320" height="410" rx="30" fill="#254B61"/><rect x="30" y="30" width="320" height="410" rx="30" fill="#367A82"/><rect width="320" height="410" rx="30" fill="#E8F3F5"/><rect x="84" y="82" width="150" height="150" rx="30" fill="#146B74"/><text x="160" y="180" text-anchor="middle" fill="#F3F7FA" font-size="70" font-weight="700">SG</text><rect x="50" y="285" width="220" height="12" rx="6" fill="#A1C7CE"/><rect x="50" y="320" width="170" height="12" rx="6" fill="#A1C7CE"/></g>
</g></svg>'''
(OUT / "cover.svg").write_text(cover, encoding="utf-8")
print("Generated 8-slide pitch PDF and vector cover.")
