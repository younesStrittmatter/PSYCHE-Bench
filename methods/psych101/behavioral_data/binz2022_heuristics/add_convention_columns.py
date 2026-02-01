from __future__ import annotations
import pandas as pd

IN_FILES = ["./exp1_legacy.csv", "./exp2_legacy.csv", "./exp3_legacy.csv"]
OUT_FILES = ["./exp1.csv", "./exp2.csv", "./exp3.csv"]

def main():
    for in_file, out_file in zip(IN_FILES, OUT_FILES):
        df = pd.read_csv(in_file)

        # Rename columns to standard
        df = df.rename(columns={
            "participant": "subject_id",
            "trial": "trial_within_task",
        })

        # Add canonical trial: sequential per subject
        df["trial"] = df.groupby("subject_id").cumcount()

        df["correct"] = (df["choice"] == df["target"]).astype(int)

        df.to_csv(out_file, index=False)

if __name__ == "__main__":
    main()
