"""Contrato abstracto para generación de reportes de sustentabilidad ESG."""

from typing import Protocol

from src.domain.value_objects.resource_savings import ResourceSavings


class IReportGenerator(Protocol):
    """Puerto para exportar informes auditables de eficiencia hídrica y energética."""

    def generate_sustainability_pdf(
        self,
        farm_name: str,
        savings: ResourceSavings,
        output_path: str,
    ) -> str:
        """Genera el reporte en PDF y devuelve la ruta del archivo generado."""
        ...
