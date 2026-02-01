from claimspec.conventions import ColumnSpecCategorical, ColumnSpec, Convention

DATASET_CONVENTION = Convention(
    name="Behavioral Data Standard",
    columns=[
        ColumnSpecCategorical(
            name="subject_id",
            description="Unique subject identifier.",
        ),
        ColumnSpecCategorical(
            name="correct",
            description="Trial level accuracy. 1 == correct response. 0 == incorrect response.",
            levels=[0, 1],
        ),
        ColumnSpec(
            name="age",
            description="Age of the subject (years, unless otherwise specified).",
        ),
        ColumnSpecCategorical(
            name="sex",
            description="Reported/recorded sex of the subject.",
            levels=("male", "female"),
        ),
        ColumnSpec(
            name="factor_*",
            description="Experimental factor column: the task variant / condition active on this trial. "
                        "For crossed designs, represent each manipulated factor in its own `factor_*` column."
        ),
        ColumnSpecCategorical(
            name="trial",
            description="Trial number. 0-based sequential trial index *within subject*.",
        ),
        ColumnSpecCategorical(
            name="phase",
            description=(
                "Functional stage of the experimental procedure. "
                "'study' = exposure or encoding of task-relevant information; "
                "'distractor' = intervening task intended to disrupt rehearsal or introduce delay; "
                "'test' = performance measurement phase (retrieval, decision, or response)."
            ),
            levels=("study", "distractor", "test"),
        ),
        ColumnSpecCategorical(
            name="block",
            description=(
                "Within-subject block index (0-based), indicating a contiguous chunk of the experiment "
                "as organized by the experimenter, typically separated by instruction screens, pauses, "
                "or changes in procedure. Blocks reflect the temporal structure of the experiment, "
                "not experimental conditions. Any manipulated block properties (e.g., block type, "
                "repetition number, task identity) are encoded as paper-specific factor_* columns."
            ),
        )

    ],
)
