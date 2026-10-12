import json
from pathlib import Path

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
