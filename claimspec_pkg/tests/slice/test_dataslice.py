from claimspec.slice.data_slice import DataSlice


def test_group_by_is_canonicalized_sorted_and_unique():
    s = DataSlice(group_by=["b", "a", "a"])
    assert s.group_by == ["a", "b"]


def test_group_by_string_vs_list_equivalence_via_from_dict():
    a = DataSlice.from_dict({"group_by": "a"})
    b = DataSlice.from_dict({"group_by": ["a"]})
    assert a == b
    assert a.group_by == ["a"]


def test_group_by_order_does_not_affect_equality():
    a = DataSlice(group_by=["b", "a"])
    b = DataSlice(group_by=["a", "b"])
    assert a == b
    assert a.group_by == b.group_by == ["a", "b"]
