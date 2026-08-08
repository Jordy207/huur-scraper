from __future__ import annotations

from bs4 import BeautifulSoup

from src.models.listing import Listing
from src.scrapers.base import BaseScraper


class NRWonenScraper(BaseScraper):
    source_name = "nrw_wonen"
    start_url = "https://www.nrw-wonen.nl/huur-aanbod"

    def search(self, max_retries: int = 2) -> list[Listing]:
        result = self.fetch_with_backoff(self.start_url, max_retries=max_retries)
        soup = BeautifulSoup(result.text, "html.parser")
        listings: list[Listing] = []

        for link in soup.select("a[href*='/huur-aanbod/']"):
            href = (link.get("href") or "").strip()
            if not href or href.endswith("/huur-aanbod"):
                continue

            title = " ".join(link.get_text(" ", strip=True).split())
            if len(title) < 4:
                continue

            url = href if href.startswith("http") else f"https://www.nrw-wonen.nl{href}"
            listing_id = url.rstrip("/").split("/")[-1]

            listings.append(
                Listing(
                    source_site=self.source_name,
                    source_listing_id=listing_id,
                    source_url=url,
                    title=title,
                    city="Den Haag" if "haag" in title.lower() else None,
                    rent_price=self.parse_int(title),
                    living_area_m2=None,
                    rooms_total=None,
                    bedrooms=None,
                    available_from=None,
                    raw_features={"selector": "a[href*='/huur-aanbod/']"},
                )
            )

        unique: dict[str, Listing] = {item.source_listing_id: item for item in listings}
        return list(unique.values())
