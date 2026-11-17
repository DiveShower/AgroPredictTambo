"""Contrato abstracto para control físico o simulado de relés de agua y ventilación."""

from typing import Protocol


class IHardwareController(Protocol):
    """Puerto de actuación sobre electroválvulas y ventiladores del tambo."""

    def activate_water_valve(self, sector_id: str, duration_seconds: int) -> bool:
        """Activa la electroválvula de aspersión de un sector por un tiempo acotado."""
        ...

    def activate_ventilation_fan(self, sector_id: str, duration_seconds: int) -> bool:
        """Activa los ventiladores forzados de un sector por un tiempo determinado."""
        ...

    def emergency_shutoff_all(self) -> None:
        """Detiene inmediatamente todos los actuadores del establecimiento."""
        ...
