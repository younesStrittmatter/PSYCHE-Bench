from __future__ import annotations

from claimspec.claims.claim import Claim
from claimspec.specs.count_unique import CountUnique
from claimspec.specs.stats_descriptive import Mean, Std
from claimspec.slice.data_slice import DataSlice
from claimspec.slice.row_filter import Eq
from claimspec.values.number import NumberValue, ApproxNumberValue
from claimspec.slice.aggregate import MeanAgg
from claimspec.conventions import Convention, ColumnSpecCategorical

from datasets.behavioral_data.standard import DATASET_CONVENTION

EXP1_CLAIMS = [
    Claim(
        spec=CountUnique(col=DATASET_CONVENTION.subject_id),
        value=NumberValue(28),
    ),

    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.trial,
            slice=DataSlice(group_by=[DATASET_CONVENTION.subject_id]),
        ),
        value=NumberValue(300),
    ),
    Claim(
        spec=Mean(
            col=DATASET_CONVENTION.correct,
            slice=DataSlice(
                aggregates=[
                    MeanAgg(
                        by=[DATASET_CONVENTION.subject_id],
                        cols=[DATASET_CONVENTION.correct],
                    )
                ]
            ),
        ),
        value=ApproxNumberValue(0.6825, atol=0.01),
    )
]

EXP2_CLAIMS = [
    Claim(
        spec=CountUnique(col=DATASET_CONVENTION.subject_id),
        value=NumberValue(24),
    ),
    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.trial,
            slice=DataSlice(group_by=[DATASET_CONVENTION.subject_id]),
        ),
        value=NumberValue(300),
    ),
    Claim(
        spec=Mean(
            col=DATASET_CONVENTION.correct,
            slice=DataSlice(
                aggregates=[
                    MeanAgg(
                        by=[DATASET_CONVENTION.subject_id],
                        cols=[DATASET_CONVENTION.correct],
                    )
                ]
            ),
        ),
        value=ApproxNumberValue(0.7385, atol=0.01),
    )

]

EXP3_CLAIMS = [
    Claim(
        spec=CountUnique(col=DATASET_CONVENTION.subject_id),
        value=NumberValue(27),
    ),
    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.trial,
            slice=DataSlice(group_by=[DATASET_CONVENTION.subject_id]),
        ),
        value=NumberValue(300),
    ),
    Claim(
        spec=Mean(
            col=DATASET_CONVENTION.correct,
            slice=DataSlice(
                aggregates=[
                    MeanAgg(
                        by=[DATASET_CONVENTION.subject_id],
                        cols=[DATASET_CONVENTION.correct],
                    )
                ]
            ),
        ),
        value=ApproxNumberValue(0.7159, atol=0.01),
    )

]
