from __future__ import annotations

from claimspec.claims.claim import Claim
from claimspec.specs.count_unique import CountUnique
from claimspec.slice.data_slice import DataSlice
from claimspec.values.number import NumberValue
from datasets.behavioral_data.standard import DATASET_CONVENTION


EXP1_CLAIMS = [
    Claim(
        spec=CountUnique(
            col=DATASET_CONVENTION.subject_id
        ),
        value=NumberValue(462),
    ),
]
