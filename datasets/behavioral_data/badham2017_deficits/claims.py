from __future__ import annotations

from claimspec.claims.claim import Claim
from claimspec.specs.count_unique import CountUnique
from claimspec.specs.stats_descriptive import Mean, Std
from claimspec.slice.data_slice import DataSlice
from claimspec.slice.row_filter import Eq, And
from claimspec.slice.aggregate import Const, MeanAgg
from claimspec.values.number import NumberValue, ApproxNumberValue
from claimspec.conventions import ColumnSpecCategorical, Convention
from datasets.behavioral_data.standard import DATASET_CONVENTION

PAPER_CONVENTION = Convention(
    name="paper convention badham 2017: Deficits...",
    columns=[
        ColumnSpecCategorical(
            name="age_group",
            description="Age group labeled young and older",
            levels=("young", "older"),
        ),
        ColumnSpecCategorical(
            name="factor_structure_type",
            description="Shepard, Hovland & Jenkins (1961) category structure type used in this condition.",
            levels=["type_i", "type_ii", "type_iii", "type_iv"],
        ),
    ]

)

EXP1_CLAIMS = [
    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.subject_id
        ),
        value=NumberValue(96),
    ),
    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.subject_id,
            slice=DataSlice(
                row_filter=Eq(
                    col=PAPER_CONVENTION.age_group,
                    value=PAPER_CONVENTION.age_group.young,
                )
            ),
        ),
        value=NumberValue(48),
    ),
    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.subject_id,
            slice=DataSlice(
                row_filter=Eq(
                    col=PAPER_CONVENTION.age_group,
                    value=PAPER_CONVENTION.age_group.older,
                )
            ),
        ),
        value=NumberValue(48),
    ),
    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.subject_id,
            slice=DataSlice(
                row_filter=And(items=[
                    Eq(col=PAPER_CONVENTION.age_group, value=PAPER_CONVENTION.age_group.young),
                    Eq(col=DATASET_CONVENTION.sex, value=DATASET_CONVENTION.sex.female)
                ])
            ),
        ),
        value=NumberValue(42),
    ),
    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.subject_id,
            slice=DataSlice(
                row_filter=And(items=[
                    Eq(col=PAPER_CONVENTION.age_group, value=PAPER_CONVENTION.age_group.older),
                    Eq(col=DATASET_CONVENTION.sex, value=DATASET_CONVENTION.sex.female)
                ])
            ),
        ),
        value=NumberValue(32),
    ),

    Claim(
        spec=Mean(
            col=DATASET_CONVENTION.age,
            slice=DataSlice(
                row_filter=Eq(
                    col=PAPER_CONVENTION.age_group,
                    value=PAPER_CONVENTION.age_group.young,
                ),
                aggregates=[
                    Const(by=[DATASET_CONVENTION.subject_id], cols=[DATASET_CONVENTION.age])
                ],
            ),
        ),
        value=ApproxNumberValue(19.3, atol=.05),
    ),

    Claim(
        spec=Std(
            col=DATASET_CONVENTION.age,
            slice=DataSlice(
                row_filter=Eq(
                    col=PAPER_CONVENTION.age_group,
                    value=PAPER_CONVENTION.age_group.young,
                ),
                aggregates=[
                    Const(by=[DATASET_CONVENTION.subject_id], cols=[DATASET_CONVENTION.age])
                ],
            ),
        ),
        value=ApproxNumberValue(0.7, atol=.05),
    ),

    Claim(
        spec=Mean(
            col=DATASET_CONVENTION.age,
            slice=DataSlice(
                row_filter=Eq(
                    col=PAPER_CONVENTION.age_group,
                    value=PAPER_CONVENTION.age_group.older,
                ),
                aggregates=[
                    Const(by=[DATASET_CONVENTION.subject_id], cols=[DATASET_CONVENTION.age])
                ],
            ),
        ),
        value=ApproxNumberValue(74.7, atol=.05),
    ),

    Claim(
        spec=Std(
            col=DATASET_CONVENTION.age,
            slice=DataSlice(
                row_filter=Eq(
                    col=PAPER_CONVENTION.age_group,
                    value=PAPER_CONVENTION.age_group.older,
                ),
                aggregates=[
                    MeanAgg(by=[DATASET_CONVENTION.subject_id], cols=[DATASET_CONVENTION.age])
                ],
            ),
        ),
        value=ApproxNumberValue(5.6, .05),
    ),

    # TODO: Paper reports accuracy with post-criterion padding (assume 100% for uncompleted blocks).
    # Raw trial means won’t match without an analysis transform. Revisit later.

    # Claim(
    #     spec=Mean(
    #         col=DATASET_CONVENTION.correct,
    #         slice=DataSlice(
    #             row_filter=And(items=[
    #                 Eq(col=PAPER_CONVENTION.age_group, value=PAPER_CONVENTION.age_group.older),
    #                 Eq(col=PAPER_CONVENTION.factor_structure_type,
    #                    value=PAPER_CONVENTION.factor_structure_type.type_iv),
    #             ]),
    #             aggregates=[MeanAgg(by=[DATASET_CONVENTION.subject_id], cols=[DATASET_CONVENTION.correct])]
    #         ),
    #     ),
    #     value=ApproxNumberValue(0.62, atol=0.005),
    # ),
    #
    # Claim(
    #     spec=Mean(
    #         col=DATASET_CONVENTION.correct,
    #         slice=DataSlice(
    #             row_filter=And(items=[
    #                 Eq(col=PAPER_CONVENTION.age_group, value=PAPER_CONVENTION.age_group.older),
    #                 Eq(col=PAPER_CONVENTION.factor_structure_type,
    #                    value=PAPER_CONVENTION.factor_structure_type.type_ii),
    #             ]),
    #             aggregates=[MeanAgg(by=[DATASET_CONVENTION.subject_id], cols=[DATASET_CONVENTION.correct])]
    #         ),
    #     ),
    #     value=ApproxNumberValue(0.57, atol=0.005),
    # ),
    #
    # Claim(
    #     spec=Mean(
    #         col=DATASET_CONVENTION.correct,
    #         slice=DataSlice(
    #             row_filter=And(items=[
    #                 Eq(col=PAPER_CONVENTION.age_group, value=PAPER_CONVENTION.age_group.young),
    #                 Eq(col=PAPER_CONVENTION.factor_structure_type,
    #                    value=PAPER_CONVENTION.factor_structure_type.type_ii),
    #             ]),
    #             aggregates=[MeanAgg(by=[DATASET_CONVENTION.subject_id], cols=[DATASET_CONVENTION.correct])]
    #         ),
    #     ),
    #     value=ApproxNumberValue(0.74, atol=0.005),
    # ),
    #
    # Claim(
    #     spec=Mean(
    #         col=DATASET_CONVENTION.correct,
    #         slice=DataSlice(
    #             row_filter=And(items=[
    #                 Eq(col=PAPER_CONVENTION.age_group, value=PAPER_CONVENTION.age_group.young),
    #                 Eq(col=PAPER_CONVENTION.factor_structure_type,
    #                    value=PAPER_CONVENTION.factor_structure_type.type_iv),
    #             ]),
    #             aggregates=[MeanAgg(by=[DATASET_CONVENTION.subject_id], cols=[DATASET_CONVENTION.correct])]
    #         ),
    #     ),
    #     value=ApproxNumberValue(0.72, atol=0.005)
    # )
]
