from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SourceMode(str, Enum):
    SCRAPE = "SCRAPE"
    ALERT_INGEST = "ALERT_INGEST"
    DISABLED = "DISABLED"


@dataclass(frozen=True)
class SourcePolicy:
    name: str
    mode: SourceMode
    min_interval_seconds: int
    max_retries: int
    auto_disable_on_block: bool


def is_collection_allowed(policy: SourcePolicy) -> bool:
    return policy.mode == SourceMode.SCRAPE
