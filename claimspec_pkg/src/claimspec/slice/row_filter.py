from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, ClassVar

import pandas as pd


@dataclass(frozen=True)
class RowFilter:
    kind: str

    # registry: kind -> subclass
    _REGISTRY: ClassVar[dict[str, type["RowFilter"]]] = {}

    def to_dict(self) -> dict:
        raise NotImplementedError

    def apply(self, df: pd.DataFrame, *, engine: str = "pandas") -> pd.DataFrame:
        """
        Return a filtered dataframe. Pandas-only for now.
        """
        if engine != "pandas":
            raise NotImplementedError(f"RowFilter engine not supported yet: {engine}")
        return self._apply_pandas(df)

    def _apply_pandas(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError(f"{type(self).__name__} must implement _apply_pandas")

    @classmethod
    def register(cls, subcls: type["RowFilter"]) -> type["RowFilter"]:
        cls._REGISTRY[subcls.kind] = subcls
        return subcls

    @classmethod
    def from_dict(cls, d: Optional[dict]) -> Optional["RowFilter"]:
        if d is None:
            return None
        kind = d.get("kind")
        subcls = cls._REGISTRY.get(kind)
        if subcls is None:
            raise ValueError(f"Unknown RowFilter kind: {kind}")
        return subcls.from_dict(d)


@RowFilter.register
@dataclass(frozen=True)
class Eq(RowFilter):
    """
    Convenience equality filter.
    Equivalent to Cmp(op="==", col=..., value=...).
    """
    kind: str = "eq"
    col: str = ""
    value: Any = None

    def to_dict(self) -> dict:
        return {"kind": self.kind, "col": self.col, "value": self.value}

    def _apply_pandas(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.col not in df.columns:
            raise KeyError(f"Eq.col '{self.col}' not in columns: {list(df.columns)}")
        return df[df[self.col] == self.value]

    @classmethod
    def from_dict(cls, d: dict) -> "Eq":
        return cls(col=d["col"], value=d.get("value"))


@RowFilter.register
@dataclass(frozen=True)
class Cmp(RowFilter):
    kind: str = "cmp"
    op: str = "=="
    col: str = ""
    value: Any = None

    def to_dict(self) -> dict:
        return {"kind": self.kind, "op": self.op, "col": self.col, "value": self.value}

    def _apply_pandas(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.col not in df.columns:
            raise KeyError(f"Cmp.col '{self.col}' not in columns: {list(df.columns)}")

        s = df[self.col]
        op = self.op

        if op == "==":
            mask = s == self.value
        elif op == "!=":
            mask = s != self.value
        elif op == "<":
            mask = s < self.value
        elif op == "<=":
            mask = s <= self.value
        elif op == ">":
            mask = s > self.value
        elif op == ">=":
            mask = s >= self.value
        elif op == "in":
            if not isinstance(self.value, (list, tuple, set)):
                raise TypeError(f'Cmp op="in" requires list/tuple/set; got {type(self.value)}')
            mask = s.isin(list(self.value))
        else:
            raise ValueError(f"Unknown Cmp.op: {op}")

        return df[mask]

    @classmethod
    def from_dict(cls, d: dict) -> "Cmp":
        # keep default "==" if older dicts omit op
        return cls(op=d.get("op", "=="), col=d["col"], value=d.get("value"))


@RowFilter.register
@dataclass(frozen=True)
class And(RowFilter):
    kind: str = "and"
    items: list[RowFilter] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.items is None:
            object.__setattr__(self, "items", [])

    def to_dict(self) -> dict:
        return {"kind": self.kind, "items": [x.to_dict() for x in self.items]}

    def _apply_pandas(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df
        for f in self.items:
            out = f.apply(out)
        return out

    @classmethod
    def from_dict(cls, d: dict) -> "And":
        items = [RowFilter.from_dict(x) for x in d.get("items", [])]
        return cls(items=items)  # type: ignore[arg-type]


@RowFilter.register
@dataclass(frozen=True)
class Or(RowFilter):
    kind: str = "or"
    items: list[RowFilter] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.items is None:
            object.__setattr__(self, "items", [])

    def to_dict(self) -> dict:
        return {"kind": self.kind, "items": [x.to_dict() for x in self.items]}

    def _apply_pandas(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.items:
            # OR of nothing -> empty selection (safer than "all rows")
            return df.iloc[0:0]

        # union by index
        mask = pd.Series(False, index=df.index)
        for f in self.items:
            sub = f.apply(df)
            mask |= df.index.isin(sub.index)
        return df[mask]

    @classmethod
    def from_dict(cls, d: dict) -> "Or":
        items = [RowFilter.from_dict(x) for x in d.get("items", [])]
        return cls(items=items)  # type: ignore[arg-type]


@RowFilter.register
@dataclass(frozen=True)
class Not(RowFilter):
    kind: str = "not"
    item: RowFilter = None  # type: ignore[assignment]

    def to_dict(self) -> dict:
        return {"kind": self.kind, "item": self.item.to_dict()}

    def _apply_pandas(self, df: pd.DataFrame) -> pd.DataFrame:
        sub = self.item.apply(df)
        # complement by index
        return df.loc[~df.index.isin(sub.index)]

    @classmethod
    def from_dict(cls, d: dict) -> "Not":
        item = RowFilter.from_dict(d["item"])
        if item is None:
            raise ValueError("Not.filter item must not be None")
        return cls(item=item)
