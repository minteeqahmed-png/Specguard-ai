from pathlib import Path

import pymupdf
import pytest

from specguard.parser import MAX_BYTES, DocumentError, parse_document


def pdf_bytes(text="Product: Football jersey"):
    with pymupdf.open() as pdf:
        page = pdf.new_page()
        if text:
            page.insert_text((72, 72), text)
        return pdf.tobytes()


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
