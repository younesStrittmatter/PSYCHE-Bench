from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from claimspec.values.base import Value


@Value.register
@dataclass(frozen=True)
class NumberValue(Value):
    kind: ClassVar[str] = "number"
    family: ClassVar[str] = "number"

    data: int | float = 0

    def to_dict(self) -> dict:
        return {"kind": self._kind, "data": self.data}

    @classmethod
    def from_dict(cls, d: dict) -> "NumberValue":
        return cls(data=d.get("data", 0))


@Value.register
@dataclass(frozen=True)
class ApproxNumberValue(Value):
    kind: ClassVar[str] = "approx_number"
    family: ClassVar[str] = "number"

    data: int | float = 0
    atol: float = 0.0
    rtol: float = 0.0

    def to_dict(self) -> dict:
        return {"kind": self._kind, "data": self.data, "atol": self.atol, "rtol": self.rtol}

    @classmethod
    def from_dict(cls, d: dict) -> "ApproxNumberValue":
        return cls(
            data=d.get("data", 0),
            atol=float(d.get("atol", 0.0)),
            rtol=float(d.get("rtol", 0.0)),
        )


@Value.register
@dataclass(frozen=True)
class IntervalNumberValue(Value):
    kind: ClassVar[str] = "interval_number"
    family: ClassVar[str] = "number"

    # IMPORTANT: tests call IntervalNumberValue({"lo":..,"hi":..}) positionally
    data: dict

    def __post_init__(self):
        # normalize + allow swapped bounds
        lo = float(self.data.get("lo", 0.0))
        hi = float(self.data.get("hi", 0.0))
        if lo > hi:
            lo, hi = hi, lo
        object.__setattr__(self, "data", {"lo": lo, "hi": hi})

    def to_dict(self) -> dict:
        return {"kind": self._kind, "data": {"lo": float(self.data["lo"]), "hi": float(self.data["hi"])}}

    @classmethod
    def from_dict(cls, d: dict) -> "IntervalNumberValue":
        dd = d.get("data") or {}
        return cls({"lo": float(dd.get("lo", 0.0)), "hi": float(dd.get("hi", 0.0))})


# ----------------------------
# Comparators for family="number"
# ----------------------------

def _num(x) -> float:
    return float(x)


def _interval_from_number(v: float, *, rtol: float, atol: float) -> tuple[float, float]:
    tol = float(atol) + float(rtol) * abs(v)
    return (v - tol, v + tol)


def _interval_from_approx(center: float, *, rtol: float, atol: float, a_rtol: float, a_atol: float) -> tuple[float, float]:
    tol = (float(a_atol) + float(atol)) + (float(a_rtol) + float(rtol)) * abs(center)
    return (center - tol, center + tol)


def _overlaps(a: tuple[float, float], b: tuple[float, float]) -> bool:
    alo, ahi = a
    blo, bhi = b
    return not (ahi < blo or bhi < alo)


def _cmp_number_number(a: Value, b: Value, rtol: float, atol: float) -> bool:
    av = _num(a.data)
    bv = _num(b.data)
    diff = abs(av - bv)
    tol = float(atol) + float(rtol) * abs(bv)
    return diff <= tol


def _cmp_approx_number(a: Value, b: Value, rtol: float, atol: float) -> bool:
    center = _num(a.data)
    x = _num(b.data)
    a_atol = float(getattr(a, "atol", 0.0))
    a_rtol = float(getattr(a, "rtol", 0.0))
    lo, hi = _interval_from_approx(center, rtol=rtol, atol=atol, a_rtol=a_rtol, a_atol=a_atol)
    return lo <= x <= hi


def _cmp_interval_number(a: Value, b: Value, rtol: float, atol: float) -> bool:
    lo = _num(a.data["lo"])
    hi = _num(a.data["hi"])
    x = _num(b.data)
    return lo <= x <= hi


def _cmp_interval_interval(a: Value, b: Value, rtol: float, atol: float) -> bool:
    return _overlaps((_num(a.data["lo"]), _num(a.data["hi"])), (_num(b.data["lo"]), _num(b.data["hi"])))


def _cmp_approx_interval(a: Value, b: Value, rtol: float, atol: float) -> bool:
    # overlap semantics (matches your tests)
    center = _num(a.data)
    a_atol = float(getattr(a, "atol", 0.0))
    a_rtol = float(getattr(a, "rtol", 0.0))
    a_int = _interval_from_approx(center, rtol=rtol, atol=atol, a_rtol=a_rtol, a_atol=a_atol)

    b_int = (_num(b.data["lo"]), _num(b.data["hi"]))
    return _overlaps(a_int, b_int)


# Register comparators (reverse direction handled by Value.compare)
Value.register_compare("number", "number", "number", _cmp_number_number)
Value.register_compare("number", "approx_number", "number", _cmp_approx_number)
Value.register_compare("number", "interval_number", "number", _cmp_interval_number)
Value.register_compare("number", "interval_number", "interval_number", _cmp_interval_interval)
Value.register_compare("number", "approx_number", "interval_number", _cmp_approx_interval)
