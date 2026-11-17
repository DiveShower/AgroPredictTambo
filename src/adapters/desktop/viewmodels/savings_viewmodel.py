"""ViewModel de retorno financiero (SIGLeA), ahorro hídrico/energético y PDF ESG."""

from typing import Optional

from src.application.dtos.calculate_savings_request_dto import (
    CalculateSavingsRequestDTO,
)
from src.application.use_cases.calculate_savings_uc import (
    CalculateSavingsUseCase,
)
from src.application.use_cases.generate_sustainability_report_uc import (
    GenerateSustainabilityReportUseCase,
)


class SavingsViewModel:
    """Formatea métricas de impacto económico y ambiental para la interfaz gráfica."""

    def __init__(
        self,
        savings_uc: CalculateSavingsUseCase,
        report_uc: Optional[GenerateSustainabilityReportUseCase] = None,
    ) -> None:
        self._savings_uc = savings_uc
        self._report_uc = report_uc

    def get_kpi_cards_data(
        self,
        active_hours: float = 3.5,
        cow_count: int = 100,
        milk_price_ars: float = 430.0,
    ) -> dict[str, str]:
        """Devuelve textos formateados de agua, kWh, CO2e y pesos ARS (SIGLeA)."""
        req = CalculateSavingsRequestDTO(
            predictive_active_hours=active_hours,
            cow_count=cow_count,
            milk_price_ars=milk_price_ars,
        )
        res = self._savings_uc.execute(req)
        s, c, e = res.savings, res.carbon_footprint, res.economic_impact
        return {
            "water_software": f"{s.water_saved_liters:.1f} L/día ({s.water_saved_pct:.1f}%)",
            "water_combined": f"{s.combined_water_saved_pct:.1f}% (vs pico 4.9 L/min)",
            "energy_kwh": f"{s.energy_saved_kwh:.2f} kWh/día ({s.energy_saved_pct:.1f}%)",
            "carbon_cammesa": f"{c.co2_avoided_kg:.2f} kg CO2e (Factor {c.emission_factor_kg_per_kwh})",
            "milk_siglea": f"{e.milk_protected_liters:.1f} L/día ({e.cow_count} vacas)",
            "economic_ars": f"${e.economic_return_ars:,.2f} ARS/día",
        }

    def export_sustainability_pdf(
        self,
        farm_name: str = "Tambo San José - Nestlé Conecta",
        output_path: str = "data/cache/reporte_sustentabilidad_nestle.pdf",
    ) -> str:
        """Solicita la exportación del informe auditado en PDF y devuelve la ruta."""
        if not self._report_uc:
            return ""
        dto = self._report_uc.execute(farm_name=farm_name, output_path=output_path)
        return dto.pdf_file_path or output_path
