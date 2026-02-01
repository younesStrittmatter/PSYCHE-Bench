import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve()
while not (ROOT / "datasets").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

ORIGINAL_DATA_ROOT = ROOT / "datasets" / "behavioral_data" / "binz2022_heuristics" / "original_data"
files = [
    ORIGINAL_DATA_ROOT / "exp1.csv",
    ORIGINAL_DATA_ROOT / "exp2.csv",
    ORIGINAL_DATA_ROOT / "exp3.csv",
]

for i, file in enumerate(files):
    df = pd.read_csv(file)

    # add correct
    df["correct"] = (df["choice"] == df["target"]).astype(int)

    # add reward
    df["reward"] = 2 * ((df["choice"] == df["target"]).astype(float) - 0.5)

    # rearrange columns (as before)
    if i < 2:
        df = df[
            ["participant", "task", "step", "choice", "reward", "x0", "x1", "x2", "x3", "target", "time", "correct"]]
        df.columns = ["participant", "task", "trial_within_task", "choice", "reward", "x0", "x1", "x2", "x3", "target",
                      "time", "correct"]
    else:
        df = df[["participant", "task", "step", "choice", "reward", "x0", "x1", "target", "time", "correct"]]
        df.columns = ["participant", "task", "trial_within_task", "choice", "reward", "x0", "x1", "target", "time",
                      "correct"]

    # rename participant → subject_id
    df = df.rename(columns={"participant": "subject_id"})

    # NEW: canonical trial = 0-based sequential trial per subject
    sort_cols = [c for c in ["subject_id", "task", "trial_within_task", "time"] if c in df.columns]
    df = df.sort_values(sort_cols, kind="mergesort")

    df["trial"] = df.groupby("subject_id", sort=False).cumcount()

    # sanity check: trial is contiguous per subject
    g = df.groupby("subject_id")["trial"]
    assert (g.min() == 0).all()
    assert (g.max() + 1 == g.count()).all()

    # save
    df.to_csv(f"exp{i + 1}.csv", index=False)
    print(f"wrote exp{i + 1}.csv  rows={len(df):,}  subjects={df['subject_id'].nunique():,}")
