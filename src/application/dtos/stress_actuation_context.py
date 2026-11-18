"""Contexto de actuadores y servicios secundarios para predicción de estrés."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from src.domain.ports.hardware_controller_port import IHardwareController
from src.domain.ports.notifier_port import INotifier
from src.domain.ports.weather_cache_port import IWeatherCache
from src.domain.value_objects.milking_schedule import MilkingSchedule


@dataclass(frozen=True)
class StressActuationContext:
    """Encapsula colaboradores opcionales de notificación, hardware y persistencia."""

    notifier: INotifier | None = None
    hardware_controller: IHardwareController | None = None
    weather_cache: IWeatherCache | None = None
    milking_schedule: MilkingSchedule | None = None

    @classmethod
    def from_args(
        cls,
        context: "StressActuationContext | None",
        args: Sequence[Any],
        kwargs: dict[str, Any],
    ) -> "StressActuationContext":
        """Resuelve el contexto a partir de parámetros posicionales o nombrados."""
        if context is not None:
            return context
        return cls(
            notifier=args[0] if len(args) > 0 else kwargs.get("notifier"),
            hardware_controller=args[1]
            if len(args) > 1
            else kwargs.get("hardware_controller"),
            weather_cache=args[2] if len(args) > 2 else kwargs.get("weather_cache"),
            milking_schedule=args[3]
            if len(args) > 3
            else kwargs.get("milking_schedule"),
        )
