"""Value Object para turnos de ordeñe y ventanas de pre-enfriamiento preventivo."""

from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class MilkingSchedule:
    """Agenda diaria de ordeñe del tambo y disparo de pre-enfriamiento en corral."""

    morning_start: time = time(4, 30)
    morning_end: time = time(7, 0)
    afternoon_start: time = time(16, 0)
    afternoon_end: time = time(18, 30)
    precooling_lead_minutes: int = 15

    def is_milking_time(self, check_time: time) -> bool:
        """Determina si el horario corresponde a un turno activo de ordeñe."""
        in_morning = self.morning_start <= check_time <= self.morning_end
        in_afternoon = self.afternoon_start <= check_time <= self.afternoon_end
        return in_morning or in_afternoon

    def requires_precooling(
        self,
        check_time: time,
        projected_thi: float,
        danger_threshold: float = 78.0,
    ) -> bool:
        """Indica si corresponde pre-enfriar 15 min antes del ingreso bajo ITH peligroso."""
        if projected_thi < danger_threshold:
            return False

        check_minutes = check_time.hour * 60 + check_time.minute
        for shift_start in (self.morning_start, self.afternoon_start):
            start_minutes = shift_start.hour * 60 + shift_start.minute
            minutes_until_shift = start_minutes - check_minutes
            if 0 < minutes_until_shift <= self.precooling_lead_minutes:
                return True
        return False
