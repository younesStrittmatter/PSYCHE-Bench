import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve()
while not (ROOT / "datasets").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

DATA_PATH = ROOT / "datasets" / "behavioral_data" / "bahrami2020_four" / "original_data" / "raw_dat.csv"
OUT_PATH = './exp1.csv'


def main():
    df = pd.read_csv(DATA_PATH)


    print("rows:", len(df))
    print("missing id:", df["id"].isna().sum())
    print("unique id:", df["id"].nunique(dropna=True))

    # ----------------------------
    # Standardize column names
    # ----------------------------
    df = df.rename(columns={
        "id": "subject_id",
    })

    # ----------------------------
    # Reindex subject IDs (0-based)
    # ----------------------------
    df["subject_id"] = df["subject_id"].astype(int)
    unique_subjects = sorted(df["subject_id"].unique())
    subject_map = {sid: i for i, sid in enumerate(unique_subjects)}
    df["subject_id"] = df["subject_id"].map(subject_map)

    # ----------------------------
    # Trial index per subject (0..149)
    # ----------------------------
    df["trial"] = df.groupby("subject_id").cumcount()

    # show first 10 trials for a couple subjects
    print(df[df["subject_id"].isin([0, 1])][["subject_id", "trial"]].head(12))

    # check distribution
    print(df.groupby("subject_id")["trial"].agg(["min", "max", "count"]).head())

    # assert exactly 0..149 for every subject
    assert (df.groupby("subject_id")["trial"].min() == 0).all()
    assert (df.groupby("subject_id")["trial"].max() == 149).all()
    assert (df.groupby("subject_id")["trial"].count() == 150).all()

    # Optional safety check
    trials_per_subj = df.groupby("subject_id")["trial"].max() + 1
    if not (trials_per_subj == 150).all():
        raise ValueError("Not all subjects have 150 trials — check raw data.")

    # ----------------------------
    # Normalize choice to 0-based
    # ----------------------------
    df["choice"] = df["choice"] - 1  # 0–3 instead of 1–4

    # ----------------------------
    # Add task label
    # ----------------------------
    df["task"] = "four_armed_bandit"

    # ----------------------------
    # Save standardized file
    # ----------------------------
    df.to_csv(OUT_PATH, index=False)
    print(f"Saved standardized dataset to: {OUT_PATH}")


if __name__ == '__main__':
    main()
