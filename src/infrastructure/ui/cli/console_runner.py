"""Driver de consola interactivo y runner de simulación benchmark para Konsole."""

from collections.abc import Callable

from src.adapters.cli.cli_controller import CliController
from src.infrastructure.ui.cli.readline_completer import setup_cli_autocomplete

MENU_HEADER = (
    "\n=== AGRO-PREDICT 2026 | CONSOLA DE DIAGNOSTICO (MVP NIVEL 1) ===\n"
    "[1] Estado de sectores e ITH actual\n"
    "[2] Alternar ocupacion de sector (corral_espera / comederos / sombras)\n"
    "[3] Ejecutar prediccion ML (+1h) y ordenes de enfriamiento\n"
    "[4] Consultar balance de ahorro (Agua / kWh / CO2e / Leche SIGLeA)\n"
    "[5] Ejecutar Benchmark completo de 24h\n"
    "[0] Salir"
)


def run_cli(
    controller: CliController,
    benchmark_mode: bool = False,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int:
    """Inicia la interfaz de línea de comandos o ejecuta la corrida benchmark."""
    if benchmark_mode:
        output_fn(controller.handle_benchmark())
        return 0

    setup_cli_autocomplete()
    while True:
        output_fn(MENU_HEADER)
        choice = input_fn("Seleccione opcion > ").strip()
        if choice == "0":
            return 0
        if choice == "1":
            output_fn(controller.handle_status())
        elif choice == "2":
            sec = input_fn("ID del sector (ej. corral_espera) > ").strip()
            occ = input_fn("Ocupado? (true/false) > ").strip().lower() == "true"
            output_fn(controller.handle_occupy(sec, occ))
        elif choice == "3":
            output_fn(controller.handle_predict())
        elif choice == "4":
            output_fn(controller.handle_savings())
        elif choice == "5":
            output_fn(controller.handle_benchmark())
        else:
            output_fn("Opcion no reconocida.")
