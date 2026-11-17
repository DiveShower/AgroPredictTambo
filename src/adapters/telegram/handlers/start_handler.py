"""Handler para el comando /start y registro de suscriptores de Telegram."""

from src.adapters.telegram.formatters.message_formatter import TelegramMessageFormatter


class StartHandler:
    """Gestiona el comando /start y registra chats suscriptores."""

    def __init__(self, subscribed_chat_ids: set[int] | None = None) -> None:
        """Inicializa el handler con el conjunto de chats suscriptos."""
        self.subscribed_chat_ids: set[int] = (
            subscribed_chat_ids if subscribed_chat_ids is not None else set()
        )

    def handle(self, chat_id: int = 0) -> str:
        """Registra un chat válido y retorna el mensaje de bienvenida."""
        if chat_id > 0:
            self.subscribed_chat_ids.add(chat_id)
        return TelegramMessageFormatter.format_welcome()
