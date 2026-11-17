"""Adaptador predictor heurístico de salvaguarda (fail-safe)."""

from collections.abc import Sequence

from src.domain.ports.model_predictor_port import IModelPredictor
from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions


class HeuristicPredictorAdapter(IModelPredictor):
    """Predictor bioclimático determinístico para operación offline o fallback."""

    def __init__(
        self,
        threshold_alert: float = 72.0,
        threshold_danger: float = 78.0,
    ) -> None:
        self._alert = threshold_alert
        self._danger = threshold_danger

    def _calc_effective_load(
        self,
        cond: WeatherConditions,
        hist: Sequence[WeatherConditions],
        debt: int,
    ) -> float:
        thi = THI_Score.calculate(cond.temperature_c, cond.relative_humidity).value
        rad_pen = 0.0
        if cond.solar_radiation_wm2 > 500.0:
            rad_pen = 0.5 + 2.0 * min(1.0, (cond.solar_radiation_wm2 - 500.0) / 500.0)
        inertia = 0.0
        if hist:
            w = hist[-3:]
            avg_thi = sum(
                THI_Score.calculate(c.temperature_c, c.relative_humidity).value
                for c in w
            ) / len(w)
            inertia = max(0.0, 0.15 * (avg_thi - 72.0))
        debt_pen = 0.35 * max(0, min(6, debt))
        wind_cooling = 0.3 * (cond.wind_speed_kmh / 3.6)
        return thi + rad_pen + inertia + debt_pen - wind_cooling

    def predict_stress_level(
        self,
        conditions: WeatherConditions,
        recent_history: Sequence[WeatherConditions] = (),
        nocturnal_debt_hours: int = 0,
    ) -> int:
        """Calcula el estrés térmico considerando ITH y variables bioclimáticas."""
        load = self._calc_effective_load(
            conditions, recent_history, nocturnal_debt_hours
        )
        if load >= self._danger:
            return 2
        if load >= self._alert:
            return 1
        return 0
