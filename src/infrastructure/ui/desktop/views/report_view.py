"""Vista de previsualización y exportación del Reporte de Sustentabilidad PDF."""

from typing import Optional

from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from src.adapters.desktop.viewmodels.savings_viewmodel import SavingsViewModel


class ReportView(QWidget):
    """Pestaña 5: Permite previsualizar y exportar el informe auditado en PDF."""

    def __init__(
        self,
        viewmodel: SavingsViewModel,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._viewmodel = viewmodel
        layout = QVBoxLayout(self)

        self.title_lbl = QLabel(
            "Auditoría ESG — Reporte de Sustentabilidad Nestlé Conecta (PDF)"
        )
        self.title_lbl.setObjectName("HeaderTitle")
        self.preview_lbl = QLabel()
        self.status_lbl = QLabel("Listo para exportar a PDF.")
        self.export_btn = QPushButton("Exportar Reporte PDF Ahora")
        self.export_btn.clicked.connect(self.export_pdf)

        for w in (self.title_lbl, self.preview_lbl, self.export_btn, self.status_lbl):
            layout.addWidget(w)
        self.refresh_preview()

    def refresh_preview(self) -> None:
        """Actualiza el resumen textual desde SavingsViewModel."""
        kpis = self._viewmodel.get_kpi_cards_data()
        self.preview_lbl.setText(
            f"• Agua Ahorrada (Software): {kpis['water_software']}\n"
            f"• Ahorro Hidráulico Combinado: {kpis['water_combined']}\n"
            f"• Energía Eléctrica Ahorrada: {kpis['energy_kwh']}\n"
            f"• Huella de Carbono (CAMMESA): {kpis['carbon_cammesa']}\n"
            f"• Leche Defendida (SIGLeA): {kpis['milk_siglea']} ({kpis['economic_ars']})"
        )

    def export_pdf(self) -> str:
        """Dispara la generación del PDF mediante el ViewModel y muestra la ruta."""
        path = self._viewmodel.export_sustainability_pdf()
        self.status_lbl.setText(f"PDF generado exitosamente en: {path}")
        return path
