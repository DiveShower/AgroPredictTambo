"""Excepción lanzada al consultar un sector inexistente en el tambo."""

from src.domain.exceptions.base_domain_exception import BaseDomainException


class SectorNotFoundException(BaseDomainException):
    """Error al intentar acceder a un sector por un identificador desconocido."""
