"""Pruebas unitarias para el exportador de telemetría de benchmarks del CLI."""

import json
from pathlib import Path
from typing import Any

from src.adapters.cli.benchmark_exporter import export_benchmark_telemetry


def test_export_benchmark_telemetry_creates_json_file(tmp_path: Path) -> None:
    """Verifica que export_benchmark_telemetry cree el JSON y retorne su ruta resuelta."""
    data: dict[str, Any] = {"status": "OK", "lat": -31.25, "orders": [1, 2]}
    out_path = tmp_path / "telemetry" / "bench.json"

    res = export_benchmark_telemetry(data, out_path)

    assert out_path.exists()
    assert res == str(out_path.resolve())
    assert json.loads(out_path.read_text(encoding="utf-8")) == data
