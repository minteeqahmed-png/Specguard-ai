import json
from pathlib import Path

import httpx
import pytest

from specguard.ai_client import ModelClient
from specguard.config import Config
from scripts.evaluate import evaluate
from specguard.parser import parse_document


def test_dataset_and_expected_evidence():
    paths = list(Path("sample_data/cases").glob("*/ground_truth.json"))
    assert len(paths) == 27
    for path in paths:
        truth = json.loads(path.read_text())
        for name, facts in truth["documents"].items():
            document = parse_document(name, (path.parent / name).read_bytes())
            for fact in facts:
                assert " ".join(fact["quote"].split()) in " ".join(document.text.split())


def test_evaluation_matches_synthetic_labels():
    report = evaluate()
    assert report["case_count"] == 27
    assert report["successfully_processed_documents"] == 81
    assert report["false_positive_count"] == report["false_negative_count"] == 0
    assert report["status_correct"] == 27


@pytest.mark.parametrize("status", [401, 403, 429])
def test_live_evaluation_stops_on_provider_failure(monkeypatch, status):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(status)
    config = Config(mode="live", api_key="test-key")
    monkeypatch.setattr("scripts.evaluate.load_config", lambda: config)
    monkeypatch.setattr("scripts.evaluate.ModelClient", lambda config: ModelClient(config, httpx.MockTransport(handler)))
    report = evaluate("live")
    assert len(calls) == 1
    assert report["case_count"] == 1 and report["dataset_case_count"] == 27
    assert len(report["not_run_cases"]) == 26
    assert report["stopped_http_status"] == status
    assert report["successfully_processed_documents"] == 0 and report["expected_documents"] == 81
    assert report["cases"][0]["status"] == "REVIEW"
    assert sum("Not processed" in error["message"] for error in report["cases"][0]["errors"]) == 2
