import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve()
while not (ROOT / "datasets").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

TRIAL_DATA_PATH = ROOT / "datasets" / "behavioral_data" / "badham2017_deficits" / "original_data" / "Badham_Sanborn_Maylor_2017_trial_by_trial_data.csv"
DEMOGRAPHIC_DATA_PATH = ROOT / "datasets" / "behavioral_data" / "badham2017_deficits" / "original_data" / "Badham_Sanborn_Maylor_2017_aggregate_data.csv"

CONDITIONS = {"TYPEONE": 1, "TYPETWO": 2, "TYPETHREE": 3, "TYPEFOUR": 4}
STRUCTURE_TYPE = {1: "type_i", 2: "type_ii", 3: "type_iii", 4: "type_iv"}

FEATURES = {
    "BigBlackSquare": [1, 1, 1],
    "SmallBlackTriangle": [0, 1, 0],
    "BigWhiteTriangle": [1, 0, 0],
    "SmallWhiteTriangle": [0, 0, 0],
    "SmallWhiteSquare": [0, 0, 1],
    "SmallBlackSquare": [0, 1, 1],
    "BigWhiteSquare": [1, 0, 1],
    "BigBlackTriangle": [1, 1, 0],
}

FEATURE_NAMES_SPLIT = {
    "BigBlackSquare": "Big Black Square",
    "SmallBlackTriangle": "Small Black Triangle",
    "BigWhiteTriangle": "Big White Triangle",
    "SmallWhiteTriangle": "Small White Triangle",
    "SmallWhiteSquare": "Small White Square",
    "SmallBlackSquare": "Small Black Square",
    "BigWhiteSquare": "Big White Square",
    "BigBlackTriangle": "Big Black Triangle",
}


def _strip_ext(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(r"\.[^.]+$", "", regex=True)


def _map_object_and_features(filename_series: pd.Series):
    base = _strip_ext(filename_series)

    object_name = base.map(FEATURE_NAMES_SPLIT)
    if object_name.isna().any():
        missing = sorted(base[object_name.isna()].unique().tolist())
        raise KeyError(f"Unknown FileName base(s) not in FEATURE_NAMES_SPLIT: {missing[:10]}")

    feat = base.map(lambda k: FEATURES.get(k))
    if feat.isna().any():
        missing = sorted(base[feat.isna()].unique().tolist())
        raise KeyError(f"Unknown FileName base(s) not in FEATURES: {missing[:10]}")

    feature = np.array(feat.tolist(), dtype=int)
    all_features = [str(list(ff)) for ff in feature]
    feature1 = feature[:, 0]
    feature2 = feature[:, 1]
    feature3 = feature[:, 2]
    return object_name.to_numpy(), all_features, feature1, feature2, feature3


def main():
    trial_data = pd.read_csv(TRIAL_DATA_PATH)
    demographic_data = pd.read_csv(DEMOGRAPHIC_DATA_PATH)

    # Standardize trial columns
    trial_data = trial_data.rename(
        columns={
            "Slide1.RESP": "cond1_response",
            "Slide2.RESP": "cond2_response",
            "Slide3.RESP": "cond3_response",
            "Slide4.RESP": "cond4_response",
            "Slide1.CRESP": "correct_cond1_response",
            "Slide2.CRESP": "correct_cond2_response",
            "Slide3.CRESP": "correct_cond3_response",
            "Slide4.CRESP": "correct_cond4_response",
            "Slide1.ACC": "cond1_acc",
            "Slide2.ACC": "cond2_acc",
            "Slide3.ACC": "cond3_acc",
            "Slide4.ACC": "cond4_acc",
        }
    )

    # demographics lookup keyed by Participant
    demo = demographic_data.set_index("Participant")

    trial_data["age"] = trial_data["Subject"].map(demo["AGE"])
    trial_data["age_group"] = trial_data["Subject"].map(demo["AGE_Y1_O0"]).map({1: "young", 0: "older"})
    trial_data["sex"] = trial_data["Subject"].map(demo["SEX_M1_F0"]).map({1: "male", 0: "female"})

    # canonical subject_id
    subjects = sorted(pd.unique(trial_data["Subject"].dropna()))
    subject_id_map = {subj: i for i, subj in enumerate(subjects)}
    trial_data["subject_id"] = trial_data["Subject"].map(subject_id_map)

    print("Number of subjects (unique IDs):", len(subjects))

    num_blocks = 4

    # IMPORTANT: includes factor_structure_type
    out_cols = [
        "subject_id",
        "age",
        "age_group",
        "sex",
        "task",
        "trial",
        "choice",
        "correct_choice",
        "correct",
        "block",
        "factor_structure_type",
        "condition",
        "category",
        "object",
        "all_features",
        "feature1",
        "feature2",
        "feature3",
    ]

    rows = []

    for subj in subjects:
        subj_df = trial_data[trial_data["Subject"] == subj].copy()
        total_trials_until_previous_block = 0

        for block_number in range(1, num_blocks + 1):
            df = subj_df.query(f"Block == {block_number}").copy()
            if df.empty:
                continue

            cond_key = df["Running[Block]"].iloc[0]
            if cond_key not in CONDITIONS:
                raise KeyError(f"Unknown Running[Block]={cond_key!r} for Subject={subj} Block={block_number}")
            cond_number = CONDITIONS[cond_key]
            factor_structure_type = STRUCTURE_TYPE[cond_number]

            df = df.query(f'cond{cond_number}_response == "j" or cond{cond_number}_response == "f"').copy()
            if df.empty:
                continue

            response = df[f"cond{cond_number}_response"].to_numpy(copy=True)
            correct_response = df[f"correct_cond{cond_number}_response"].to_numpy(copy=True)
            correct = df[f"cond{cond_number}_acc"].astype(int).to_numpy(copy=True)

            trial_ids = np.arange(1, len(response) + 1) + total_trials_until_previous_block
            conditions = np.repeat(cond_number, len(response))
            blocks = np.repeat(block_number, len(response)) - 1

            object_name, all_features, feature1, feature2, feature3 = _map_object_and_features(df["FileName"])
            category = np.where(df["Alpha"] == "ALPHA", 0, 1)

            rows.append(
                pd.DataFrame(
                    {
                        "subject_id": np.repeat(df["subject_id"].iloc[0], len(response)),
                        "age": np.repeat(df["age"].iloc[0], len(response)),
                        "age_group": np.repeat(df["age_group"].iloc[0], len(response)),
                        "sex": np.repeat(df["sex"].iloc[0], len(response)),
                        "task": 0,
                        "block": blocks,
                        "factor_structure_type": np.repeat(factor_structure_type, len(response)),
                        "condition": conditions,
                        "trial": trial_ids - 1,
                        "category": category,
                        "correct": correct,
                        "choice": response,
                        "correct_choice": correct_response,
                        "object": object_name,
                        "all_features": all_features,
                        "feature1": feature1,
                        "feature2": feature2,
                        "feature3": feature3,
                    }
                )[out_cols]  # <- now includes factor_structure_type, so it won't be dropped
            )

            total_trials_until_previous_block = int(trial_ids[-1])

    if not rows:
        raise RuntimeError("No rows produced. Check input paths and column names.")

    out_df = pd.concat(rows, ignore_index=True)

    # Hard fail if something went wrong (prevents your exact error)
    missing = [c for c in out_cols if c not in out_df.columns]
    if missing:
        raise RuntimeError(f"Output is missing columns: {missing}")

    # show final columns for debugging
    print("Final columns:", out_df.columns.tolist())
    print("factor_structure_type levels:", sorted(out_df["factor_structure_type"].unique().tolist()))

    outpath = Path(__file__).resolve().parent / "exp1.csv"
    out_df.to_csv(outpath, index=False)
    print("Wrote:", outpath)


if __name__ == "__main__":
    main()
