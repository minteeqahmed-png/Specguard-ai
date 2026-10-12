import pytest
from pydantic import ValidationError

from specguard.schemas import ExtractionPayload, Fact


def test_valid_schema_and_optional_fields():
    result = ExtractionPayload.model_validate({"facts": [{"field": "quantity", "value": 500, "quote": "500", "location": "line 1"}]})
    assert len(result.facts) == 1
    assert ExtractionPayload(facts=[]).facts == []


@pytest.mark.parametrize("value", ["500", -1, 0, 1.5, True])
def test_invalid_quantity(value):
    with pytest.raises(ValidationError):
        Fact(field="quantity", value=value, quote="quantity", location="line 1")


@pytest.mark.parametrize("data", ['not json', '{"facts": "oops"}', '{"facts": [], "extra": true}'])
def test_invalid_payload(data):
    with pytest.raises(ValidationError):
        ExtractionPayload.model_validate_json(data)
