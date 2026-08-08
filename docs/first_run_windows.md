# First run on Windows (local)

You can run this without Telegram first.

## 1) Python and venv
- Install Python 3.11+
- In PowerShell:
  - `./scripts/setup_local.ps1`

This script uses only `./.venv/Scripts/python.exe` and does not install globally.

## 2) Environment file
- Copy `.env.example` to `.env`
- You can leave `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` empty for first run

## 3) First run
- `./scripts/run_once.ps1`

The SQLite database is auto-created at `data/huur_scraper.db`.

## 4) Check output data quickly
Use any SQLite viewer or run:
- `.\.venv\Scripts\python.exe -c "import sqlite3; c=sqlite3.connect('data/huur_scraper.db'); print(c.execute('select count(*) from listings').fetchone())"`

## 5) Optional Telegram setup (later)
1. In Telegram, open `@BotFather`, create bot, copy token.
2. Send a message to your bot.
3. Find your chat id (for private chat often your numeric user id).
4. Put token/id in `.env`.
5. Re-run `./scripts/run_once.ps1`.
