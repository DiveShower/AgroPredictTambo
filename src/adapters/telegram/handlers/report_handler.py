"""Handler para el comando /reporte del bot de Telegram."""

from src.application.use_cases.generate_sustainability_report_uc import (
    GenerateSustainabilityReportUseCase,
)


class ReportHandler:
    """Gestiona el comando /reporte generando el informe ESG en PDF."""

    def __init__(
        self,
        report_uc: GenerateSustainabilityReportUseCase,
        farm_name: str = "Tambo San José - Nestlé Conecta",
        output_path: str = "data/cache/reporte_sustentabilidad_nestle.pdf",
    ) -> None:
        """Inicializa el handler con el caso de uso y parámetros del reporte."""
        self._report_uc = report_uc
        self._farm_name = farm_name
        self._output_path = output_path

    def handle(self) -> tuple[str, str | None]:
        """Genera el reporte PDF ESG y retorna el resumen junto con la ruta del archivo."""
        dto = self._report_uc.execute(
            farm_name=self._farm_name,
            output_path=self._output_path,
        )
        msg = (
            f"📄 Reporte de Sustentabilidad — {dto.farm_name}\n"
            f"• Agua ahorrada: {dto.savings.water_saved_liters:.2f} L\n"
            f"• Energía ahorrada: {dto.savings.energy_saved_kwh:.2f} kWh\n"
            f"• CO2e evitado: {dto.carbon_footprint.co2_avoided_kg:.2f} kg\n"
            f"• Leche protegida: {dto.economic_impact.milk_protected_liters:.2f} L\n"
            f"• Archivo PDF: {dto.pdf_file_path or 'No generado'}"
        )
        return msg, dto.pdf_file_path
