from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Type

from claimspec.claims.claim import Claim
from claimspec.specs.base import Spec
from claimspec.values.base import Value
from claimspec.values.number import NumberValue


@dataclass(frozen=True)
class DummySpec(Spec):
    kind: ClassVar[str] = "dummy_spec_for_claim"
    value_cls: ClassVar[Type[Value]] = NumberValue
    x: int = 0

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "x": self.x,
            "slice": None if self.slice is None else self.slice.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DummySpec":
        return cls(x=int(d["x"]))


Spec.register(DummySpec)


def test_claim_equality():
    c1 = Claim(spec=DummySpec(x=1), value=NumberValue(10))
    c2 = Claim(spec=DummySpec(x=1), value=NumberValue(10))
    c3 = Claim(spec=DummySpec(x=2), value=NumberValue(10))
    c4 = Claim(spec=DummySpec(x=1), value=NumberValue(11))

    assert c1 == c2
    assert c1 != c3
    assert c1 != c4


def test_claim_roundtrip_dict():
    c1 = Claim(spec=DummySpec(x=1), value=NumberValue(10))
    c2 = Claim.from_dict(c1.to_dict())
    assert c1 == c2
