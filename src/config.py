from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_path: Path
    telegram_bot_token: str
    telegram_chat_id: str
    user_agent: str
    max_workers: int
    request_timeout_seconds: int
    max_rent_eur: int
    min_size_m2: int
    preferred_bedrooms: int
    allow_close_match: bool
    allowed_cities: list[str]
    log_level: str
    log_file_path: Path
    log_to_console: bool


def _parse_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_cities(value: str) -> list[str]:
    if not value:
        return ["Den Haag", "Delft"]
    return [item.strip() for item in value.split(",") if item.strip()]


def load_settings() -> Settings:
    load_dotenv()

    database_path = Path(os.getenv("DATABASE_PATH", "data/huur_scraper.db"))
    return Settings(
        database_path=database_path,
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        user_agent=os.getenv("USER_AGENT", "huur-scraper/0.1"),
        max_workers=int(os.getenv("MAX_WORKERS", "2")),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
        max_rent_eur=int(os.getenv("MAX_RENT_EUR", "1000")),
        min_size_m2=int(os.getenv("MIN_SIZE_M2", "40")),
        preferred_bedrooms=int(os.getenv("PREFERRED_BEDROOMS", "2")),
        allow_close_match=_parse_bool(os.getenv("ALLOW_CLOSE_MATCH", "true"), True),
        allowed_cities=_parse_cities(os.getenv("ALLOWED_CITIES", "Den Haag,Delft")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        log_file_path=Path(os.getenv("LOG_FILE_PATH", "logs/huur_scraper.log")),
        log_to_console=_parse_bool(os.getenv("LOG_TO_CONSOLE", "true"), True),
    )
