"""Construct synthetic fixtures and independent intent labels; no reconciliation imports."""
import json
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1] / "sample_data" / "cases"
PRODUCTS = ["Football jersey", "Basketball uniform", "Sports trousers", "Custom hoodie", "Embroidered shirt", "Team tracksuit"]
GROUPS = [("consistent", 6), ("quantity", 5), ("color", 4), ("material", 3), ("printing", 3), ("missing", 3), ("multi", 3)]
LABELS = {"product": "Product", "quantity": "Quantity", "unit": "Unit", "color": "Color", "material": "Material", "printing": "Printing", "deadline": "Deadline"}


def text_for(values):
    return "\n".join(f"{LABELS[field]}: {value}" for field, value in values.items())


def expected_facts(values, pdf=False):
    return [{"field": field, "value": value, "quote": f"{LABELS[field]}: {value}", "location": "page 1" if pdf else f"line {index}"} for index, (field, value) in enumerate(values.items(), 1)]


def generate():
    ROOT.mkdir(parents=True, exist_ok=True)
    cases = []
    number = 0
    for group, count in GROUPS:
        for index in range(count):
            number += 1
            case_id = f"{number:02d}_{group}"
            folder = ROOT / case_id
            folder.mkdir(exist_ok=True)
            base = {"product": PRODUCTS[(number - 1) % 6], "quantity": 500, "unit": "pieces", "color": "navy blue", "material": "polyester", "printing": "sublimation", "deadline": "2026-11-20"}
            buyer, tech = dict(base), dict(base)
            expected = []
            if group in {"quantity", "multi"}:
                tech["quantity"] = 450
                expected += ["conflict:quantity", "size_total:0"]
            if group in {"color", "multi"}:
                tech["color"] = "royal blue"
                expected += ["conflict:color"]
            if group in {"material", "multi"}:
                tech["material"] = "cotton"
                expected += ["conflict:material"]
            if group == "printing":
                tech["printing"] = "screen printing"
                expected += ["conflict:printing"]
            if group == "missing":
                field = ["material", "color", "printing"][index]
                buyer.pop(field)
                tech.pop(field)
                expected += [f"missing:{field}"]
            if group == "consistent" and index == 0:
                tech.update(unit="PCS", printing="DYE SUBLIMATION", color="NAVY   BLUE")
            (folder / "buyer_message.txt").write_text(text_for(buyer), encoding="utf-8")
            with pymupdf.open() as pdf:
                page = pdf.new_page()
                page.insert_text((72, 72), text_for(tech), fontsize=12)
                pdf.save(folder / "tech_pack.pdf")
            (folder / "quantities.csv").write_text("size,quantity\nS,100\nM,150\nL,150\nXL,100\n", encoding="utf-8")
            sizes = {"S": 100, "M": 150, "L": 150, "XL": 100}
            csv_quote = "\n".join(f"size: {size}; quantity: {count}" for size, count in sizes.items())
            labels = {"case_id": case_id, "group": group, "expected_issue_ids": expected, "expected_status": "HOLD" if group in {"quantity", "multi"} else "REVIEW" if expected else "READY", "documents": {"buyer_message.txt": expected_facts(buyer), "tech_pack.pdf": expected_facts(tech, pdf=True), "quantities.csv": [{"field": "size_quantities", "value": sizes, "quote": csv_quote, "location": "document"}]}}
            (folder / "ground_truth.json").write_text(json.dumps(labels, indent=2), encoding="utf-8")
            cases.append({"id": case_id, "group": group})
    (ROOT.parent / "manifest.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(f"Generated {len(cases)} cases with 81 synthetic documents.")


if __name__ == "__main__":
    generate()
