"""Widget indicador visual de nivel de ITH y deuda térmica nocturna."""

from typing import Optional

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QWidget


class ThiGaugeWidget(QFrame):
    """Barra y cuadrante de estado bioclimático general del establecimiento."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("ThiGauge")
        layout = QHBoxLayout(self)

        self.summary_label = QLabel("ITH Actual: 65.0 | Proyectado (+1h): 65.0 | Deuda Nocturna: 0h")
        self.progress = QProgressBar()
        self.progress.setRange(40, 100)
        self.progress.setValue(65)
        self.progress.setFormat("ITH %v")

        layout.addWidget(self.summary_label, stretch=2)
        layout.addWidget(self.progress, stretch=1)

    def update_metrics(
        self,
        current_thi: float,
        predicted_thi: float,
        nocturnal_debt: int = 0,
    ) -> None:
        """Actualiza el indicador numérico y la barra de progreso de ITH."""
        self.summary_label.setText(
            f"ITH Actual: {current_thi:.1f} | Proyectado (+1h): {predicted_thi:.1f} | Deuda Nocturna: {nocturnal_debt}h"
        )
        clamped = max(40, min(100, int(round(predicted_thi))))
        self.progress.setValue(clamped)
        color = "#2ecc71" if predicted_thi < 72.0 else ("#f1c40f" if predicted_thi < 78.0 else "#e74c3c")
        self.progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
