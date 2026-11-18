"""Cliente HTTP síncrono con reintentos y backoff exponencial."""

import time
from typing import Any

import requests


def get_with_retry(
    url: str,
    params: dict[str, Any],
    timeout: int = 8,
    max_retries: int = 3,
    backoff_factor: float = 0.5,
) -> dict[str, Any]:
    """Ejecuta GET con reintentos ante fallos de red, HTTP o JSON inválido."""
    if max_retries < 1:
        raise ValueError("max_retries debe ser al menos 1")

    delay = backoff_factor
    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return dict(response.json())
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2.0

    if last_error is not None:
        raise last_error
    raise RuntimeError("Reintentos agotados sin excepción registrada")
