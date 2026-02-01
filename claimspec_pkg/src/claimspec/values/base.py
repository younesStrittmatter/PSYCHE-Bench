from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Dict, Optional, Tuple, Type, Union


ValueLike = Union["Value", Dict[str, "Value"]]
CompareFn = Callable[["Value", "Value", float, float], bool]
PairKey = Tuple[str, str, str]  # (family, left_kind, right_kind)


@dataclass(frozen=True)
class ValueComparison:
    ok: bool
    passed: Optional[bool]  # None if ok=False
    reason: Optional[str] = None
    detail: Optional[dict] = None


@dataclass(frozen=True)
class Value:
    """
    Base class for all Values.

    IMPORTANT:
    - `kind` is a ClassVar on subclasses (NOT part of __init__).
    - `data` is the main payload and is the first constructor argument.
    """
    data: Any = None

    kind: ClassVar[str] = "value"
    family: ClassVar[str] = ""  # if empty, defaults to kind

    _REGISTRY: ClassVar[Dict[str, Type["Value"]]] = {}
    _PAIRWISE: ClassVar[Dict[PairKey, CompareFn]] = {}

    @property
    def _kind(self) -> str:
        # Instance-level accessor for kind
        return type(self).kind

    @property
    def _family(self) -> str:
        fam = getattr(type(self), "family", "") or ""
        return fam if fam else self._kind

    # ----------------------------
    # Registry for (de)serialization
    # ----------------------------

    @classmethod
    def register(cls, subclass: Type["Value"]) -> Type["Value"]:
        cls._REGISTRY[subclass.kind] = subclass
        return subclass

    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "Value":
        kind = d.get("kind")
        subcls = cls._REGISTRY.get(kind)
        if subcls is None:
            raise ValueError(f"Unknown Value kind: {kind}")
        return subcls.from_dict(d)

    # ----------------------------
    # Pairwise comparator registration
    # ----------------------------

    @classmethod
    def register_compare(cls, family: str, left_kind: str, right_kind: str, fn: CompareFn) -> None:
        """
        Register comparator for (family, left_kind, right_kind).
        You can register only one direction; reverse direction will be tried automatically.
        """
        cls._PAIRWISE[(family, left_kind, right_kind)] = fn

    # ----------------------------
    # Public comparison entrypoint
    # ----------------------------

    @classmethod
    def compare(cls, a: ValueLike, b: ValueLike, *, rtol: float = 0.0, atol: float = 0.0) -> ValueComparison:
        # Reject dicts that are not dict[str, Value]
        if isinstance(a, dict) and not _is_grouped(a):
            return ValueComparison(
                ok=False,
                passed=None,
                reason="invalid_grouped_value",
                detail={"side": "left", "note": "dict values must all be Value"},
            )
        if isinstance(b, dict) and not _is_grouped(b):
            return ValueComparison(
                ok=False,
                passed=None,
                reason="invalid_grouped_value",
                detail={"side": "right", "note": "dict values must all be Value"},
            )

        # invalid anywhere => not evaluable
        if _contains_invalid(a) or _contains_invalid(b):
            return ValueComparison(
                ok=False,
                passed=None,
                reason="invalid_value",
                detail={"left": _to_dictish(a), "right": _to_dictish(b)},
            )

        a_is_grouped = isinstance(a, dict)
        b_is_grouped = isinstance(b, dict)

        # scalar-scalar
        if not a_is_grouped and not b_is_grouped:
            return cls._compare_scalar(a, b, rtol=rtol, atol=atol)

        # grouped-grouped
        if a_is_grouped and b_is_grouped:
            return _compare_grouped_grouped(a, b, rtol=rtol, atol=atol)

        # grouped-scalar / scalar-grouped => broadcast scalar to each key
        if a_is_grouped and not b_is_grouped:
            return _compare_grouped_scalar(a, b, rtol=rtol, atol=atol, direction="grouped_vs_scalar")
        if b_is_grouped and not a_is_grouped:
            return _compare_grouped_scalar(b, a, rtol=rtol, atol=atol, direction="scalar_vs_grouped")

        return ValueComparison(ok=False, passed=None, reason="internal_error")

    @classmethod
    def _compare_scalar(cls, a: "Value", b: "Value", *, rtol: float, atol: float) -> ValueComparison:
        fa = a._family
        fb = b._family
        if fa != fb:
            return ValueComparison(
                ok=False,
                passed=None,
                reason="family_mismatch",
                detail={"left_family": fa, "right_family": fb, "left_kind": a._kind, "right_kind": b._kind},
            )

        left_kind = a._kind
        right_kind = b._kind

        fn = cls._PAIRWISE.get((fa, left_kind, right_kind))
        if fn is None:
            # Try reverse direction
            fn_rev = cls._PAIRWISE.get((fa, right_kind, left_kind))
            if fn_rev is not None:
                same = fn_rev(b, a, rtol, atol)
                return ValueComparison(
                    ok=True,
                    passed=same,
                    reason=None if same else "value_mismatch",
                    detail=None if same else {"left": a.to_dict(), "right": b.to_dict()},
                )

            # Default: if same kind, compare data exactly
            if left_kind == right_kind:
                same = (a.data == b.data)
                return ValueComparison(
                    ok=True,
                    passed=same,
                    reason=None if same else "value_mismatch",
                    detail=None if same else {"left": a.to_dict(), "right": b.to_dict()},
                )

            return ValueComparison(
                ok=False,
                passed=None,
                reason="no_comparator",
                detail={"family": fa, "left_kind": left_kind, "right_kind": right_kind},
            )

        same = fn(a, b, rtol, atol)
        return ValueComparison(
            ok=True,
            passed=same,
            reason=None if same else "value_mismatch",
            detail=None if same else {"left": a.to_dict(), "right": b.to_dict()},
        )


@Value.register
@dataclass(frozen=True)
class InvalidValue(Value):
    kind: ClassVar[str] = "invalid"

    # keep data for symmetry; can ignore
    data: Any = None
    reason: str = ""
    detail: Optional[dict] = None

    def to_dict(self) -> dict:
        return {"kind": self._kind, "data": self.data, "reason": self.reason, "detail": self.detail}

    @classmethod
    def from_dict(cls, d: dict) -> "InvalidValue":
        return cls(data=d.get("data"), reason=d.get("reason", ""), detail=d.get("detail"))


# ----------------------------
# helpers
# ----------------------------

def _is_grouped(d: dict) -> bool:
    return all(isinstance(v, Value) for v in d.values())


def _contains_invalid(x: ValueLike) -> bool:
    if isinstance(x, InvalidValue):
        return True
    if isinstance(x, dict):
        return any(isinstance(v, InvalidValue) for v in x.values())
    return False


def _compare_grouped_grouped(a: Dict[str, Value], b: Dict[str, Value], *, rtol: float, atol: float) -> ValueComparison:
    a_keys = set(a.keys())
    b_keys = set(b.keys())

    missing_left = sorted(list(b_keys - a_keys))
    missing_right = sorted(list(a_keys - b_keys))

    per_key: Dict[str, Any] = {}
    passed = True

    for k in sorted(list(a_keys & b_keys)):
        av = a[k]
        bv = b[k]

        cmp = Value.compare(av, bv, rtol=rtol, atol=atol)
        if not cmp.ok:
            return ValueComparison(ok=False, passed=None, reason=cmp.reason, detail={"key": k, **(cmp.detail or {})})

        per_key[k] = {"passed": cmp.passed, "left": av.to_dict(), "right": bv.to_dict()}
        if not cmp.passed:
            passed = False

    if missing_left or missing_right:
        passed = False

    return ValueComparison(
        ok=True,
        passed=passed,
        reason=None if passed else "dict_mismatch",
        detail=None if passed else {"missing_left": missing_left, "missing_right": missing_right, "per_key": per_key},
    )


def _compare_grouped_scalar(d: Dict[str, Value], scalar: Value, *, rtol: float, atol: float, direction: str) -> ValueComparison:
    per_key: Dict[str, Any] = {}
    passed = True

    for k in sorted(d.keys()):
        v = d[k]
        cmp = Value.compare(v, scalar, rtol=rtol, atol=atol)
        if not cmp.ok:
            return ValueComparison(ok=False, passed=None, reason=cmp.reason, detail={"key": k, **(cmp.detail or {})})

        per_key[k] = {"passed": cmp.passed, "left": v.to_dict(), "right": scalar.to_dict()}
        if not cmp.passed:
            passed = False

    return ValueComparison(
        ok=True,
        passed=passed,
        reason=None if passed else "broadcast_mismatch",
        detail=None if passed else {"direction": direction, "per_key": per_key},
    )


def _to_dictish(x: ValueLike) -> Any:
    if isinstance(x, dict):
        return {k: v.to_dict() for k, v in x.items()}
    return x.to_dict()
