"""ViewModel de curva proyectada ITH 24h y simulador interactivo (Anillo 3)."""

from datetime import datetime
from typing import Any, Optional
from src.domain.ports.model_predictor_port import IModelPredictor
from src.domain.ports.weather_provider_port import IWeatherProvider
from src.domain.value_objects.cooling_cycle import CoolingCycle
from src.domain.value_objects.nocturnal_recovery import NocturnalRecovery
from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions


class ForecastViewModel:
    """Prepara series de 24h y simulaciones para las vistas sin usar matplotlib ni Qt."""

    def __init__(
        self,
        weather_provider: IWeatherProvider,
        predictor: Optional[IModelPredictor] = None,
    ) -> None:
        self._weather = weather_provider
        self._predictor = predictor

    def get_24h_curve_data(self, lat: float = -31.25, lon: float = -61.48) -> dict[str, Any]:
        """Devuelve etiquetas horarias, curva ITH, umbrales ajustados y puntos críticos."""
        forecast = self._weather.get_hourly_forecast(lat, lon, hours=24)
        night = [c for c in forecast if c.timestamp.hour >= 21 or c.timestamp.hour < 6][:6]
        warm_n = sum(1 for c in night if THI_Score.calculate(c.temperature_c, c.relative_humidity).value >= 65.0)
        penalty = NocturnalRecovery(cool_hours_count=max(0, 6 - warm_n)).threshold_penalty
        alert_lim, danger_lim = round(72.0 - penalty, 2), round(78.0 - penalty, 2)

        labels = [c.timestamp.strftime("%H:%M") for c in forecast]
        thi_vals = [THI_Score.calculate(c.temperature_c, c.relative_humidity).value for c in forecast]
        danger_idx = [i for i, val in enumerate(thi_vals) if val >= danger_lim]
        return {
            "hours_labels": labels, "thi_values": thi_vals,
            "alert_threshold": alert_lim, "danger_threshold": danger_lim,
            "nocturnal_penalty": penalty, "danger_indices": danger_idx,
        }

    def simulate_custom_conditions(
        self, temp_c: float, rh: float, wind_kmh: float, rad_wm2: float
    ) -> dict[str, Any]:
        """Calcula respuesta instantánea ante movimiento de sliders del jurado."""
        cond = WeatherConditions(temp_c, rh, wind_kmh, datetime(2026, 1, 15, 14, 0), rad_wm2)
        thi = THI_Score.calculate(temp_c, rh)
        lvl = self._predictor.predict_stress_level(cond) if self._predictor else thi.stress_level
        lvl = max(lvl, thi.stress_level)
        c_std = CoolingCycle.for_stress_level(lvl, allows_water_sprinkling=True)
        c_comp = CoolingCycle.for_stress_level(lvl, allows_water_sprinkling=False)
        return {
            "thi_value": thi.value, "stress_level": lvl, "category": thi.category_name,
            "concrete_order": f"Agua: {c_std.water_mist_seconds}s | Vent: {c_std.fan_ventilation_seconds}s",
            "compost_order": f"Agua: {c_comp.water_mist_seconds}s (Bloqueo Anti-Mastitis) | Vent: {c_comp.fan_ventilation_seconds}s",
        }
