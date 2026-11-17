"""Excepción raíz para errores de reglas de negocio en la capa de dominio."""


class BaseDomainException(Exception):
    """Excepción base de dominio para el sistema predictivo de estrés térmico."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
