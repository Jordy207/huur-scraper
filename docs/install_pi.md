# Raspberry Pi setup

## 1) Copy project to Pi
Place this repository in `/home/pi/huur_scraper`.

## 2) Create environment and install deps
```bash
cd /home/pi/huur_scraper
chmod +x scripts/setup_pi.sh
./scripts/setup_pi.sh
```

## 3) Configure env
```bash
cp .env.example .env
nano .env
```
Set at least your matching profile and (optionally) Telegram.

Recommended logging values in `.env`:
- `LOG_LEVEL=INFO`
- `LOG_FILE_PATH=logs/huur_scraper.log`
- `LOG_TO_CONSOLE=true`

## 4) Test once manually
```bash
/home/pi/huur_scraper/.venv/bin/python -m src.main --once
```

## 5) Install systemd units
```bash
sudo cp deploy/systemd/huur-scraper.service /etc/systemd/system/
sudo cp deploy/systemd/huur-scraper.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now huur-scraper.timer
```

## 6) Observe runtime logs
```bash
journalctl -u huur-scraper.service -f
tail -f /home/pi/huur_scraper/logs/huur_scraper.log
```

## Useful checks
```bash
systemctl status huur-scraper.timer
systemctl list-timers | grep huur-scraper
```
