from claimspec.values.base import Value, InvalidValue
from claimspec.values.number import NumberValue, ApproxNumberValue, IntervalNumberValue


def test_number_number_exact_pass():
    cmp = Value.compare(NumberValue(5), NumberValue(5))
    assert cmp.ok is True
    assert cmp.passed is True


def test_number_number_exact_fail():
    cmp = Value.compare(NumberValue(5), NumberValue(6))
    assert cmp.ok is True
    assert cmp.passed is False
    assert cmp.reason == "value_mismatch"


def test_number_number_tolerance_pass():
    cmp = Value.compare(NumberValue(1.0), NumberValue(1.01), atol=0.02)
    assert cmp.ok is True
    assert cmp.passed is True


def test_approx_number_pass():
    # approx 200 +/- 10 should accept 207
    cmp = Value.compare(ApproxNumberValue(200, atol=10), NumberValue(207))
    assert cmp.ok is True
    assert cmp.passed is True


def test_approx_number_fail():
    cmp = Value.compare(ApproxNumberValue(200, atol=10), NumberValue(215))
    assert cmp.ok is True
    assert cmp.passed is False


def test_interval_number_pass():
    cmp = Value.compare(IntervalNumberValue({"lo": 190, "hi": 210}), NumberValue(207))
    assert cmp.ok is True
    assert cmp.passed is True


def test_interval_number_fail():
    cmp = Value.compare(IntervalNumberValue({"lo": 190, "hi": 210}), NumberValue(189))
    assert cmp.ok is True
    assert cmp.passed is False


def test_approx_interval_pass():
    # approx 200 +/- 10 overlaps interval [205, 220] -> True under overlap semantics
    cmp = Value.compare(ApproxNumberValue(200, atol=10), IntervalNumberValue({"lo": 205, "hi": 220}))
    assert cmp.ok is True
    assert cmp.passed is True


def test_approx_interval_fail():
    # approx 200 +/- 10 does not overlap interval [211, 220]
    cmp = Value.compare(ApproxNumberValue(200, atol=10), IntervalNumberValue({"lo": 211, "hi": 220}))
    assert cmp.ok is True
    assert cmp.passed is False


def test_interval_interval_overlap_pass():
    cmp = Value.compare(
        IntervalNumberValue({"lo": 0, "hi": 10}),
        IntervalNumberValue({"lo": 10, "hi": 20}),
    )
    # inclusive overlap at 10
    assert cmp.ok is True
    assert cmp.passed is True


def test_interval_interval_overlap_fail():
    cmp = Value.compare(
        IntervalNumberValue({"lo": 0, "hi": 9}),
        IntervalNumberValue({"lo": 10, "hi": 20}),
    )
    assert cmp.ok is True
    assert cmp.passed is False


def test_reverse_direction_comparator_resolution():
    """
    Ensure reverse-direction lookup works.

    Example: you may have registered ("approx_number","number") but not ("number","approx_number").
    Value.compare should still find the reverse comparator and work.
    """
    cmp = Value.compare(NumberValue(207), ApproxNumberValue(200, atol=10))
    assert cmp.ok is True
    assert cmp.passed is True


def test_invalid_value_anywhere_is_not_evaluable():
    cmp = Value.compare(InvalidValue(reason="oops"), NumberValue(1))
    assert cmp.ok is False
    assert cmp.passed is None
    assert cmp.reason == "invalid_value"


def test_family_mismatch_not_evaluable():
    @Value.register
    class StringValue(Value):  # minimal stub for test
        kind: str = "string"
        data: str = ""
        family: str = "string"  # type: ignore[assignment]

        def to_dict(self) -> dict:
            return {"kind": self.kind, "data": self.data}

        @classmethod
        def from_dict(cls, d: dict) -> "StringValue":
            return cls(data=str(d.get("data", "")))

    cmp = Value.compare(StringValue("x"), NumberValue(1))
    assert cmp.ok is False
    assert cmp.passed is None
    assert cmp.reason == "family_mismatch"


def test_dict_vs_scalar_broadcast_pass():
    observed = {
        "a": NumberValue(1),
        "b": NumberValue(1),
    }
    expected = NumberValue(1)
    cmp = Value.compare(observed, expected)
    assert cmp.ok is True
    assert cmp.passed is True


def test_dict_vs_scalar_broadcast_fail():
    observed = {
        "a": NumberValue(1),
        "b": NumberValue(2),
    }
    expected = NumberValue(1)
    cmp = Value.compare(observed, expected)
    assert cmp.ok is True
    assert cmp.passed is False
    assert cmp.reason == "broadcast_mismatch"
    assert "per_key" in (cmp.detail or {})


def test_dict_dict_key_mismatch_fails():
    left = {"a": NumberValue(1)}
    right = {"b": NumberValue(1)}
    cmp = Value.compare(left, right)
    assert cmp.ok is True
    assert cmp.passed is False
    assert cmp.reason == "dict_mismatch"
    assert cmp.detail is not None
    assert cmp.detail["missing_left"] == ["b"]
    assert cmp.detail["missing_right"] == ["a"]


def test_dict_dict_per_key_mismatch_reports():
    left = {"a": NumberValue(1), "b": NumberValue(2)}
    right = {"a": NumberValue(1), "b": NumberValue(3)}
    cmp = Value.compare(left, right)
    assert cmp.ok is True
    assert cmp.passed is False
    assert cmp.reason == "dict_mismatch"
    assert cmp.detail is not None
    assert cmp.detail["per_key"]["b"]["passed"] is False
