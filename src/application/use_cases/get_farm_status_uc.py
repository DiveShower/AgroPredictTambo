"""Caso de uso para consultar el estado operativo consolidado de los sectores."""

from typing import Optional

from src.application.dtos.sector_status_dto import SectorStatusDTO
from src.domain.entities.sector import Sector
from src.domain.ports.sector_repository_port import ISectorRepository
from src.domain.ports.weather_provider_port import IWeatherProvider
from src.domain.value_objects.cooling_cycle import CoolingCycle
from src.domain.value_objects.thi_score import THI_Score


def _describe_cycle(sec: Sector, stress: int) -> str:
    if not sec.current_occupancy:
        return "Inactivo (Sin ocupación)"
    if stress == 0:
        return "Confort Térmico (Apagado)"
    if stress == 1:
        return "Alerta (Solo Ventilación 270s)"
    return (
        "Peligro (Aspersión 40s + Ventilación 270s)"
        if sec.allows_water_sprinkling
        else "Peligro Sanitario (Solo Ventilación 270s)"
    )


class GetFarmStatusUseCase:
    """Consolida el estado operativo, sanitario y de ocupación del tambo."""

    def __init__(
        self,
        sector_repository: ISectorRepository,
        weather_provider: Optional[IWeatherProvider] = None,
    ) -> None:
        self._sector_repo = sector_repository
        self._weather = weather_provider

    def _current_thi(self, lat: float, lon: float) -> float:
        if not self._weather:
            return 65.0
        try:
            cond = self._weather.get_current_weather(lat, lon)
            return THI_Score.calculate(cond.temperature_c, cond.relative_humidity).value
        except Exception:
            return 65.0

    def execute(self, latitude: float = -31.25, longitude: float = -61.48) -> list[SectorStatusDTO]:
        thi = self._current_thi(latitude, longitude)
        result: list[SectorStatusDTO] = []
        for s in self._sector_repo.get_all_sectors():
            lvl = s.evaluate_stress_level(thi) if s.current_occupancy else 0
            cyc = CoolingCycle.for_stress_level(lvl, s.allows_water_sprinkling)
            active = s.current_occupancy and cyc.total_cycle_seconds > 0
            result.append(SectorStatusDTO(
                s.sector_id, s.name, s.cow_capacity, s.current_occupancy,
                s.allows_water_sprinkling, s.sprinkler_count, s.fan_count,
                lvl, _describe_cycle(s, lvl), active,
            ))
        return result
