from __future__ import annotations

from claimspec.claims.claim import Claim
from claimspec.specs.count_unique import CountUnique
from claimspec.specs.stats_descriptive import Mean

from claimspec.slice.data_slice import DataSlice
from claimspec.slice.row_filter import Eq
from claimspec.slice.aggregate import Const
from claimspec.values.number import NumberValue
from claimspec.values.number import ApproxNumberValue

from datasets.behavioral_data.standard import DATASET_CONVENTION

EXP1_CLAIMS = [
    # -----------------------
    # Sample / demographics
    # -----------------------
    Claim(
        spec=CountUnique(col=DATASET_CONVENTION.subject_id),
        value=NumberValue(80),
    ),

    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.subject_id,
            slice=DataSlice(
                row_filter=Eq(col=DATASET_CONVENTION.sex, value=DATASET_CONVENTION.sex.male),
            ),
        ),
        value=NumberValue(11),
    ),
    #
    Claim(
        spec=Mean(
            col=DATASET_CONVENTION.age,
            slice=DataSlice(
                aggregates=[
                    Const(by=[DATASET_CONVENTION.subject_id], cols=[DATASET_CONVENTION.age])
                ],
            ),
        ),
        value=ApproxNumberValue(19.7, atol=0.05),  # “mean age = 19.7 years”
    ),
    # -----------------------
    # Procedure structure
    # -----------------------
    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.trial,
            slice=DataSlice(group_by=[DATASET_CONVENTION.subject_id]),
        ),
        value=NumberValue(264),  # “presented with 264 arithmetic problems” / 6*44
    ),
]
