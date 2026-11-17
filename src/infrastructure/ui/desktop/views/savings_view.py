"""Vista de retorno financiero (SIGLeA) y ahorro hídrico/energético ESG."""

from typing import Optional

from PyQt6.QtWidgets import QGridLayout, QPushButton, QVBoxLayout, QWidget

from src.adapters.desktop.viewmodels.savings_viewmodel import SavingsViewModel
from src.infrastructure.ui.desktop.components.kpi_metric_card_widget import (
    KpiMetricCardWidget,
)

KPI_DEFINITIONS = (
    ("water_software", "Agua Ahorrada (Software 1.3 L/min)"),
    ("water_combined", "Ahorro Hidraulico Combinado (vs 4.9 L/min)"),
    ("energy_kwh", "Energia Electrica Ahorrada (kWh)"),
    ("carbon_cammesa", "Huella de Carbono Evitada (CAMMESA)"),
    ("milk_siglea", "Leche Protegida (Panel SIGLeA)"),
    ("economic_ars", "Retorno Financiero Diario (ARS)"),
)


class SavingsView(QWidget):
    """Pestaña 3: Muestra tarjetas KPI de ahorro hídrico, energético y leche."""

    def __init__(
        self,
        viewmodel: SavingsViewModel,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._cards: dict[str, KpiMetricCardWidget] = {}

        root = QVBoxLayout(self)
        grid = QGridLayout()
        for idx, (key, title) in enumerate(KPI_DEFINITIONS):
            card = KpiMetricCardWidget(title, parent=self)
            self._cards[key] = card
            grid.addWidget(card, idx // 2, idx % 2)
        root.addLayout(grid)

        self.refresh_btn = QPushButton("Recalcular Balance de Ahorro (8h Fijo vs Predictivo)")
        self.refresh_btn.clicked.connect(self.refresh_kpis)
        root.addWidget(self.refresh_btn)
        self.refresh_kpis()

    def refresh_kpis(self) -> None:
        """Actualiza todas las tarjetas consultando a SavingsViewModel."""
        data = self._viewmodel.get_kpi_cards_data()
        for key, card in self._cards.items():
            card.set_value(data.get(key, "--"))
