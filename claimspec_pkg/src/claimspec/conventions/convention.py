from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Any

columns: Sequence[ColumnSpec] = ()


# -------------------------
# Column specs
# -------------------------

@dataclass(frozen=True)
class ColumnSpec:
    """
    Documentation for a column used in a Convention (global or paper-local).
    """
    name: str
    description: str

    @property
    def kind(self) -> str:
        return "unknown"

    def to_dict(self) -> dict:
        return {"name": self.name, "description": self.description, "kind": self.kind}

    @classmethod
    def from_dict(cls, d: dict) -> "ColumnSpec":
        kind = d.get("kind", "unknown")
        if kind == "categorical":
            return ColumnSpecCategorical.from_dict(d)
        return cls(name=d["name"], description=d["description"])


@dataclass(frozen=True)
class ColumnSpecCategorical(ColumnSpec):
    """
    Categorical column, optionally with explicit allowed levels.
    """
    levels: Sequence[Any] = ()

    @property
    def kind(self) -> str:
        return "categorical"

    def to_dict(self) -> dict:
        out = super().to_dict()
        out["levels"] = list(self.levels) if self.levels else None
        return out

    @classmethod
    def from_dict(cls, d: dict) -> "ColumnSpecCategorical":
        lv = d.get("levels") or []
        return cls(name=d["name"], description=d["description"], levels=lv)

    def level(self, x: str) -> str:
        """
        Validate a categorical level if levels are explicitly defined.
        If levels are not defined, allow any value (open categorical).
        """
        if not self.levels:
            return x
        if x not in self.levels:
            raise ValueError(
                f"Invalid level {x!r} for column {self.name!r}. Allowed: {list(self.levels)}"
            )
        return x


# -------------------------
# Syntactic sugar: CONV.age_group.young
# -------------------------

class _ColumnRef(str):
    """
    String subclass representing a column key, with optional categorical level access.

    Examples:
        conv.age_group          -> "age_group"  (usable wherever a str is expected)
        conv.age_group.young    -> "young"      (validated if levels are defined)
    """

    def __new__(cls, name: str, spec: ColumnSpec):
        obj = str.__new__(cls, name)
        obj._spec = spec
        return obj

    def __getattr__(self, item: str) -> str:
        if isinstance(self._spec, ColumnSpecCategorical):
            return self._spec.level(item)
        raise AttributeError(
            f"Column {str(self)!r} is not categorical (kind={self._spec.kind!r})."
        )


# -------------------------
# Convention (shared)
# -------------------------

@dataclass(frozen=True)
class Convention:
    """
    A named set of column specs. Use for both global standards and paper-local conventions.
    """
    name: str
    version: str = "0"
    columns: Sequence[ColumnSpec] = ()
    notes: Sequence[str] = ()

    def __getattr__(self, item: str) -> _ColumnRef:
        """
        Allow CONV.subject_id to resolve to a string-like column ref.
        """
        col = self.get_column(item)
        if col is not None:
            return _ColumnRef(item, col)
        raise AttributeError(
            f"{type(self).__name__} has no column '{item}'. "
            f"Known: {[c.name for c in self.columns]}"
        )

    def get_column(self, name: str) -> Optional[ColumnSpec]:
        for c in self.columns:
            if c.name == name:
                return c
        return None

    # tiny sugar for claims (only categorical for now)
    def cat(self, col: str, level: str) -> str:
        c = self.get_column(col)
        if isinstance(c, ColumnSpecCategorical):
            return c.level(level)
        return level

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "columns": [c.to_dict() for c in self.columns],
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Convention":
        cols = tuple(ColumnSpec.from_dict(x) for x in d.get("columns", []))
        notes = tuple(d.get("notes", []) or [])
        return cls(
            name=d["name"],
            version=str(d.get("version", "0")),
            columns=cols,
            notes=notes,
        )
