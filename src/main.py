from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.config import load_settings
from src.logging_setup import configure_logging
from src.scrapers.runner import run_all_sources
from src.scrapers.sites.nrw_wonen import NRWonenScraper
from src.scrapers.sites.thehaguerealestate import TheHagueRealEstateScraper
from src.scrapers.sites.wobeco import WobecoScraper
from src.storage.sqlite_store import SQLiteStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run rental source scraping")
    parser.add_argument("--once", action="store_true", help="Run one scraping cycle")
    parser.add_argument(
        "--sources",
        type=str,
        default="",
        help="Comma-separated source names (optional)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings()
    configure_logging(settings)
    logger = logging.getLogger(__name__)
    logger.info("Starting run (once=%s, sources=%s)", args.once, args.sources or "all")

    store = SQLiteStore(settings.database_path)

    source_factories = {
        "thehaguerealestate": TheHagueRealEstateScraper,
        "wobeco": WobecoScraper,
        "nrw_wonen": NRWonenScraper,
    }

    selected_sources = (
        {item.strip() for item in args.sources.split(",") if item.strip()}
        if args.sources
        else None
    )

    registry_file = Path("src/config/sources.yaml")

    run_all_sources(
        settings=settings,
        store=store,
        source_factories=source_factories,
        registry_file=registry_file,
        selected_sources=selected_sources,
    )
    logger.info("Run completed")


if __name__ == "__main__":
    main()
