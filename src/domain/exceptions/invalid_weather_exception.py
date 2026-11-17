"""Excepción lanzada cuando los datos meteorológicos están fuera de rango físico."""

from src.domain.exceptions.base_domain_exception import BaseDomainException


class InvalidWeatherException(BaseDomainException):
    """Error de validación física en mediciones o pronósticos climáticos."""
