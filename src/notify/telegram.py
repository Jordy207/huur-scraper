from __future__ import annotations

import logging

import httpx


logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

    @property
    def enabled(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_message(self, text: str) -> None:
        if not self.enabled:
            logger.debug("Telegram disabled; skipping message")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        response = httpx.post(url, json=payload, timeout=20)
        response.raise_for_status()
        logger.info("Telegram message sent")
