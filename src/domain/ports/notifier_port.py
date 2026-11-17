"""Contrato abstracto para emisión síncrona de notificaciones push de alerta."""

from typing import Protocol

from src.domain.entities.heat_stress_alert import HeatStressAlert


class INotifier(Protocol):
    """Puerto de envío de alertas preventivas de estrés térmico."""

    def send_alert(self, alert: HeatStressAlert) -> bool:
        """Envía una notificación de alerta y retorna True si fue entregada."""
        ...
