from __future__ import annotations

import importlib.util
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

from claimspec.values.base import Value

# ----------------------------
# Config
# ----------------------------

PAPER_SLUGS = ["badham2017_deficits", "bahrami2020_four", "binz2022_heuristics", "cox2017_information",
               "desender2021_math"]

ROOT = Path(__file__).parent

# Datasets to compare (paper slug is appended inside the loop)
METHODS: Dict[str, Path] = {
    "gold_standard": ROOT / "methods" / "gold_standard" / "behavioral_data",
    "original_fair": ROOT / "methods" / "psych101" / "behavioral_data",
}

# ----------------------------
# Helpers
# ----------------------------

_EXP_RE = re.compile(r"^exp(\d+)\.csv$")


@dataclass(frozen=True)
class PaperPaths:
    paper_slug: str
    claims_path: Path
    gold_dir: Path
    datasets: Dict[str, Path]
    report_dir: Path
    per_claim_out: Path
    summary_exp_out: Path
    summary_all_out: Path


def _paths_for_paper(paper_slug: str) -> PaperPaths:
    claims_path = ROOT / "datasets" / "behavioral_data" / paper_slug / "claims.py"
    gold_dir = METHODS["gold_standard"] / paper_slug

    datasets = {
        "gold_standard": METHODS["gold_standard"] / paper_slug,
        "original_fair": METHODS["original_fair"] / paper_slug,
    }

    report_dir = ROOT / "reports" / "compare" / "behavioral_data" / paper_slug
    return PaperPaths(
        paper_slug=paper_slug,
        claims_path=claims_path,
        gold_dir=gold_dir,
        datasets=datasets,
        report_dir=report_dir,
        per_claim_out=report_dir / "per_claim.csv",
        summary_exp_out=report_dir / "summary_by_experiment.csv",
        summary_all_out=report_dir / "summary_overall.csv",
    )


def _import_claims(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing claims file: {path}")
    spec = importlib.util.spec_from_file_location(f"claims_{path.parent.name}", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _discover_experiments(gold_dir: Path) -> List[str]:
    """
    Discover experiments based on gold_standard exp*.csv presence.
    Returns ["exp1", "exp2", ...] sorted numerically.
    """
    if not gold_dir.exists():
        raise FileNotFoundError(f"Missing gold_standard dir: {gold_dir}")

    found: List[Tuple[int, str]] = []
    for p in gold_dir.glob("exp*.csv"):
        m = _EXP_RE.match(p.name)
        if not m:
            continue
        idx = int(m.group(1))
        found.append((idx, f"exp{idx}"))

    if not found:
        raise FileNotFoundError(f"No exp*.csv found in: {gold_dir}")

    found.sort(key=lambda t: t[0])
    return [s for _, s in found]


def _claims_for_experiment(mod: Any, exp: str, claims_path: Path) -> List[Any]:
    """
    Uses naming convention EXP1_CLAIMS, EXP2_CLAIMS, ...
    exp is "exp1" -> "EXP1_CLAIMS"
    """
    name = f"{exp.upper()}_CLAIMS"
    claims = getattr(mod, name, None)
    if claims is None:
        raise AttributeError(f"No {name} found in {claims_path}.")
    return list(claims)


def _is_invalid_value(v: Any) -> bool:
    return getattr(v, "kind", None) == "invalid" or v.__class__.__name__ == "InvalidValue"


def _spec_type(spec: Any) -> str:
    return spec.__class__.__name__


def _cmp_fields(cmp: Any) -> Tuple[bool, bool, Any, Any]:
    ok = bool(getattr(cmp, "ok", False))
    passed = bool(getattr(cmp, "passed", False))
    reason = getattr(cmp, "reason", None)
    detail = getattr(cmp, "detail", None)
    return ok, passed, reason, detail


def _csv_for(dataset_name: str, base_dir: Path, exp: str) -> Path:
    # If you later want different naming for original_fair, change it here.
    if dataset_name == "gold_standard":
        return base_dir / f"{exp}.csv"
    if dataset_name == "original_fair":
        return base_dir / f"{exp}.csv"
    raise ValueError(f"Unknown dataset_name: {dataset_name}")


def eval_dataset_for_exp(
        *,
        paper_slug: str,
        dataset_name: str,
        base_dir: Path,
        exp: str,
        claims: List[Any],
) -> pd.DataFrame:
    csv_path = _csv_for(dataset_name, base_dir, exp)
    if not csv_path.exists():
        raise FileNotFoundError(f"[{paper_slug} | {dataset_name}] Missing CSV for {exp}: {csv_path}")

    df = pd.read_csv(csv_path)

    rows: List[Dict[str, Any]] = []
    for i, claim in enumerate(claims):
        spec = claim.spec
        expected = claim.value

        row: Dict[str, Any] = {
            "paper": paper_slug,
            "experiment": exp,
            "dataset": dataset_name,
            "claim_index": i,
            "spec_type": _spec_type(spec),
            "spec_repr": repr(spec),
            "expected_repr": repr(expected),
            "observed_repr": "",
            "coverage_computable": False,
            "correctness_passed": False,
            "cmp_ok": False,
            "cmp_passed": False,
            "cmp_reason": None,
            "cmp_detail": "",
            "csv_path": str(csv_path),
        }

        try:
            observed = spec.apply(df)
            row["observed_repr"] = repr(observed)
        except Exception as e:
            row["cmp_reason"] = "spec_apply_exception"
            row["cmp_detail"] = json.dumps({"error": e.__class__.__name__, "message": str(e)})
            rows.append(row)
            continue

        try:
            cmp = Value.compare(expected, observed)
            ok, passed, reason, detail = _cmp_fields(cmp)
        except Exception as e:
            row["cmp_reason"] = "compare_exception"
            row["cmp_detail"] = json.dumps({"error": e.__class__.__name__, "message": str(e)})
            rows.append(row)
            continue

        row["cmp_ok"] = ok
        row["cmp_passed"] = passed
        row["cmp_reason"] = reason
        row["cmp_detail"] = json.dumps(detail, default=str) if detail is not None else ""

        row["coverage_computable"] = ok and not _is_invalid_value(observed)
        row["correctness_passed"] = ok and passed

        rows.append(row)

    return pd.DataFrame(rows)


def summarize(per_claim: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      - summary_by_experiment: (paper, experiment, dataset) rows
      - summary_overall: (paper, dataset) rows aggregated across experiments
    """

    def _agg(g: pd.DataFrame) -> Dict[str, Any]:
        n = len(g)
        cov_n = int(g["coverage_computable"].sum())
        pass_n = int(g["correctness_passed"].sum())
        ok_n = int(g["cmp_ok"].sum())
        return {
            "n_claims": n,
            "coverage_computable_n": cov_n,
            "coverage_computable_rate": cov_n / n if n else 0.0,
            "correctness_pass_n": pass_n,
            "correctness_pass_rate": pass_n / n if n else 0.0,
            "compare_ok_n": ok_n,
            "compare_ok_rate": ok_n / n if n else 0.0,
        }

    by_exp = []
    for (paper, exp, ds), g in per_claim.groupby(["paper", "experiment", "dataset"], dropna=False):
        by_exp.append({"paper": paper, "experiment": exp, "dataset": ds, **_agg(g)})

    by_exp_df = pd.DataFrame(by_exp).sort_values(["paper", "experiment", "dataset"])

    overall = []
    for (paper, ds), g in per_claim.groupby(["paper", "dataset"], dropna=False):
        overall.append({"paper": paper, "dataset": ds, **_agg(g)})

    overall_df = pd.DataFrame(overall).sort_values(["paper", "dataset"])

    return by_exp_df, overall_df


# ----------------------------
# Main
# ----------------------------

def run_one_paper(paper_slug: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = _paths_for_paper(paper_slug)
    paths.report_dir.mkdir(parents=True, exist_ok=True)

    mod = _import_claims(paths.claims_path)
    exp_list = _discover_experiments(paths.gold_dir)

    all_frames: List[pd.DataFrame] = []
    for exp in exp_list:
        claims = _claims_for_experiment(mod, exp, paths.claims_path)

        for ds_name, base_dir in paths.datasets.items():
            all_frames.append(
                eval_dataset_for_exp(
                    paper_slug=paper_slug,
                    dataset_name=ds_name,
                    base_dir=base_dir,
                    exp=exp,
                    claims=claims,
                )
            )

    per_claim = pd.concat(all_frames, ignore_index=True)
    by_exp, overall = summarize(per_claim)

    per_claim.to_csv(paths.per_claim_out, index=False)
    by_exp.to_csv(paths.summary_exp_out, index=False)
    overall.to_csv(paths.summary_all_out, index=False)

    print(f"\n=== {paper_slug} ===")
    print("Wrote:")
    print(" ", paths.per_claim_out)
    print(" ", paths.summary_exp_out)
    print(" ", paths.summary_all_out)
    print("\nOverall:")
    print(overall.to_string(index=False))

    return per_claim, by_exp, overall


def main() -> None:
    all_per_claim: List[pd.DataFrame] = []
    all_by_exp: List[pd.DataFrame] = []
    all_overall: List[pd.DataFrame] = []

    for paper_slug in PAPER_SLUGS:
        per_claim, by_exp, overall = run_one_paper(paper_slug)
        all_per_claim.append(per_claim)
        all_by_exp.append(by_exp)
        all_overall.append(overall)

    # Optional: combined outputs across all papers
    combined_dir = ROOT / "reports" / "compare" / "behavioral_data" / "_all"
    combined_dir.mkdir(parents=True, exist_ok=True)

    per_claim_all = pd.concat(all_per_claim, ignore_index=True)
    by_exp_all = pd.concat(all_by_exp, ignore_index=True).sort_values(["paper", "experiment", "dataset"])
    overall_all = pd.concat(all_overall, ignore_index=True).sort_values(["paper", "dataset"])

    per_claim_all.to_csv(combined_dir / "per_claim.csv", index=False)
    by_exp_all.to_csv(combined_dir / "summary_by_experiment.csv", index=False)
    overall_all.to_csv(combined_dir / "summary_overall.csv", index=False)

    print("\n=== Combined (_all) ===")
    print("Wrote:")
    print(" ", combined_dir / "per_claim.csv")
    print(" ", combined_dir / "summary_by_experiment.csv")
    print(" ", combined_dir / "summary_overall.csv")


if __name__ == "__main__":
    main()
