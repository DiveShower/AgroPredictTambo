"""Pruebas unitarias para el cliente HTTP síncrono con reintentos."""

from typing import Any

import pytest
import requests

from src.infrastructure.weather_api.http_retry_client import get_with_retry


def test_retry_success_after_failure(mocker: Any) -> None:
    """Reintenta tras fallo de red y retorna el JSON en el segundo intento."""
    payload: dict[str, Any] = {"ok": True, "temp": 28.5}
    mock_resp = mocker.Mock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = payload

    mock_sleep = mocker.patch("time.sleep")
    mock_get = mocker.patch(
        "requests.get",
        side_effect=[requests.RequestException("timeout"), mock_resp],
    )

    result = get_with_retry("https://api.example.com/weather", {"lat": -31.25})

    assert result == payload
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(0.5)


def test_retry_exhaustion_raises_error(mocker: Any) -> None:
    """Agota los 3 reintentos y propaga RequestException."""
    mock_sleep = mocker.patch("time.sleep")
    mock_get = mocker.patch(
        "requests.get",
        side_effect=requests.RequestException("network down"),
    )

    with pytest.raises(requests.RequestException, match="network down"):
        get_with_retry("https://api.example.com/weather", {"lat": -31.25})

    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2
