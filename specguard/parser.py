"""Bounded local parsing; never writes uploaded documents to disk."""
import csv
import hashlib
import io
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader

MAX_BYTES = 10 * 1024 * 1024
MAX_CHARS = 100_000
MAX_PAGES = 50


class DocumentError(ValueError):
    """A document cannot be safely or meaningfully parsed."""


@dataclass(frozen=True)
class Segment:
    location: str
    text: str


@dataclass
class Document:
    name: str
    kind: str
    sha256: str
    segments: list[Segment]
    rows: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(segment.text for segment in self.segments)


def parse_document(name: str, data: bytes) -> Document:
    kind = Path(name).suffix.lower().lstrip(".")
    if kind not in {"txt", "csv", "pdf"}:
        raise DocumentError("Unsupported format. Upload TXT, CSV, or a text-based PDF.")
    if len(data) > MAX_BYTES:
        raise DocumentError("File exceeds the 10 MB limit.")
    if not data:
        raise DocumentError("Document is empty.")
    doc = Document(name, kind, hashlib.sha256(data).hexdigest(), [])
    if kind == "pdf":
        try:
            with io.BytesIO(data) as stream:
                pdf = PdfReader(stream, strict=True)
                if pdf.is_encrypted:
                    raise DocumentError("Password-protected PDFs are not supported.")
                if len(pdf.pages) > MAX_PAGES:
                    raise DocumentError("PDF exceeds the 50-page limit.")
                for index, page in enumerate(pdf.pages):
                    text = (page.extract_text() or "").strip()
                    doc.segments.append(Segment(f"page {index + 1}", text))
                    if not text:
                        doc.warnings.append(f"Page {index + 1} has no extractable text; scanned content requires OCR, which is not supported.")
                    if sum(len(s.text) for s in doc.segments) > MAX_CHARS:
                        raise DocumentError("Extracted content exceeds the 100,000-character limit.")
        except DocumentError:
            raise
        except Exception as exc:
            raise DocumentError("PDF is corrupt or unreadable. Export a new text-based PDF.") from exc
    else:
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DocumentError("Invalid encoding. Save the document as UTF-8 and upload again.") from exc
        if "\x00" in text:
            raise DocumentError("Binary or UTF-16 content detected. Save as UTF-8.")
        if len(text) > MAX_CHARS:
            raise DocumentError("Content exceeds the 100,000-character limit.")
        if kind == "txt":
            doc.segments = [Segment(f"line {i}", line) for i, line in enumerate(text.splitlines(), 1) if line.strip()]
        else:
            try:
                table = list(csv.reader(io.StringIO(text, newline=""), strict=True))
            except csv.Error as exc:
                raise DocumentError("Malformed CSV. Use a comma-separated table with a header row.") from exc
            if not table or not table[0]:
                raise DocumentError("CSV is empty.")
            headers = [h.strip() for h in table[0]]
            if any(not h for h in headers) or len(set(h.casefold() for h in headers)) != len(headers):
                raise DocumentError("CSV headers must be nonempty and unique.")
            for row_index, row in enumerate(table[1:], 2):
                if not row or not any(v.strip() for v in row):
                    continue
                if len(row) != len(headers):
                    raise DocumentError(f"CSV record {row_index} has a different column count than its header.")
                values = [v.strip() for v in row]
                doc.rows.append(dict(zip(headers, values)))
                doc.segments.append(Segment(f"record {row_index}", "; ".join(f"{h}: {v}" for h, v in zip(headers, values))))
                if any(not v for v in values):
                    doc.warnings.append(f"CSV record {row_index} contains missing values.")
    if not doc.text.strip():
        raise DocumentError("No readable content. Scanned PDFs need OCR; CSV files need data rows.")
    return doc
