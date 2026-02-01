from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List

from claimspec.slice.row_filter import RowFilter
from claimspec.slice.aggregate import Aggregate


@dataclass(frozen=True)
class DataSlice:
    row_filter: Optional[RowFilter] = None
    aggregates: Optional[List[Aggregate]] = None
    group_by: Optional[list[str]] = None

    def __post_init__(self) -> None:
        gb = self.group_by
        if gb is not None:
            if isinstance(gb, str):
                gb = [gb]
            gb = sorted(set(gb))
            object.__setattr__(self, "group_by", gb)

        aggs = self.aggregates
        if aggs is not None:
            object.__setattr__(self, "aggregates", list(aggs))

    def to_dict(self) -> dict:
        return {
            "row_filter": None if self.row_filter is None else self.row_filter.to_dict(),
            "aggregates": None if self.aggregates is None else [a.to_dict() for a in self.aggregates],
            "group_by": self.group_by,
        }

    @classmethod
    def from_dict(cls, d: Optional[dict]) -> Optional["DataSlice"]:
        if d is None:
            return None
        return cls(
            row_filter=RowFilter.from_dict(d.get("row_filter")),
            aggregates=[Aggregate.from_dict(a) for a in d.get("aggregates") or []] or None,
            group_by=d.get("group_by"),
        )
