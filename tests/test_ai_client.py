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
