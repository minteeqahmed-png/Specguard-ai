from pathlib import Path

import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas
import pytest

from specguard.parser import MAX_BYTES, DocumentError, parse_document


def pdf_bytes(text="Product: Football jersey"):
    stream = io.BytesIO()
    pdf = Canvas(stream)
    if text:
        pdf.drawString(72, 750, text)
    pdf.showPage()
    pdf.save()
    return stream.getvalue()


def test_encrypted_pdf_is_rejected():
    writer = PdfWriter()
    writer.append(PdfReader(io.BytesIO(pdf_bytes())))
    writer.encrypt("secret")
    stream = io.BytesIO()
    writer.write(stream)
    with pytest.raises(DocumentError, match="Password-protected"):
        parse_document("locked.pdf", stream.getvalue())


def test_pdf_page_limit():
    writer = PdfWriter()
    for _ in range(51):
        writer.add_blank_page(width=100, height=100)
    stream = io.BytesIO()
    writer.write(stream)
    with pytest.raises(DocumentError, match="50-page"):
        parse_document("long.pdf", stream.getvalue())


def test_txt():
    doc = parse_document("buyer.TXT", b"\xef\xbb\xbfQuantity: 500\nColor: navy blue")
    assert doc.segments[1].location == "line 2"
    assert "500" in doc.text


def test_pdf():
    doc = parse_document("tech.pdf", pdf_bytes())
    assert doc.segments[0].location == "page 1"
    assert "Football jersey" in doc.text


def test_csv_missing_values():
    doc = parse_document("sizes.csv", b"size,quantity\nS,100\nM,\n")
    assert doc.rows[1]["quantity"] == ""
    assert doc.warnings


@pytest.mark.parametrize("name,data", [
    ("empty.txt", b""), ("space.txt", b"   "), ("broken.pdf", b"not a pdf"),
    ("scan.pdf", pdf_bytes("")), ("bad.txt", b"\xff\xfe"),
    ("bad.csv", b"size,quantity\nS,1,2"), ("headers.csv", b"size,Size\nS,M"),
    ("empty.csv", b"size,quantity\n"), ("image.png", b"png"),
    ("large.txt", b"x" * (MAX_BYTES + 1)), ("utf16.txt", b"a\x00b\x00"),
], ids=["empty", "whitespace", "corrupt-pdf", "scanned-pdf", "encoding", "columns", "duplicate-headers", "header-only", "unsupported", "oversized", "utf16"])
def test_invalid_documents(name, data):
    with pytest.raises(DocumentError):
        parse_document(name, data)


def test_samples_parse():
    for path in Path("sample_data/initial").glob("*"):
        assert parse_document(path.name, path.read_bytes()).text


def test_csv_expansion_cannot_bypass_character_limit():
    data = (("x" * 1000) + "\n" + "v\n" * 101).encode()
    with pytest.raises(DocumentError, match="100,000-character"):
        parse_document("expanded.csv", data)


def test_csv_character_limit_includes_record_separators(monkeypatch):
    monkeypatch.setattr("specguard.parser.MAX_CHARS", 11)
    assert len(parse_document("small.csv", b"xx\nv\nv\n").text) == 11
    monkeypatch.setattr("specguard.parser.MAX_CHARS", 10)
    with pytest.raises(DocumentError, match="character limit"):
        parse_document("small.csv", b"xx\nv\nv\n")
