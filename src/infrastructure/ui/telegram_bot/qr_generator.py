"""Generador de enlaces profundos y códigos QR para el bot de Telegram."""

from __future__ import annotations

import os
from pathlib import Path

import qrcode

DEFAULT_BOT_USERNAME = "AgroStressNestleBot"
DEFAULT_QR_PATH = Path("data/cache/bot_qr.png")


def get_bot_deep_link(bot_username: str | None = None) -> str:
    """Construye el deep link HTTPS hacia el bot de Telegram configurado."""
    raw = bot_username or os.getenv("TELEGRAM_BOT_USERNAME", DEFAULT_BOT_USERNAME)
    username = raw.strip().lstrip("@").strip() or DEFAULT_BOT_USERNAME
    return f"https://t.me/{username}"


def generate_bot_qr(
    bot_username: str | None = None,
    output_path: Path | str = DEFAULT_QR_PATH,
) -> Path:
    """Genera un PNG con el código QR del deep link del bot y retorna su ruta."""
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    image = qrcode.make(get_bot_deep_link(bot_username))
    with target.open("wb") as stream:
        image.save(stream)
    return target
