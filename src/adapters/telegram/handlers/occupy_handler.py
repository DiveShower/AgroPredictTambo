"""Handler para el comando /ocupar del bot de Telegram."""

from collections.abc import Callable

from src.application.use_cases.toggle_sector_occupancy_uc import (
    ToggleSectorOccupancyUseCase,
)
from src.domain.exceptions.sector_not_found_exception import SectorNotFoundException

_TRUE_VALUES = {"true", "1", "si", "sí", "on"}
_FALSE_VALUES = {"false", "0", "no", "off"}


class OccupyHandler:
    """Gestiona el comando /ocupar para actualizar ocupación y sincronizar SCADA."""

    def __init__(
        self,
        toggle_uc: ToggleSectorOccupancyUseCase,
        on_changed: Callable[[str, bool], None] | None = None,
    ) -> None:
        """Inicializa el handler con el caso de uso y un callback opcional."""
        self._toggle_uc = toggle_uc
        self._on_changed = on_changed

    @staticmethod
    def _parse_bool(raw: str | bool) -> bool:
        """Convierte cadenas o booleanos válidos en bool; lanza ValueError si falla."""
        if isinstance(raw, bool):
            return raw
        normalized = raw.strip().lower()
        if normalized in _TRUE_VALUES:
            return True
        if normalized in _FALSE_VALUES:
            return False
        raise ValueError(f"Valor booleano inválido: {raw!r}")

    def handle(self, sector_id: str, raw_flag: str | bool) -> str:
        """Actualiza la ocupación del sector, notifica al callback y responde texto."""
        cleaned_id = sector_id.strip()
        if not cleaned_id:
            return "Uso: /ocupar <sector_id> <true|false>"
        try:
            is_occupied = self._parse_bool(raw_flag)
        except ValueError:
            return "Uso: /ocupar <sector_id> <true|false>"
        try:
            sector = self._toggle_uc.execute(cleaned_id, is_occupied)
        except SectorNotFoundException:
            return f"Sector no encontrado: {cleaned_id}."
        if self._on_changed is not None:
            self._on_changed(sector.sector_id, sector.current_occupancy)
        state = "OCUPADO" if sector.current_occupancy else "VACÍO"
        return f"Sector {sector.sector_id} ({sector.name}) actualizado a {state}."
