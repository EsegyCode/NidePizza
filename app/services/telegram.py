import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)


def send_telegram_message(message: str) -> bool:
    """Send an HTML-formatted notification to Telegram if configured."""
    token = current_app.config.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = current_app.config.get("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        logger.debug("Telegram not configured; skipping notification.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=payload, timeout=5)
        resp.raise_for_status()
        return True
    except Exception as exc:
        logger.warning("Failed to send Telegram notification: %s", exc)
        return False
