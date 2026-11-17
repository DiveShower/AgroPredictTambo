"""Simulador de relés IoT en memoria con Watchdog de seguridad de 60 segundos."""

from src.domain.ports.hardware_controller_port import IHardwareController

MAX_WATER_WATCHDOG_SECONDS = 60


class MockRelayAdapter(IHardwareController):
    """Simula electroválvulas y ventiladores registrando tiempos activos."""

    def __init__(self) -> None:
        self.water_valves_seconds: dict[str, int] = {}
        self.ventilation_fans_seconds: dict[str, int] = {}

    def activate_water_valve(self, sector_id: str, duration_seconds: int) -> bool:
        """Activa la electroválvula aplicando corte Watchdog máximo de 60s."""
        if duration_seconds <= 0:
            self.water_valves_seconds[sector_id] = 0
            return False
        clamped = min(MAX_WATER_WATCHDOG_SECONDS, duration_seconds)
        self.water_valves_seconds[sector_id] = clamped
        return True

    def activate_ventilation_fan(
        self, sector_id: str, duration_seconds: int
    ) -> bool:
        """Activa los ventiladores forzados del sector por la duración indicada."""
        if duration_seconds <= 0:
            self.ventilation_fans_seconds[sector_id] = 0
            return False
        self.ventilation_fans_seconds[sector_id] = duration_seconds
        return True

    def emergency_shutoff_all(self) -> None:
        """Apaga inmediatamente todas las electroválvulas y ventiladores."""
        for sec_id in list(self.water_valves_seconds.keys()):
            self.water_valves_seconds[sec_id] = 0
        for sec_id in list(self.ventilation_fans_seconds.keys()):
            self.ventilation_fans_seconds[sec_id] = 0
