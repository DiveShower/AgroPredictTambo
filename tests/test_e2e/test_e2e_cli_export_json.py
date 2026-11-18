"""Prueba E2E de exportación de telemetría JSON mediante --export-json."""

import json
from pathlib import Path

import pytest

from src.main import main


@pytest.mark.e2e
def test_e2e_cli_benchmark_export_json_creates_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Valida que --cli --benchmark --export-json genere el JSON con claves esperadas."""
    out_file = tmp_path / "telemetry_benchmark.json"
    rc = main(["--cli", "--benchmark", "--export-json", str(out_file)])

    assert rc == 0
    assert out_file.exists() is True

    out = capsys.readouterr().out
    assert out.strip() != ""

    data: object = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    for key in ("status", "prediction", "savings", "lat", "lon"):
        assert key in data
