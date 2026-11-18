"""Barra de controles operativos del tablero SCADA con feedback de estado."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class ScadaControlBar(QWidget):
    """Barra inferior con acciones de sincronización climática, demo y emergencia."""

    sync_requested = pyqtSignal()
    demo_heatwave_requested = pyqtSignal()
    emergency_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Inicializa los botones de control y conecta sus señales de clic."""
        super().__init__(parent)
        self.sync_btn = QPushButton("Sincronizar Clima Ahora")
        self.demo_btn = QPushButton("Simular Ola de Calor")
        self.stop_btn = QPushButton("Detencion de Emergencia")
        self.stop_btn.setObjectName("EmergencyBtn")

        self.sync_btn.clicked.connect(self.sync_requested.emit)
        self.demo_btn.clicked.connect(self.demo_heatwave_requested.emit)
        self.stop_btn.clicked.connect(self.emergency_requested.emit)

        layout = QHBoxLayout(self)
        for btn in (self.sync_btn, self.demo_btn, self.stop_btn):
            layout.addWidget(btn)

    def set_sync_busy(self, is_busy: bool) -> None:
        """Deshabilita los botones de sincronización y actualiza el texto mientras sincroniza."""
        self.sync_btn.setEnabled(not is_busy)
        self.demo_btn.setEnabled(not is_busy)
        self.sync_btn.setText(
            "Sincronizando..." if is_busy else "Sincronizar Clima Ahora"
        )
