from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Type, Dict, Iterable, Tuple, Union

import pandas as pd

from claimspec.values.base import Value, InvalidValue
from claimspec.slice.data_slice import DataSlice
from claimspec.utils.fingerprint import fingerprint_dict


GroupKey = str
SpecResult = Union[Value, Dict[GroupKey, Value]]


@dataclass(frozen=True)
class Spec:
    kind: ClassVar[str]
    value_cls: ClassVar[Type[Value]]

    slice: Optional[DataSlice] = None

    _REGISTRY: ClassVar[Dict[str, Type["Spec"]]] = {}

    def to_dict(self) -> dict:
        raise NotImplementedError

    def key(self) -> str:
        return fingerprint_dict(self.to_dict())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Spec):
            return NotImplemented
        return self.key() == other.key()

    def __hash__(self) -> int:
        # because we override __eq__ in a frozen dataclass
        return hash(self.key())

    @classmethod
    def register(cls, subcls: Type["Spec"]) -> Type["Spec"]:
        cls._REGISTRY[subcls.kind] = subcls
        return subcls

    @classmethod
    def from_dict(cls, d: dict) -> "Spec":
        kind = d.get("kind")
        subcls = cls._REGISTRY.get(kind)
        if subcls is None:
            raise ValueError(f"Unknown Spec kind: {kind}")
        return subcls.from_dict(d)

    # ----------------------------
    # Execution (pandas-only for now)
    # ----------------------------

    def apply(self, df: pd.DataFrame, *, engine: str = "pandas") -> SpecResult:
        if engine != "pandas":
            return InvalidValue(
                reason="unsupported_engine",
                detail={"engine": engine, "supported": ["pandas"]},
            )

        df2 = self._apply_slice_pandas(df)

        # If slicing failed, bubble up InvalidValue
        if isinstance(df2, InvalidValue):
            return df2

        groups = list(self._iter_groups_pandas(df2))
        if len(groups) == 1 and groups[0][0] == "__all__":
            # no grouping
            return self.compute(groups[0][1], engine="pandas")

        out: Dict[GroupKey, Value] = {}
        for gk, gdf in groups:
            out[gk] = self.compute(gdf, engine="pandas")
        return out

    def compute(self, df: pd.DataFrame, *, engine: str = "pandas") -> Value:
        """
        Engine-dispatch wrapper. Subclasses should override _compute_pandas.
        """
        if engine == "pandas":
            return self._compute_pandas(df)
        raise NotImplementedError(f"Spec engine not supported yet: {engine}")

    def _compute_pandas(self, df: pd.DataFrame) -> Value:
        """
        Subclasses override this with their core pandas implementation.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not implement _compute_pandas"
        )

    # ----------------------------
    # Helpers
    # ----------------------------

    def _apply_slice_pandas(self, df: pd.DataFrame) -> Union[pd.DataFrame, InvalidValue]:
        df2 = df

        # 1) row filter
        if self.slice is not None and self.slice.row_filter is not None:
            try:
                df2 = self.slice.row_filter.apply(df2, engine="pandas")
            except Exception as e:
                return InvalidValue(
                    reason="row_filter_failed",
                    detail={"error": type(e).__name__, "message": str(e)},
                )

        # 2) aggregates (unit-of-analysis transformations)
        if self.slice is not None and self.slice.aggregates:
            for agg in self.slice.aggregates:
                try:
                    df2 = agg.apply(df2)
                except Exception as e:
                    return InvalidValue(
                        reason="aggregate_failed",
                        detail={"error": type(e).__name__, "message": str(e)},
                    )

                if isinstance(df2, InvalidValue):
                    return df2

        return df2


    def _iter_groups_pandas(self, df: pd.DataFrame) -> Iterable[Tuple[GroupKey, pd.DataFrame]]:
        if self.slice is None or not self.slice.group_by:
            yield ("__all__", df)
            return

        gb = self.slice.group_by
        for col in gb:
            if col not in df.columns:
                # If you prefer hard failure, replace with: raise KeyError(...)
                yield (
                    "__invalid__",
                    df.iloc[0:0],  # empty df
                )
                return

        grouped = df.groupby(gb, dropna=False, sort=False)
        for key, gdf in grouped:
            yield (self._format_group_key(key), gdf)

    @staticmethod
    def _format_group_key(key: Any) -> str:
        if isinstance(key, tuple):
            return "|".join(str(x) for x in key)
        return str(key)
