"""Pruebas unitarias para el autocompletado CLI mediante readline."""

from src.infrastructure.ui.cli.readline_completer import (
    get_completions,
    setup_cli_autocomplete,
)


def test_get_completions_matching() -> None:
    """Verifica coincidencias por prefijo e índice de estado en get_completions."""
    assert get_completions("corr", 0) == "corral_espera"
    assert get_completions("corr", 1) is None
    assert get_completions("som", 0) == "sombras"
    assert get_completions("tr", 0) == "true"
    assert get_completions("xyz", 0) is None


def test_setup_cli_autocomplete_runs() -> None:
    """Comprueba que setup_cli_autocomplete se ejecuta sin lanzar excepciones."""
    setup_cli_autocomplete()
