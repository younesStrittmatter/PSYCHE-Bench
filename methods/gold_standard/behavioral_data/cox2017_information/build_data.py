import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve()
while not (ROOT / "datasets").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

ORIGINAL_DATA_ROOT = ROOT / "datasets" / "behavioral_data" / "cox2017_information" / "original_data"


def main():
    df = pd.read_csv(ORIGINAL_DATA_ROOT / "all_data_studytest.csv")

    print("unique original subjects:", df["subject"].nunique())  # should be 462

    # Reward mapping
    def map_reward(resp_type: str):
        if resp_type in ["Hit", "CR"]:
            return 1
        if resp_type in ["Miss", "FA"]:
            return -1
        return None

    df["reward"] = df["resp.type"].apply(map_reward)

    # Keep and rename columns
    df = df[
        [
            "subject",
            "block",
            "trial",
            "phase",
            "condition",
            "resp",
            "resp.type",
            "resp.string",
            "reward",
            "rt",
            "stim.string.left",
            "stim.string.right",
        ]
    ].copy()

    df.columns = [
        "subject_id",          # raw subject label (will be reindexed later)
        "task",                # raw task label (string)
        "trial",               # original trial index (we'll rebuild later)
        "phase",
        "condition",
        "choice",
        "resp.type",
        "resp.string",
        "reward",
        "rt",
        "stim.string.left",
        "stim.string.right",
    ]

    # ----------------------------
    # Build study lists per (subject, task) from study phase
    # ----------------------------
    study = df[df["phase"] == "study"].copy()

    # If there are NaNs, drop them so lists are clean
    study_lists = (
        study.groupby(["subject_id", "task"], as_index=False)
        .agg(
            **{
                "study.list.left": ("stim.string.left", lambda s: [x for x in s.tolist() if pd.notna(x)]),
                "study.list.right": ("stim.string.right", lambda s: [x for x in s.tolist() if pd.notna(x)]),
            }
        )
    )

    # ----------------------------
    # Keep only test trials and attach study lists
    # ----------------------------
    test = df[df["phase"] == "test"].copy()

    test = test.merge(
        study_lists,
        on=["subject_id", "task"],
        how="left",
    )

    # Lexical decision has no study phase → ensure empty lists (not NaN)
    test["study.list.left"] = test["study.list.left"].apply(lambda x: x if isinstance(x, list) else [])
    test["study.list.right"] = test["study.list.right"].apply(lambda x: x if isinstance(x, list) else [])

    # ----------------------------
    # Robust reindexing (no row-order bugs)
    # ----------------------------
    # Stable ordering (optional but helps make outputs deterministic)
    test = test.sort_values(["subject_id", "task", "trial"]).reset_index(drop=True)

    # Global subject reindex: 0..n-1
    test["subject_id"] = pd.factorize(test["subject_id"])[0]

    # Task reindex within subject: 0..k-1
    test["task"] = test.groupby("subject_id")["task"].transform(lambda s: pd.factorize(s)[0])

    # Trial reindex within (subject, task): 0..N-1
    test["trial"] = test.groupby(["subject_id", "task"]).cumcount()

    # ----------------------------
    # Save
    # ----------------------------
    outpath = Path("exp1.csv")
    test.to_csv(outpath, index=False)

    print("wrote:", outpath.resolve())
    print("unique subjects in export:", test["subject_id"].nunique())


if __name__ == "__main__":
    main()
