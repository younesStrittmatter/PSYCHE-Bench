# root/run.py
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

from claimspec.values.base import Value

PAPER_SLUG = "desender2021_math"
EXPERIMENT = "exp1"

ROOT = Path(__file__).parent

CLAIMS_PATH = ROOT / "datasets" / "behavioral_data" / PAPER_SLUG / "claims.py"
CSV_PATH = ROOT / "methods" / "gold_standard" / "behavioral_data" / PAPER_SLUG / f"{EXPERIMENT}.csv"


def main() -> None:
    spec = importlib.util.spec_from_file_location("claims_module", CLAIMS_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)

    claims = mod.EXP1_CLAIMS
    df = pd.read_csv(CSV_PATH)

    failures = 0
    for claim in claims:
        observed = claim.spec.apply(df)
        cmp = Value.compare(claim.value, observed)
        if not cmp.ok or not cmp.passed:
            failures += 1
            print("FAIL")
            print(" spec:", claim.spec)
            print(" expected:", claim.value)
            print(" observed:", observed)
            print(" compare:", cmp)

    if failures:
        raise SystemExit(f"{failures} claim(s) failed.")
    print("OK")


if __name__ == "__main__":
    main()
