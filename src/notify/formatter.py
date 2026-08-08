from __future__ import annotations

from src.filtering.rules import MatchResult
from src.models.listing import Listing


def format_listing_message(listing: Listing, result: MatchResult) -> str:
    match_type = "HARD_MATCH" if result.is_hard_match else "CLOSE_MATCH"
    price = f"€{listing.rent_price}" if listing.rent_price is not None else "n/a"
    area = f"{listing.living_area_m2} m²" if listing.living_area_m2 is not None else "n/a"
    bedrooms = str(listing.bedrooms) if listing.bedrooms is not None else "n/a"
    city = listing.city or "n/a"

    return (
        f"[{match_type}] {listing.title}\n"
        f"Site: {listing.source_site}\n"
        f"City: {city}\n"
        f"Price: {price}\n"
        f"Area: {area}\n"
        f"Bedrooms: {bedrooms}\n"
        f"Score: {result.score}\n"
        f"URL: {listing.source_url}"
    )
