"""Shared processing for Streamlit and evaluation; errors never become READY."""
from time import perf_counter

from specguard.ai_client import ExtractionError
from specguard.parser import DocumentError, parse_document
from specguard.reconciliation import reconcile


def analyze(inputs, client, progress=None):
    started = perf_counter()
    extractions, documents, errors = [], [], []
    if not inputs:
        errors.append({"source": "order", "message": "No documents supplied."})
    for index, (name, data) in enumerate(inputs):
        try:
            document = parse_document(name, data)
            documents.append(document)
            for warning in document.warnings:
                errors.append({"source": name, "message": warning})
            extraction = client.extract(document)
            extractions.append(extraction)
            if extraction.verification != "template_verified":
                errors.append({"source": name, "message": "Extracted facts require source review: values and completeness could not be independently verified. READY is blocked. Supply a supported labeled template or size,quantity CSV after checking the original document."})
        except (DocumentError, ExtractionError) as exc:
            errors.append({"source": name, "message": str(exc)})
        if progress:
            progress((index + 1) / len(inputs))
    return {"documents": documents, "extractions": extractions, "issues": reconcile(extractions), "errors": errors, "complete": bool(inputs) and len(extractions) == len(inputs) and not errors, "elapsed": perf_counter() - started}
