from __future__ import annotations

from dataclasses import dataclass
import re

from src.config import Settings
from src.models.listing import Listing


@dataclass(frozen=True)
class MatchResult:
    is_hard_match: bool
    is_close_match: bool
    score: int
    reasons: list[str]


def _normalize_city_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def normalize_city_name(value: str | None) -> str | None:
    if not value:
        return None

    token = _normalize_city_token(value)
    aliases = {
        "denhaag": "denhaag",
        "sgravenhage": "denhaag",
        "gravenhage": "denhaag",
        "thehague": "denhaag",
        "rijswijk": "rijswijk",
        "rijswijkzh": "rijswijk",
        "delft": "delft",
        "voorburg": "voorburg",
        "leidschendam": "leidschendam",
        "nootdorp": "nootdorp",
        "ypenburg": "ypenburg",
    }
    return aliases.get(token, token)


def evaluate_listing(listing: Listing, settings: Settings) -> MatchResult:
    reasons: list[str] = []
    score = 0

    allowed_city_keys = {
        normalized
        for normalized in (normalize_city_name(city) for city in settings.allowed_cities)
        if normalized
    }
    listing_city_key = normalize_city_name(listing.city)

    hard_price = listing.rent_price is not None and listing.rent_price <= settings.max_rent_eur
    hard_area = listing.living_area_m2 is not None and listing.living_area_m2 >= settings.min_size_m2
    hard_city = listing_city_key is not None and listing_city_key in allowed_city_keys
    hard_availability = listing.is_available

    if hard_price:
        score += 40
        reasons.append("price_ok")
    if hard_area:
        score += 30
        reasons.append("size_ok")
    if hard_city:
        score += 20
        reasons.append("city_ok")
    if hard_availability:
        score += 5
        reasons.append("available")

    preferred_bedrooms = listing.bedrooms is not None and listing.bedrooms >= settings.preferred_bedrooms
    if preferred_bedrooms:
        score += 10
        reasons.append("preferred_bedrooms")

    is_hard_match = hard_price and hard_area and hard_city and hard_availability

    relaxed_price = listing.rent_price is not None and listing.rent_price <= int(settings.max_rent_eur * 1.1)
    relaxed_area = listing.living_area_m2 is not None and listing.living_area_m2 >= int(settings.min_size_m2 * 0.9)
    close_city = listing_city_key is not None and listing_city_key in allowed_city_keys
    # Close match still requires both dimensions to stay near profile bounds.
    is_close_match = (
        settings.allow_close_match
        and hard_availability
        and close_city
        and relaxed_price
        and relaxed_area
    )

    return MatchResult(
        is_hard_match=is_hard_match,
        is_close_match=is_close_match and not is_hard_match,
        score=score,
        reasons=reasons,
    )
