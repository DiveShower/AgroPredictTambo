"""Pruebas unitarias para el generador de enlaces y QR de Telegram."""

from pathlib import Path

import pytest

from src.infrastructure.ui.telegram_bot.qr_generator import (
    generate_bot_qr,
    get_bot_deep_link,
)


def test_get_bot_deep_link_default_and_explicit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_USERNAME", raising=False)
    assert get_bot_deep_link() == "https://t.me/AgroStressNestleBot"
    assert get_bot_deep_link(" @MiTamboBot ") == "https://t.me/MiTamboBot"


def test_get_bot_deep_link_env_var_and_empty_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_USERNAME", "@TamboEnvBot")
    assert get_bot_deep_link() == "https://t.me/TamboEnvBot"
    monkeypatch.setenv("TELEGRAM_BOT_USERNAME", "   ")
    assert get_bot_deep_link() == "https://t.me/AgroStressNestleBot"


def test_generate_bot_qr_creates_subdirs_and_valid_png(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "nested" / "dir" / "bot_qr.png"
    result = generate_bot_qr(bot_username=" @MiTamboBot ", output_path=output_path)
    assert result == output_path
    assert result.exists()
    data = result.read_bytes()
    assert len(data) > 0
    assert data.startswith(b"\x89PNG")
