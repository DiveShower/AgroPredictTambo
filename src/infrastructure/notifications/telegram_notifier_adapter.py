"""Adaptador emisor HTTP REST síncrono para alertas preventivas en Telegram."""

import os
from typing import Optional

import requests

from src.domain.entities.heat_stress_alert import HeatStressAlert
from src.domain.ports.notifier_port import INotifier


class TelegramNotifierAdapter(INotifier):
    """Envía alertas de estrés térmico vía HTTP POST síncrono (thread-safe)."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        admin_chat_id: Optional[str] = None,
        timeout_seconds: int = 5,
    ) -> None:
        self._token = (
            bot_token
            if bot_token is not None
            else os.getenv("TELEGRAM_BOT_TOKEN", "")
        )
        self._chat_id = (
            admin_chat_id
            if admin_chat_id is not None
            else os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")
        )
        self._timeout = timeout_seconds

    def _format_message(self, alert: HeatStressAlert) -> str:
        hora = alert.target_time.strftime("%H:%M")
        return (
            f"🚨 *ALERTA PREVENTIVA ESTRÉS TÉRMICO*\n"
            f"• *Sector:* {alert.sector_name} (`{alert.sector_id}`)\n"
            f"• *ITH Proyectado ({hora} hs):* `{alert.thi_value}` (Nivel {alert.stress_level})\n"
            f"• *Acción:* {alert.recommended_action}"
        )

    def send_alert(self, alert: HeatStressAlert) -> bool:
        """Despacha la notificación a la API REST de Telegram sin usar asyncio."""
        if not self._token or not self._chat_id:
            return False
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload = {
            "chat_id": self._chat_id,
            "text": self._format_message(alert),
            "parse_mode": "Markdown",
        }
        try:
            resp = requests.post(url, json=payload, timeout=self._timeout)
            return resp.status_code == 200
        except Exception:
            return False
