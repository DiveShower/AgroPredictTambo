"""Grupo de controles deslizantes bioclimáticos para simulación interactiva."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFormLayout, QSlider, QWidget


def _make_slider(min_v: int, max_v: int, val: int) -> QSlider:
    """Crea un slider horizontal configurado con rango y valor inicial."""
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(min_v, max_v)
    slider.setValue(val)
    return slider


class SimulationSliderGroup(QWidget):
    """Formulario de sliders climáticos con emisión unificada de cambios."""

    values_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Inicializa los sliders bioclimáticos y los dispone en QFormLayout."""
        super().__init__(parent)
        self.temp_slider = _make_slider(15, 45, 34)
        self.rh_slider = _make_slider(20, 95, 68)
        self.wind_slider = _make_slider(0, 40, 6)
        self.rad_slider = _make_slider(0, 1000, 820)

        form = QFormLayout(self)
        for label, sld in (
            ("Temperatura (15 a 45 C):", self.temp_slider),
            ("Humedad Relativa (20 a 95 %):", self.rh_slider),
            ("Velocidad de Viento (0 a 40 km/h):", self.wind_slider),
            ("Radiacion Solar (0 a 1000 W/m2):", self.rad_slider),
        ):
            sld.valueChanged.connect(self.values_changed.emit)
            form.addRow(label, sld)

    def current_values(self) -> tuple[float, float, float, float]:
        """Devuelve (temperatura, humedad, viento, radiacion) como floats."""
        return (
            float(self.temp_slider.value()),
            float(self.rh_slider.value()),
            float(self.wind_slider.value()),
            float(self.rad_slider.value()),
        )
