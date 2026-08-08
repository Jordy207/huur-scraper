# huur_scraper

Compliance-first rental listing aggregator for Delft/The Hague area.

## MVP features
- Multi-source scraping with conservative rate limits
- Source policy modes: `SCRAPE`, `ALERT_INGEST`, `DISABLED`
- Hard and close-match filtering
- SQLite persistence + dedupe
- Telegram alerts
- Raspberry Pi systemd service/timer

## Quick start
1. Run `./scripts/setup_local.ps1`.
2. Copy `.env.example` to `.env` and fill Telegram values.
3. Run once:
   - `./scripts/run_once.ps1`

## Local-first setup (Windows)
- Follow [docs/first_run_windows.md](docs/first_run_windows.md)
- Telegram is optional for the first run
- Database is created automatically at `data/huur_scraper.db`

## Raspberry Pi setup
- Follow [docs/install_pi.md](docs/install_pi.md)

## Current MVP sources
- `thehaguerealestate`
- `wobeco`
- `nrw_wonen`

Run only selected sources:
- `./scripts/run_once.ps1 --sources thehaguerealestate,wobeco`

## Safety defaults
- Low concurrency
- Retry with backoff
- Auto-block handling for 403/429
- Policy-driven source enablement

## Logging
- Console logs are enabled by default
- File logs are written to `logs/huur_scraper.log`
- Configure via `.env`: `LOG_LEVEL`, `LOG_FILE_PATH`, `LOG_TO_CONSOLE`

Raspberry Pi monitoring commands:
- `tail -f logs/huur_scraper.log`
- `journalctl -u huur-scraper.service -f`
