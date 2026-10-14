"""Validated facts and immutable evidence, separate from human resolutions."""
from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

FieldName = Literal["product", "category", "quantity", "unit", "size_quantities", "color", "secondary_colors", "material", "printing", "embroidery", "deadline", "instructions"]


class Fact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    field: FieldName
    value: str | StrictInt | dict[str, StrictInt]
    quote: str = Field(min_length=1, max_length=12000)
    location: str = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def valid_value(self):
        if self.field == "quantity":
            if type(self.value) is not int or not 0 < self.value <= 100_000_000:
                raise ValueError("Quantity must be a positive integer, not a string or decimal.")
        elif self.field == "size_quantities":
            if not isinstance(self.value, dict) or not self.value:
                raise ValueError("Size quantities must be a nonempty mapping.")
            keys = [key.strip().casefold() for key in self.value]
            if any(not key for key in keys) or len(set(keys)) != len(keys):
                raise ValueError("Size labels must be nonempty and unique.")
            if any(type(v) is not int or v < 0 or v > 100_000_000 for v in self.value.values()):
                raise ValueError("Size counts must be nonnegative integers.")
        elif not isinstance(self.value, str) or not self.value.strip() or self.value.strip().casefold() in {"unknown", "n/a", "null", "unspecified"}:
            raise ValueError("Unknown fields must be omitted; text values must be nonempty.")
        if self.field == "deadline":
            date.fromisoformat(self.value)
        if not self.quote.strip() or not self.location.strip():
            raise ValueError("Evidence quote and location cannot be blank.")
        return self


class ExtractionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    facts: list[Fact] = Field(max_length=100)


class Extraction(BaseModel):
    model_config = ConfigDict(frozen=True)
    source: str
    sha256: str
    mode: Literal["demo", "live"]
    facts: tuple[Fact, ...]
    inference_seconds: float | None = None
    model: str | None = None
    verification: Literal["template_verified", "review_required"] = "review_required"


class Observation(BaseModel):
    source: str
    sha256: str
    fact: Fact


class Issue(BaseModel):
    id: str
    field: str
    severity: Literal["CRITICAL", "MAJOR", "MINOR"]
    kind: Literal["conflict", "missing"]
    title: str
    evidence: list[Observation] = Field(default_factory=list)
    question: str


class Resolution(BaseModel):
    model_config = ConfigDict(frozen=True)
    issue_id: str
    corrected_value: str = Field(min_length=1)
    note: str = Field(min_length=1)
    reviewer: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def not_blank(self):
        if not all(x.strip() for x in (self.corrected_value, self.note, self.reviewer)):
            raise ValueError("Corrected value, explanation and reviewer are required.")
        return self
