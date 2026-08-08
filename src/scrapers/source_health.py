from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SourceHealthState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


@dataclass
class SourceHealth:
    state: SourceHealthState = SourceHealthState.HEALTHY
    consecutive_blocks: int = 0


class SourceHealthTracker:
    def __init__(self, block_threshold: int = 2) -> None:
        self.block_threshold = block_threshold
        self._health: dict[str, SourceHealth] = {}

    def _entry(self, source_name: str) -> SourceHealth:
        if source_name not in self._health:
            self._health[source_name] = SourceHealth()
        return self._health[source_name]

    def mark_success(self, source_name: str) -> None:
        entry = self._entry(source_name)
        entry.consecutive_blocks = 0
        entry.state = SourceHealthState.HEALTHY

    def mark_block(self, source_name: str) -> SourceHealthState:
        entry = self._entry(source_name)
        entry.consecutive_blocks += 1
        if entry.consecutive_blocks >= self.block_threshold:
            entry.state = SourceHealthState.BLOCKED
        else:
            entry.state = SourceHealthState.DEGRADED
        return entry.state

    def get_state(self, source_name: str) -> SourceHealthState:
        return self._entry(source_name).state
