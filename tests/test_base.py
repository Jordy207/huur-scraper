from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx

from src.scrapers.base import BaseScraper


class BaseScraperTests(unittest.TestCase):
    def test_retries_transport_error(self) -> None:
        settings = SimpleNamespace(user_agent="test", request_timeout_seconds=20)
        scraper = BaseScraper(settings)
        response = Mock(status_code=200)

        with (
            patch("src.scrapers.base.BaseScraper.jitter_sleep"),
            patch("src.scrapers.base.time.sleep") as sleep,
            patch(
                "src.scrapers.base.httpx.request",
                side_effect=[httpx.TimeoutException("timed out"), response],
            ) as request,
        ):
            result = scraper.request_with_backoff(
                "GET", "https://example.test", max_retries=1
            )

        self.assertIs(result, response)
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(2)


if __name__ == "__main__":
    unittest.main()