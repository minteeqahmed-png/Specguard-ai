import json

import httpx
import pytest

from specguard.ai_client import ExtractionError, ModelClient
from specguard.config import Config
from specguard.parser import parse_document
from specguard.pipeline import analyze
from specguard.reconciliation import order_status

DOC = parse_document("buyer.txt", b"Quantity: 500")
PAYLOAD = {"facts": [{"field": "quantity", "value": 500, "quote": "Quantity: 500", "location": "line 1"}]}


def client(handler):
    return ModelClient(Config(mode="live", api_key="test-key"), httpx.MockTransport(handler))


def response(content=PAYLOAD, finish="stop"):
    return httpx.Response(200, json={"choices": [{"finish_reason": finish, "message": {"content": json.dumps(content)}}]})


def test_success():
    def handler(request):
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.url.path == "/v1/chat/completions"
        assert json.loads(request.content)["response_format"] == {"type": "json_object"}
        return response()
    result = client(handler).extract(DOC)
    assert result.facts[0].value == 500
    assert result.mode == "live" and result.inference_seconds >= 0


@pytest.mark.parametrize("error", [httpx.ReadTimeout("timeout"), httpx.ConnectError("unavailable")])
def test_network_errors(error):
    def handler(request):
        raise error
    with pytest.raises(ExtractionError):
        client(handler).extract(DOC)


@pytest.mark.parametrize("result", [httpx.Response(503), httpx.Response(200, text="broken"), httpx.Response(200, json={}), response({"facts": "wrong"}), response(finish="length"), response({"facts": [{"field": "quantity", "value": 500, "quote": "invented", "location": "line 1"}]})], ids=["unavailable", "invalid-json", "structure", "schema", "truncated", "false-evidence"])
def test_bad_responses(result):
    with pytest.raises(ExtractionError):
        client(lambda r: result).extract(DOC)


def test_health():
    assert "reachable" in client(lambda r: httpx.Response(200, json={"data": [{"id": "Qwen/Qwen2.5-7B-Instruct"}]})).check_connection()


def test_failed_document_blocks_pipeline():
    result = analyze([("buyer.txt", b"Quantity: 500"), ("broken.pdf", b"bad")], ModelClient(Config()))
    assert result["errors"] and not result["complete"]
    assert order_status(result["issues"], [], complete=result["complete"]) == "REVIEW"


@pytest.mark.parametrize("kwargs", [{"mode": "typo"}, {"timeout": float("nan")}, {"timeout": 0}, {"base_url": "http://remote.test/v1"}, {"mode": "live"}])
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        Config(**kwargs)


@pytest.mark.parametrize("data", [None, [], {"choices": [None]}, {"choices": "wrong"}])
def test_unexpected_response_shapes(data):
    with pytest.raises(ExtractionError):
        client(lambda r: httpx.Response(200, json=data)).extract(DOC)


def test_demo_rejects_unrecognized_prose():
    with pytest.raises(ExtractionError):
        ModelClient(Config()).extract(parse_document("buyer.txt", b"Quantity: 500\nActually make only 300."))


@pytest.mark.parametrize("invalid", [
    response({"facts": []}),
    response({"facts": [{"field": "quantity", "value": "500", "quote": "Quantity: 500", "location": "line 1"}]}),
    httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": "{invalid JSON"}}]}),
    response({"facts": [{"field": "quantity", "value": 500, "quote": "invented", "location": "line 1"}]}),
])
def test_invalid_extraction_is_retried_and_fully_validated(invalid):
    requests = []
    def handler(request):
        requests.append(json.loads(request.content))
        return invalid if len(requests) == 1 else response()
    result = client(handler).extract(DOC)
    assert len(requests) == 2
    assert result.facts[0].value == 500
    assert result.facts[0].quote == "Quantity: 500"
    assert requests[0]["messages"][1] == requests[1]["messages"][1]
    assert "previous extraction failed validation" in requests[1]["messages"][0]["content"]


def test_repeated_schema_failure_is_bounded_and_blocks_approval():
    requests = []
    def handler(request):
        requests.append(json.loads(request.content))
        return response({"facts": [{"field": "quantity", "value": "private-invalid-value", "quote": "Quantity: 500", "location": "line 1"}]})
    result = analyze([("buyer.txt", b"Quantity: 500")], client(handler))
    assert len(requests) == 2
    assert not result["complete"] and not result["extractions"]
    assert order_status(result["issues"], [], complete=result["complete"]) == "REVIEW"
    assert "after 2 attempts" in result["errors"][0]["message"]
    assert "private-invalid-value" not in result["errors"][0]["message"]
    assert "private-invalid-value" not in json.dumps(requests[1])


def test_retry_cannot_bypass_evidence_validation():
    calls = []
    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            return response({"facts": "invalid"})
        return response({"facts": [{"field": "quantity", "value": 500, "quote": "invented", "location": "line 1"}]})
    with pytest.raises(ExtractionError, match="after 2 attempts"):
        client(handler).extract(DOC)
    assert len(calls) == 2


@pytest.mark.parametrize("failed_response", [httpx.Response(401), httpx.Response(429), response(finish="length")])
def test_non_validation_failures_do_not_trigger_extraction_retry(failed_response):
    calls = []
    def handler(request):
        calls.append(request)
        return failed_response
    with pytest.raises(ExtractionError):
        client(handler).extract(DOC)
    assert len(calls) == 1


def test_csv_has_one_citable_complete_table():
    document = parse_document("sizes.csv", b"size,quantity\nS,100\nM,150\n")
    def handler(request):
        segments = json.loads(json.loads(request.content)["messages"][1]["content"])
        assert segments == [{"location": "document", "text": document.text}]
        return response({"facts": [{"field": "size_quantities", "value": {"S": 100, "M": 150}, "quote": document.text, "location": "document"}]})
    result = client(handler).extract(document)
    assert len(result.facts) == 1
    assert result.facts[0].value == {"S": 100, "M": 150}


def test_empty_facts_cannot_count_as_a_successfully_processed_document():
    result = analyze([("buyer.txt", b"Quantity: 500")], client(lambda request: response({"facts": []})))
    assert not result["complete"] and not result["extractions"]
    assert "No supported facts" in result["errors"][0]["message"]
    assert order_status(result["issues"], [], complete=result["complete"]) == "REVIEW"


BASE_ORDER = "Product: Football jersey\nQuantity: 500\nUnit: pieces\nColor: navy blue\nMaterial: polyester\nPrinting: sublimation"


@pytest.mark.parametrize("fault", ["wrong_value", "omitted_quantity"])
def test_conflicting_source_cannot_become_ready_with_valid_but_incorrect_model_facts(fault):
    from specguard.ai_client import demo_extract
    def handler(request):
        segments = json.loads(json.loads(request.content)["messages"][1]["content"])
        text = "\n".join(s["text"] for s in segments)
        facts = [f.model_dump() for f in demo_extract(parse_document("source.txt", text.encode())).facts]
        if "Quantity: 450" in text:
            if fault == "wrong_value":
                next(f for f in facts if f["field"] == "quantity")["value"] = 500
            else:
                facts = [f for f in facts if f["field"] != "quantity"]
        return response({"facts": facts})
    result = analyze([("buyer.txt", BASE_ORDER.encode()), ("tech.txt", BASE_ORDER.replace("500", "450").encode())], client(handler))
    assert not result["complete"]
    assert order_status(result["issues"], [], complete=result["complete"], extractions=result["extractions"]) != "READY"
    assert any(e["source"] == "tech.txt" for e in result["errors"])


def test_freeform_omission_remains_reviewable_but_cannot_be_ready():
    from specguard.ai_client import demo_extract
    facts = [f.model_dump() for f in demo_extract(parse_document("buyer.txt", BASE_ORDER.encode())).facts]
    result = analyze([("buyer.txt", (BASE_ORDER + "\nActually make only 450 instead.").encode())], client(lambda r: response({"facts": facts})))
    assert result["extractions"]  # Preserve model output for inspection, without claiming completeness.
    assert not result["complete"]
    assert order_status(result["issues"], [], complete=result["complete"]) == "REVIEW"


@pytest.mark.parametrize("value", [{"S": 101, "M": 149}, {"S": 100}])
def test_size_table_changed_or_omitted_rows_are_rejected(value):
    document = parse_document("sizes.csv", b"size,quantity\nS,100\nM,150\n")
    with pytest.raises(ExtractionError):
        client(lambda r: response({"facts": [{"field": "size_quantities", "value": value, "quote": document.text, "location": "document"}]})).extract(document)


def test_same_document_contradiction_cannot_be_omitted():
    with pytest.raises(ExtractionError):
        client(lambda r: response()).extract(parse_document("buyer.txt", b"Quantity: 500\nQuantity: 450"))


def test_source_validation_retry_can_recover_without_replacing_model_facts():
    calls = []
    def handler(request):
        calls.append(request)
        return response({"facts": [{"field": "quantity", "value": 450, "quote": "Quantity: 500", "location": "line 1"}]}) if len(calls) == 1 else response()
    extraction = client(handler).extract(DOC)
    assert len(calls) == 2 and extraction.mode == "live"
    assert extraction.verification == "template_verified"
    assert extraction.facts[0].value == 500


def test_unverified_live_extraction_blocks_status_and_export_even_if_complete_claimed():
    from specguard.schemas import Extraction
    from specguard.reporting import full_report
    from specguard.ai_client import demo_extract
    facts = demo_extract(parse_document("buyer.txt", BASE_ORDER.encode())).facts
    unverified = Extraction(source="buyer.txt", sha256="test", mode="live", facts=facts)
    assert order_status([], [], complete=True, extractions=[unverified]) == "REVIEW"
    report = full_report([unverified], [], [], [], True, 0, {"reviewer": "Test reviewer"})
    assert report["status"] == "REVIEW"
    assert report["extractions"][0]["verification"] == "review_required"


def test_blank_labeled_value_cannot_be_silently_ignored():
    with pytest.raises(ExtractionError):
        ModelClient(Config()).extract(parse_document("buyer.txt", (BASE_ORDER + "\nDeadline:").encode()))
