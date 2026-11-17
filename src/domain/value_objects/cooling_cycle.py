"""Value Object para parámetros hidráulicos y temporales del ciclo evaporativo."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CoolingCycle:
    """Parámetros técnicos del micro-ciclo de enfriamiento (INTA Rafaela / Chen 2016)."""

    water_mist_seconds: int = 40
    fan_ventilation_seconds: int = 270
    sprinkler_flow_lpm: float = 1.3
    traditional_flow_lpm: float = 4.9
    pump_power_kw: float = 2.2
    fan_unit_power_kw: float = 0.75

    @property
    def total_cycle_seconds(self) -> int:
        """Duración total de un ciclo combinado en segundos."""
        return self.water_mist_seconds + self.fan_ventilation_seconds

    @property
    def cycles_per_hour(self) -> float:
        """Cantidad de ciclos completos que caben en una hora activa."""
        if self.total_cycle_seconds <= 0:
            return 0.0
        return 3600.0 / self.total_cycle_seconds

    @property
    def water_duty_cycle(self) -> float:
        """Fracción de tiempo en que la bomba de agua permanece activa por ciclo."""
        if self.total_cycle_seconds <= 0:
            return 0.0
        return self.water_mist_seconds / self.total_cycle_seconds

    @property
    def active_water_minutes_per_hour(self) -> float:
        """Minutos efectivos de bombeo de agua por hora en operación combinada."""
        return 60.0 * self.water_duty_cycle

    @classmethod
    def for_stress_level(
        cls,
        stress_level: int,
        allows_water_sprinkling: bool = True,
    ) -> "CoolingCycle":
        """Construye la configuración de ciclo según el nivel de estrés y tipo de piso."""
        if stress_level <= 0:
            return cls(water_mist_seconds=0, fan_ventilation_seconds=0)
        if stress_level == 1:
            return cls(water_mist_seconds=0, fan_ventilation_seconds=270)
        water_secs = 40 if allows_water_sprinkling else 0
        return cls(water_mist_seconds=water_secs, fan_ventilation_seconds=270)
