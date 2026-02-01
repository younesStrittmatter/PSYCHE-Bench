from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from claimspec.specs.base import Spec
from claimspec.values.base import Value, ValueComparison, ValueLike


@dataclass(frozen=True)
class ClaimSource:
    """
    Optional provenance for analytics / training.

    - source_type: where the claim comes from ("paper", "dataset", ...)
    - extractor_type: who/what extracted it ("human", "llm:gpt-5", "method:xyz", ...)
    - locator: where to find it (page/table/section/...)
    - quote: short excerpt (keep it short)
    - note: free-form hint
    - confidence: optional score (useful for LLM-extracted claims)
    """
    source_type: Optional[str] = None
    extractor_type: Optional[str] = None
    locator: Optional[str] = None
    quote: Optional[str] = None
    note: Optional[str] = None
    confidence: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "source_type": self.source_type,
            "extractor_type": self.extractor_type,
            "locator": self.locator,
            "quote": self.quote,
            "note": self.note,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, d: Optional[dict]) -> Optional["ClaimSource"]:
        if not d:
            return None
        return cls(
            source_type=d.get("source_type"),
            extractor_type=d.get("extractor_type"),
            locator=d.get("locator"),
            quote=d.get("quote"),
            note=d.get("note"),
            confidence=d.get("confidence"),
        )


@dataclass(frozen=True)
class Claim:
    """
    A claim is a (Spec, Value) pair:
      - Spec: the question/query
      - Value: the asserted answer

    Optionally includes claim_source for provenance (analytics / LLM training).
    """
    spec: Spec
    value: ValueLike  # Value or dict[str, Value] (grouped)
    claim_source: Optional[ClaimSource] = None

    def to_dict(self) -> dict:
        # Only reliably supports scalar Value for now.
        # Claims are primarily authored in Python; JSON is for debugging/optional persistence.
        if isinstance(self.value, dict):
            value_dict = {k: v.to_dict() for k, v in self.value.items()}
        else:
            value_dict = self.value.to_dict()

        out = {"spec": self.spec.to_dict(), "value": value_dict}
        if self.claim_source is not None:
            out["claim_source"] = self.claim_source.to_dict()
        return out

    @classmethod
    def from_dict(cls, d: dict) -> "Claim":
        # Only supports scalar Value from JSON right now
        return cls(
            spec=Spec.from_dict(d["spec"]),
            value=Value.from_dict(d["value"]),
            claim_source=ClaimSource.from_dict(d.get("claim_source")),
        )

    def compare(self, other: "Claim", *, rtol: float = 0.0, atol: float = 0.0) -> ValueComparison:
        if self.spec != other.spec:
            return ValueComparison(ok=False, passed=None, reason="spec_mismatch")
        return Value.compare(self.value, other.value, rtol=rtol, atol=atol)
