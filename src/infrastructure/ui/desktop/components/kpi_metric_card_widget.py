"""Widget de tarjeta KPI reutilizable para métricas de ahorro y sostenibilidad."""

from typing import Optional

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class KpiMetricCardWidget(QFrame):
    """Muestra un título de indicador y su valor formateado desde SavingsViewModel."""

    def __init__(
        self,
        title: str,
        initial_value: str = "--",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("SectorCard")
        layout = QVBoxLayout(self)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("HeaderTitle")
        self.value_label = QLabel(initial_value)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, formatted_value: str) -> None:
        """Actualiza el valor textual renderizado en la tarjeta."""
        self.value_label.setText(formatted_value)
