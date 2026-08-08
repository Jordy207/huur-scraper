from __future__ import annotations

from dataclasses import dataclass

from src.config import Settings
from src.models.listing import Listing


@dataclass(frozen=True)
class MatchResult:
    is_hard_match: bool
    is_close_match: bool
    score: int
    reasons: list[str]


def evaluate_listing(listing: Listing, settings: Settings) -> MatchResult:
    reasons: list[str] = []
    score = 0

    hard_price = listing.rent_price is not None and listing.rent_price <= settings.max_rent_eur
    hard_area = listing.living_area_m2 is not None and listing.living_area_m2 >= settings.min_size_m2
    hard_city = listing.city is not None and listing.city in settings.allowed_cities

    if hard_price:
        score += 40
        reasons.append("price_ok")
    if hard_area:
        score += 30
        reasons.append("size_ok")
    if hard_city:
        score += 20
        reasons.append("city_ok")

    preferred_bedrooms = listing.bedrooms is not None and listing.bedrooms >= settings.preferred_bedrooms
    if preferred_bedrooms:
        score += 10
        reasons.append("preferred_bedrooms")

    is_hard_match = hard_price and hard_area and hard_city

    relaxed_price = listing.rent_price is not None and listing.rent_price <= int(settings.max_rent_eur * 1.1)
    relaxed_area = listing.living_area_m2 is not None and listing.living_area_m2 >= int(settings.min_size_m2 * 0.9)
    close_city = listing.city is not None and listing.city in settings.allowed_cities
    is_close_match = settings.allow_close_match and close_city and (relaxed_price or relaxed_area)

    return MatchResult(
        is_hard_match=is_hard_match,
        is_close_match=is_close_match and not is_hard_match,
        score=score,
        reasons=reasons,
    )
