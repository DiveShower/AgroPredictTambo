"""Autocompletado por tabulación en consola CLI mediante readline."""

SECTORS_AND_COMMANDS: tuple[str, ...] = (
    "corral_espera",
    "comederos",
    "sombras",
    "true",
    "false",
)


def get_completions(
    text: str,
    state: int,
    candidates: tuple[str, ...] = SECTORS_AND_COMMANDS,
) -> str | None:
    """Retorna la coincidencia en la posición state para el prefijo text."""
    matches = [c for c in candidates if c.startswith(text)]
    if 0 <= state < len(matches):
        return matches[state]
    return None


def setup_cli_autocomplete(
    words: tuple[str, ...] = SECTORS_AND_COMMANDS,
) -> None:
    """Configura el autocompletado Tab con readline si está disponible."""
    try:
        import readline
    except ImportError:
        return

    readline.set_completer(lambda t, s: get_completions(t, s, words))
    readline.parse_and_bind("tab: complete")
