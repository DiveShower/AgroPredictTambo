"""Adaptador de control físico de relés por puerto serie (Arduino / USB)."""

import os
from typing import Any, Optional

import serial

from src.domain.ports.hardware_controller_port import IHardwareController
from src.infrastructure.hardware.mock_relay_adapter import (
    MAX_WATER_WATCHDOG_SECONDS,
)


class SerialRelayAdapter(IHardwareController):
    """Comanda electroválvulas y ventiladores vía puerto serie con Watchdog 60s."""

    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: Optional[int] = None,
    ) -> None:
        self._port = port or os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
        self._baud = baudrate or int(os.getenv("SERIAL_BAUDRATE", "9600"))
        self._serial: Optional[Any] = self._open_port()

    def _open_port(self) -> Optional[Any]:
        try:
            return serial.Serial(self._port, self._baud, timeout=1)
        except Exception:
            return None

    def _send_command(self, cmd: str) -> bool:
        if self._serial is None:
            return False
        try:
            self._serial.write(f"{cmd}\n".encode("ascii"))
            return True
        except Exception:
            return False

    def activate_water_valve(self, sector_id: str, duration_seconds: int) -> bool:
        """Envía trama de apertura de agua acotada a máximo 60 segundos."""
        if duration_seconds <= 0:
            return False
        clamped = min(MAX_WATER_WATCHDOG_SECONDS, duration_seconds)
        return self._send_command(f"WATER:{sector_id}:{clamped}")

    def activate_ventilation_fan(
        self, sector_id: str, duration_seconds: int
    ) -> bool:
        """Envía trama de encendido de ventiladores forzados del sector."""
        if duration_seconds <= 0:
            return False
        return self._send_command(f"FAN:{sector_id}:{duration_seconds}")

    def emergency_shutoff_all(self) -> None:
        """Envía trama de corte total de emergencia a la placa de relés."""
        self._send_command("SHUTOFF:ALL:0")
