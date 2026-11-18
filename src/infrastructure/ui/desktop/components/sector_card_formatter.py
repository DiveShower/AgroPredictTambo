"""Funciones auxiliares de formateo para etiquetas de SectorCardWidget."""


def format_water_label(allows_water: bool, seconds: int) -> str:
    """Formatea la etiqueta de estado de aspersión según permiso y tiempo restante."""
    if not allows_water:
        return "ASPERSION BLOQUEADA (Anti-Mastitis)"
    if seconds > 0:
        return f"Bomba Aspersion: ACTIVA ({seconds}s)"
    return "Bomba Aspersion: OFF"


def format_fan_label(seconds: int) -> str:
    """Formatea la etiqueta de estado de ventilación según tiempo restante."""
    if seconds > 0:
        return f"Ventiladores: ACTIVOS ({seconds}s)"
    return "Ventiladores: OFF"
