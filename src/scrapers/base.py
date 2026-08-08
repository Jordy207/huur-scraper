from __future__ import annotations

import logging
import random
import re
import time
from dataclasses import dataclass

import httpx

from src.config import Settings
from src.models.listing import Listing


_BLOCK_STATUSES = {403, 429}
logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    url: str
    status_code: int
    text: str


class SourceBlockedError(Exception):
    pass


class BaseScraper:
    source_name: str = "base"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def search(self) -> list[Listing]:
        raise NotImplementedError

    def fetch_with_backoff(self, url: str, max_retries: int = 2) -> FetchResult:
        headers = {"User-Agent": self.settings.user_agent}
        timeout = self.settings.request_timeout_seconds
        base_wait = 2

        for attempt in range(max_retries + 1):
            self.jitter_sleep(0.8, 1.8)
            logger.info(
                "Fetching source=%s url=%s attempt=%d/%d",
                self.source_name,
                url,
                attempt + 1,
                max_retries + 1,
            )
            response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
            logger.info(
                "Response source=%s status=%s url=%s",
                self.source_name,
                response.status_code,
                url,
            )

            if response.status_code in _BLOCK_STATUSES:
                if attempt >= max_retries:
                    raise SourceBlockedError(f"Blocked with status {response.status_code} for {self.source_name}")
                wait_seconds = base_wait * (attempt + 1)
                logger.warning(
                    "Blocked response source=%s status=%s; backing off for %ss",
                    self.source_name,
                    response.status_code,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
                continue

            if response.status_code >= 500 and attempt < max_retries:
                wait_seconds = base_wait * (attempt + 1)
                logger.warning(
                    "Server error source=%s status=%s; retrying in %ss",
                    self.source_name,
                    response.status_code,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
                continue

            return FetchResult(url=url, status_code=response.status_code, text=response.text)

        raise RuntimeError(f"Failed to fetch {url}")

    @staticmethod
    def jitter_sleep(min_seconds: float, max_seconds: float) -> None:
        time.sleep(random.uniform(min_seconds, max_seconds))

    @staticmethod
    def parse_int(value: str | None) -> int | None:
        if not value:
            return None
        cleaned = re.sub(r"[^0-9]", "", value)
        if not cleaned:
            return None
        return int(cleaned)
