import pandas as pd

from claimspec.specs.count_unique import CountUnique
from claimspec.slice.data_slice import DataSlice
from claimspec.slice.row_filter import Cmp
from claimspec.values.number import NumberValue


def test_count_unique_no_grouping_with_filter():
    df = pd.DataFrame(
        {
            "participant": ["p1", "p1", "p2", "p2", "p3", "p3"],
            "cond": ["A", "B", "A", "A", "B", "A"],
            "trial": [1, 2, 1, 2, 1, 1],
        }
    )

    spec = CountUnique(
        col="trial",
        slice=DataSlice(row_filter=Cmp(op="==", key="cond", value="A")),
    )

    res = spec.apply(df)

    assert isinstance(res, NumberValue)
    assert res.data == 2


def test_count_unique_grouped_by_participant_with_filter():
    df = pd.DataFrame(
        {
            "participant": ["p1", "p1", "p2", "p2", "p3", "p3"],
            "cond": ["A", "B", "A", "A", "B", "A"],
            "trial": [1, 2, 1, 2, 1, 1],
        }
    )

    spec = CountUnique(
        col="trial",
        slice=DataSlice(
            row_filter=Cmp(op="==", key="cond", value="A"),
            group_by=["participant"],
        ),
    )

    res = spec.apply(df)

    assert isinstance(res, dict)
    assert set(res.keys()) == {"p1", "p2", "p3"}
    assert res["p1"].data == 1
    assert res["p2"].data == 2
    assert res["p3"].data == 1
