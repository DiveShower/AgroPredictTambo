"""Contexto de actuadores y servicios secundarios para predicción de estrés."""

from dataclasses import dataclass

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
