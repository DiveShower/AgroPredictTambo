"""Servicio driver del bot de Telegram usando python-telegram-bot v22."""

from collections.abc import Callable
from os import getenv as env
from pathlib import Path

from telegram import Update, error
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

from src.infrastructure.ui.telegram_bot import bot_command_router as bcr
from src.infrastructure.ui.telegram_bot.qr_generator import generate_bot_qr

_CMDS = "start help estado pronostico sectores ocupar prediccion ahorro reporte"
COMMANDS = tuple(_CMDS.split())
_ENV = "TELEGRAM_BOT_TOKEN"
Router = bcr.TelegramCommandRouter


class TelegramBotService:
    """Orquesta recepción de comandos de Telegram y despacho al router."""

    def __init__(self, router: Router | None = None, token: str | None = None) -> None:
        self._router = router or bcr.build_default_router()
        self._token = (env(_ENV, "") if token is None else token).strip()

    def handle_text(self, raw_text: str, chat_id: int = 0) -> tuple[str, str | None]:
        return self._router.dispatch(raw_text, chat_id)

    def build_application(self) -> Application:
        app = ApplicationBuilder().token(self._token).build()

        async def _on_command(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
            if msg := update.effective_message:
                cid = update.effective_chat.id if update.effective_chat else 0
                text, pdf = self.handle_text(msg.text or "/start", cid)
                await msg.reply_text(text)
                if pdf and Path(pdf).exists():
                    await msg.reply_document(document=Path(pdf))

        app.add_handlers([CommandHandler(cmd, _on_command) for cmd in COMMANDS])
        return app


def run_bot(
    force_heatwave: bool = False,
    on_occupancy_changed: Callable[[str, bool], None] | None = None,
) -> int:
    """Inicia el bot en modo polling o falla de forma segura si falta el token."""
    qr_path, token = generate_bot_qr(), env(_ENV, "").strip()
    if not token or token.startswith("REEMPLAZAR"):
        print(f"Falta {_ENV} válido. QR del bot en: {qr_path}")
        return 0
    try:
        router = bcr.build_default_router(force_heatwave, on_occupancy_changed)
        TelegramBotService(router, token).build_application().run_polling()
    except (error.TelegramError, OSError, RuntimeError, ValueError) as exc:
        print(f"Bot de Telegram detenido de forma segura: {exc}")
    return 0
