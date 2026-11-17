"""Prueba E2E de la ejecución CLI --benchmark desde el punto de entrada main()."""

import pytest

from src.main import main


@pytest.mark.e2e
def test_e2e_cli_benchmark_outputs_sectors_thi_and_esg_metrics(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Valida retorno 0, los 3 sectores, reporte ITH y métricas ESG en salida."""
    rc = main(["--cli", "--benchmark"])

    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip() != ""

    assert "=== ESTADO OPERATIVO DEL TAMBO (SECTORES) ===" in out
    for sector in ("corral_espera", "comederos", "sombras"):
        assert sector in out

    assert "=== PREDICCION BIOCLIMATICA Y ORDENES DE ENFRIAMIENTO ===" in out
    for token in ("Actual:", "Proyectado:", "ITH"):
        assert token in out

    assert "=== BALANCE DE AHORRO Y SUSTENTABILIDAD ESG" in out
    for token in (
        "Agua Ahorrada",
        "Energia Electrica Ahorrada",
        "Huella de Carbono Evitada",
        "Leche Protegida",
        " L (",
        " kWh",
        " kg CO2e",
        " L/dia",
    ):
        assert token in out
