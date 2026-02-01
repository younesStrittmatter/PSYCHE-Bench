from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint_dict(d: dict) -> str:
    """
    Helper for stable hashing of dict representations.
    """
    s = stable_json(d)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
