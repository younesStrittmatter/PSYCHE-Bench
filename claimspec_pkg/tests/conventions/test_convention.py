from claimspec.conventions import ColumnSpec, Convention

PSYCHE_STANDARD_V0 = Convention(
    name="psyche_standard_v0",
    columns=(
        ColumnSpec(
            "participant",
            "Unique participant identifier (unordered label).",
        ),
        ColumnSpec(
            "experiment",
            "Experiment identifier ordered by appearance in the paper: exp1, exp2, ...",
        ),
    ),
    notes=(
        "Descriptive only: a dataset may omit these columns unless a claim/spec requires them.",
    ),
)


def test_standard_roundtrip():
    s2 = Convention.from_dict(PSYCHE_STANDARD_V0.to_dict())
    assert s2 == PSYCHE_STANDARD_V0


def test_get_column_description():
    c = PSYCHE_STANDARD_V0.get_column("experiment")
    assert c is not None
    assert "exp1" in c.description
