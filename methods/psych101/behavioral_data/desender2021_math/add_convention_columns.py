from __future__ import annotations
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
IN_PATH = HERE / "exp1_legacy.csv"
OUT_PATH = HERE / "exp1.csv"


def main():
    df = pd.read_csv(IN_PATH)

    # --- Add subject_id (standard alias) ---
    df["subject_id"] = df["participant"]

    df.to_csv(OUT_PATH, index=False)


if __name__ == "__main__":
    main()
