from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Dict, Optional, Type, List

import pandas as pd

from claimspec.values.base import InvalidValue


@dataclass(frozen=True)
class Aggregate:
    kind: ClassVar[str]
    _REGISTRY: ClassVar[Dict[str, Type["Aggregate"]]] = {}

    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def register(cls, subcls: Type["Aggregate"]) -> Type["Aggregate"]:
        cls._REGISTRY[subcls.kind] = subcls
        return subcls

    @classmethod
    def from_dict(cls, d: Optional[dict]) -> Optional["Aggregate"]:
        if d is None:
            return None
        kind = d.get("kind")
        subcls = cls._REGISTRY.get(kind)
        if subcls is None:
            raise ValueError(f"Unknown Aggregate kind: {kind}")
        return subcls.from_dict(d)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame | InvalidValue:
        raise NotImplementedError


@Aggregate.register
@dataclass(frozen=True)
class Const(Aggregate):
    kind: ClassVar[str] = "const"

    by: List[str]  # unit-of-analysis keys (e.g., subject_id)
    cols: List[str]  # columns that must be constant within unit

    def to_dict(self) -> dict:
        return {"kind": self.kind, "by": self.by, "cols": self.cols}

    @classmethod
    def from_dict(cls, d: dict) -> "Const":
        return cls(by=list(d["by"]), cols=list(d["cols"]))

    def apply(self, df: pd.DataFrame) -> pd.DataFrame | InvalidValue:
        missing = [c for c in self.by + self.cols if c not in df.columns]
        if missing:
            return InvalidValue(reason="missing_column", detail={"cols": missing})

        g = df.groupby(self.by, dropna=False, sort=False)

        for c in self.cols:
            nun = g[c].nunique(dropna=True)
            bad = nun[nun > 1]
            if not bad.empty:
                return InvalidValue(
                    reason="non_constant_within_unit",
                    detail={"col": c, "examples": bad.head(5).to_dict()},
                )

        # reduce to one row per unit, keeping constant cols
        keep_cols = list(dict.fromkeys(self.by + self.cols))
        return df[keep_cols].drop_duplicates(subset=self.by, keep="first")

@Aggregate.register
@dataclass(frozen=True)
class MeanAgg(Aggregate):
    """
    Reduce df to one row per unit (by=...), replacing each col in `cols`
    with its mean within the unit.

    Use this to compute mean-of-subject-means:
        aggregates=[MeanAgg(by=["subject_id"], cols=["correct"])]
    then a Spec Mean(col="correct") will compute the mean across subjects.
    """
    kind: ClassVar[str] = "mean_agg"

    by: List[str]
    cols: List[str]

    def to_dict(self) -> dict:
        return {"kind": self.kind, "by": list(self.by), "cols": list(self.cols)}

    @classmethod
    def from_dict(cls, d: dict) -> "MeanAgg":
        return cls(by=list(d["by"]), cols=list(d["cols"]))

    def apply(self, df: pd.DataFrame) -> pd.DataFrame | InvalidValue:
        missing = [c for c in self.by + self.cols if c not in df.columns]
        if missing:
            return InvalidValue(reason="missing_column", detail={"cols": missing})

        bad_cols = [c for c in self.cols if not pd.api.types.is_numeric_dtype(df[c])]
        if bad_cols:
            return InvalidValue(
                reason="non_numeric_aggregate_col",
                detail={"cols": bad_cols, "dtypes": {c: str(df[c].dtype) for c in bad_cols}},
            )

        out = (
            df.groupby(self.by, dropna=False, sort=False)[self.cols]
              .mean()
              .reset_index()
        )

        # stable column order: by then cols
        out_cols = list(dict.fromkeys(self.by + self.cols))
        return out[out_cols]
