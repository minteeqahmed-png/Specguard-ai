"""Evaluate actual pipeline outputs against synthetic intent labels."""
import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from specguard.ai_client import ModelClient
from specguard.config import Config, load_config
from specguard.pipeline import analyze
from specguard.reconciliation import normalize, order_status


def evaluate(mode="demo"):
    config = Config() if mode == "demo" else load_config()
    if config.mode != mode:
        raise ValueError("For live evaluation, set SPECGUARD_MODE=live and configure the endpoint.")
    client = ModelClient(config)
    tp = fp = fn = field_correct = field_total = processed = status_correct = 0
    rows, inference = [], []
    started = perf_counter()
    for truth_path in sorted((ROOT / "sample_data/cases").glob("*/ground_truth.json")):
        truth = json.loads(truth_path.read_text(encoding="utf-8"))
        inputs = [(name, (truth_path.parent / name).read_bytes()) for name in truth["documents"]]
        result = analyze(inputs, client)
        actual = {i.id for i in result["issues"]}
        expected = set(truth["expected_issue_ids"])
        actual_conflicts = {i.id for i in result["issues"] if i.kind == "conflict"}
        expected_conflicts = {i for i in expected if not i.startswith("missing:")}
        tp += len(actual_conflicts & expected_conflicts)
        fp += len(actual_conflicts - expected_conflicts)
        fn += len(expected_conflicts - actual_conflicts)
        processed += len(result["extractions"])
        by_source = {e.source: e for e in result["extractions"]}
        for name, facts in truth["documents"].items():
            predicted = list(by_source[name].facts) if name in by_source else []
            # Exact normalized field/value matching; false extra fields increase denominator.
            for fact in facts:
                field_total += 1
                match = next((p for p in predicted if p.field == fact["field"] and normalize(p.field, p.value) == normalize(fact["field"], fact["value"])), None)
                if match is not None:
                    field_correct += 1
                    predicted.remove(match)
            field_total += len(predicted)
        inference += [e.inference_seconds for e in result["extractions"] if e.inference_seconds is not None]
        status = order_status(result["issues"], [], complete=result["complete"])
        status_correct += status == truth["expected_status"]
        rows.append({"case": truth["case_id"], "expected": sorted(expected), "actual": sorted(actual), "status": status, "errors": result["errors"], "processing_seconds": result["elapsed"]})
    if not rows:
        raise ValueError("Dataset missing. Run scripts/generate_dataset.py first.")
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "mode": mode, "python": platform.python_version(), "platform": platform.system(), "scope": "Synthetic template extraction and deterministic rule evaluation; not real-world accuracy or AMD performance." if mode == "demo" else "Synthetic live endpoint evaluation; AMD hardware must be independently evidenced.", "case_count": len(rows), "true_positive_count": tp, "false_positive_count": fp, "false_negative_count": fn, "conflict_precision": precision, "conflict_recall": recall, "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0, "field_extraction_accuracy": field_correct / field_total if field_total else 0, "field_correct": field_correct, "field_total": field_total, "successfully_processed_documents": processed, "expected_documents": len(rows) * 3, "status_correct": status_correct, "processing_seconds": perf_counter() - started, "inference_request_seconds": inference if mode == "live" else None, "amd_hardware_verified": False, "cases": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    parser.add_argument("--output", type=Path, default=ROOT / "results/local_evaluation.json")
    args = parser.parse_args()
    report = evaluate(args.mode)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))
    print(f"Saved results to {args.output}")
