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
