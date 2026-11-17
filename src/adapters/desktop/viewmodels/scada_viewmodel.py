"""ViewModel del tablero SCADA desacoplado de PyQt6 (Anillo 3 - Adapters)."""

from collections.abc import Callable
from typing import Any, Optional
from src.application.dtos.predict_stress_request_dto import PredictStressRequestDTO
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.application.use_cases.get_farm_status_uc import GetFarmStatusUseCase
from src.application.use_cases.predict_sector_stress_uc import PredictSectorStressUseCase
from src.application.use_cases.toggle_sector_occupancy_uc import ToggleSectorOccupancyUseCase
from src.domain.value_objects.cooling_cycle import CoolingCycle

LEVEL_COLORS = {0: "#2ecc71", 1: "#f1c40f", 2: "#e74c3c"}
LEVEL_LABELS = {0: "CONFORT", 1: "ALERTA LEVE", 2: "PELIGRO"}


class ScadaViewModel:
    """Transforma DTOs de aplicación en modelos de presentación para la vista SCADA."""

    def __init__(
        self, predict_uc: PredictSectorStressUseCase, status_uc: GetFarmStatusUseCase,
        toggle_uc: ToggleSectorOccupancyUseCase, shutoff_fn: Optional[Callable[[], None]] = None,
    ) -> None:
        self._predict_uc, self._status_uc = predict_uc, status_uc
        self._toggle_uc, self._shutoff_fn = toggle_uc, shutoff_fn

    def get_cards_state(self, lat: float = -31.25, lon: float = -61.48) -> list[dict[str, Any]]:
        """Devuelve diccionarios listos para renderizar en cada SectorCardWidget."""
        cards: list[dict[str, Any]] = []
        for s in self._status_uc.execute(lat, lon):
            cyc = CoolingCycle.for_stress_level(s.current_stress_level, s.allows_water_sprinkling)
            w_sec = cyc.water_mist_seconds if s.current_occupancy else 0
            f_sec = cyc.fan_ventilation_seconds if s.current_occupancy else 0
            w_txt = "ASPERSION BLOQUEADA (Anti-Mastitis)" if not s.allows_water_sprinkling else (f"Bomba Activa: {w_sec}s" if w_sec > 0 else "Bomba: OFF")
            cards.append({
                "sector_id": s.sector_id, "name": s.name, "capacity": s.cow_capacity,
                "is_occupied": s.current_occupancy, "stress_level": s.current_stress_level,
                "status_badge": LEVEL_LABELS.get(s.current_stress_level, "CONFORT"),
                "color_hex": LEVEL_COLORS.get(s.current_stress_level, "#2ecc71"),
                "allows_water": s.allows_water_sprinkling, "water_seconds": w_sec,
                "fan_seconds": f_sec, "water_text": w_txt, "cycle_desc": s.cycle_description,
            })
        return cards

    def sync_weather_and_predict(self, lat: float = -31.25, lon: float = -61.48) -> PredictStressResponseDTO:
        return self._predict_uc.execute(PredictStressRequestDTO(lat, lon))

    def toggle_occupancy(self, sector_id: str, is_occupied: bool) -> list[dict[str, Any]]:
        self._toggle_uc.execute(sector_id, is_occupied)
        return self.get_cards_state()

    def emergency_shutoff(self) -> None:
        if self._shutoff_fn:
            self._shutoff_fn()
