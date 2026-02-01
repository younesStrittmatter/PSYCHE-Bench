from __future__ import annotations
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
IN_PATH = HERE / "exp1_legacy.csv"
OUT_PATH = HERE / "exp1.csv"

STRUCTURE_TYPE = {
    1: "type_i",
    2: "type_ii",
    3: "type_iii",
    4: "type_iv",
}

def main():
    df = pd.read_csv(IN_PATH)


    # --- Add subject_id (standard alias) ---
    df["subject_id"] = df["participant"]

    # --- Add correct (0/1) from reward (-1/1) ---
    unique_rewards = set(df["reward"].dropna().unique())
    if not unique_rewards.issubset({-1, 0, 1}):
        raise ValueError(f"Unexpected reward values: {sorted(unique_rewards)}")

    df["correct"] = df["reward"].map({1: 1, -1: 0, 0: 0}).astype(int)

    # --- Add factor_structure_type ---
    unique_conditions = set(df["condition"].dropna().unique())
    if not unique_conditions.issubset({1, 2, 3, 4}):
        raise ValueError(f"Unexpected condition values: {sorted(unique_conditions)}")

    df["factor_structure_type"] = df["condition"].map(STRUCTURE_TYPE)

    df.to_csv(OUT_PATH, index=False)


if __name__ == "__main__":
    main()
