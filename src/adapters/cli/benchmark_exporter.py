"""Exportador de telemetría de benchmarks a archivos JSON para el CLI."""

import json
from pathlib import Path
from typing import Any


def export_benchmark_telemetry(data: dict[str, Any], export_path: str | Path) -> str:
    """Serializa la telemetría del benchmark a JSON y retorna la ruta absoluta resuelta."""
    path = Path(export_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return str(path.resolve())
