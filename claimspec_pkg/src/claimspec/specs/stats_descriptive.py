from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Type

import pandas as pd

from claimspec.specs.base import Spec
from claimspec.slice.data_slice import DataSlice
from claimspec.values.base import Value, InvalidValue
from claimspec.values.number import NumberValue


@Spec.register
@dataclass(frozen=True)
class Mean(Spec):
    """
    Mean of a numeric column, optionally within a DataSlice.
    """
    kind: ClassVar[str] = "mean"
    value_cls: ClassVar[Type[Value]] = NumberValue

    col: str = ""

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "col": self.col,
            "slice": None if self.slice is None else self.slice.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Mean":
        return cls(
            col=d["col"],
            slice=DataSlice.from_dict(d.get("slice")),
        )

    def _compute_pandas(self, df: pd.DataFrame) -> Value:
        if self.col not in df.columns:
            return InvalidValue(
                reason="missing_column",
                detail={"col": self.col, "columns": list(df.columns)},
            )

        s = pd.to_numeric(df[self.col], errors="coerce").dropna()
        if s.empty:
            return InvalidValue(
                reason="no_data",
                detail={"col": self.col, "n_rows": len(df)},
            )

        return NumberValue(data=float(s.mean()))


@Spec.register
@dataclass(frozen=True)
class Std(Spec):
    """
    Sample standard deviation of a numeric column (ddof=1).
    """
    kind: ClassVar[str] = "std"
    value_cls: ClassVar[Type[Value]] = NumberValue

    col: str = ""

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "col": self.col,
            "slice": None if self.slice is None else self.slice.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Std":
        return cls(
            col=d["col"],
            slice=DataSlice.from_dict(d.get("slice")),
        )

    def _compute_pandas(self, df: pd.DataFrame) -> Value:
        if self.col not in df.columns:
            return InvalidValue(
                reason="missing_column",
                detail={"col": self.col, "columns": list(df.columns)},
            )

        s = pd.to_numeric(df[self.col], errors="coerce").dropna()
        if len(s) < 2:
            return InvalidValue(
                reason="not_enough_data",
                detail={"col": self.col, "n_rows": len(s)},
            )

        return NumberValue(data=float(s.std(ddof=1)))
