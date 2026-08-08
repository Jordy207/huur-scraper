from __future__ import annotations

from src.models.listing import Listing
from src.scrapers.base import BaseScraper


class WobecoScraper(BaseScraper):
    source_name = "wobeco"
    api_url = "https://www.wobeco.com/rts/collections/public/c90a4b31/runtime/collection/EAZLEE/query-data?pageSize=10&pageNumber=0&query=%28filters%3A%21%28%28field%3Adivision%2Coperator%3Aeq%2Cvalue%3Aproperty%29%2C%28field%3Atmp_label%2Coperator%3ANIN%2Cvalue%3A%21%28%27*%27%29%29%2C%28field%3Atmp_forrent%2Coperator%3AEQ%2Cvalue%3A%271%27%29%2C%28field%3Atmp_city%2Coperator%3ANE%2Cvalue%3A%27*%27%29%2C%28field%3Atmp_streetAddress%2Coperator%3ANE%2Cvalue%3A%27*%27%29%2C%28field%3Atmp_property_type_1%2Coperator%3AEQ%2Cvalue%3AAppartement%29%2C%28field%3Atmp_property_type_2%2Coperator%3ANE%2Cvalue%3A%27*%27%29%2C%28field%3Atmp_property_type_3%2Coperator%3ANE%2Cvalue%3A%27*%27%29%2C%28field%3Atmp_num_bedrooms%2Coperator%3AGTE%2Cvalue%3A%271%27%29%2C%28field%3Atmp_interior%2Coperator%3ANE%2Cvalue%3A%27*%27%29%2C%28field%3Atmp_surface%2Coperator%3AGTE%2Cvalue%3A%2740%27%29%2C%28field%3Atmp_price%2Coperator%3AGTE%2Cvalue%3A%270%27%29%2C%28field%3Atmp_price%2Coperator%3ALTE%2Cvalue%3A%271150%27%29%2C%28field%3Apo-api%2Coperator%3ANE%2Cvalue%3A%27*%27%29%29%2CsortBy%3A%21%28%28direction%3Aasc%2Cfield%3Aranking%29%29%29&language=DUTCH"

    def search(self, max_retries: int = 2) -> list[Listing]:
        payload = self.fetch_json(self.api_url, max_retries=max_retries)["values"]
        if not isinstance(payload, list):
            return []

        listings: list[Listing] = []

        for item in payload:
            item = item.get("data")
            if not isinstance(item, dict):
                continue

            listing_id_raw = item.get("id")
            if listing_id_raw is None:
                continue

            listing_id = str(listing_id_raw)
            url = "https://www.wobeco.com/woning/" + item.get("page_item_url", "")

            title = item.get("street-zip-city") or f"Wobeco listing {listing_id}"
            city = item.get("city")
            city = city.strip() if isinstance(city, str) else None

            status = item.get("forrent")
            listing_status = "available" if status else "unavailable"
            is_available = self.map_status_to_available(status, default=False)

       
            available_from = None

            raw_features = {
                "status": status if isinstance(status, str) else "",
                "postal_code": str(item.get("locality", {}).get("zipcode", "")),
                "street": str(item.get("locality", {}).get("street", "")),
                "house_number": f"{item.get('locality', {}).get('number', '')}{item.get('locality', {}).get('addition', '')}",
                "asset_type": str(item.get("property_type_1") or ""),
                "furniture": str(item.get("interior") or ""),
            }

            rent_price = item.get("price")
            if not isinstance(rent_price, int):
                rent_price = self.parse_int(str(rent_price) if rent_price is not None else None)

            living_area = item.get("surface")
            if not isinstance(living_area, int):
                living_area = self.parse_int(str(living_area) if living_area is not None else None)

            total_rooms = item.get("counts", {}).get("total_rooms")
            if not isinstance(total_rooms, int):
                total_rooms = self.parse_int(str(total_rooms) if total_rooms is not None else None)

            bedrooms = item.get("num_bedrooms")
            if not isinstance(bedrooms, int):
                bedrooms = self.parse_int(str(bedrooms) if bedrooms is not None else None)

            listings.append(
                Listing(
                    source_site=self.source_name,
                    source_listing_id=listing_id,
                    source_url=url,
                    title=title,
                    city=city,
                    rent_price=rent_price,
                    living_area_m2=living_area,
                    rooms_total=total_rooms,
                    bedrooms=bedrooms,
                    available_from=available_from,
                    raw_features=raw_features,
                    is_available=is_available,
                    listing_status=listing_status,
                )
            )

        unique: dict[str, Listing] = {item.source_listing_id: item for item in listings}
        return list(unique.values())
