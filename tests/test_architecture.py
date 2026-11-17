"""Suite automatizada de verificación AST para Clean Architecture y regla Anti-Bloat."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.arch_helpers import (
    FORBIDDEN_NAMES,
    MAX_LINES,
    SCRIPTS_DIR,
    SRC_DIR,
    TESTS_DIR,
    assert_ring_isolation,
    extract_imports,
    iter_python_files,
)


def test_init_files_are_zero_bytes() -> None:
    """Todos los __init__.py bajo src/ y tests/ deben medir exactamente 0 bytes."""
    for root in (SRC_DIR, TESTS_DIR):
        for init_file in root.rglob("__init__.py"):
            assert init_file.stat().st_size == 0, f"{init_file} no mide 0 bytes"


def test_anti_bloat_and_no_relative_imports() -> None:
    """Máximo 60 líneas por archivo, sin archivos acumuladores ni imports relativos."""
    for py_file in iter_python_files(SRC_DIR) + iter_python_files(SCRIPTS_DIR):
        assert py_file.name not in FORBIDDEN_NAMES, f"Archivo prohibido: {py_file}"
        if py_file.name == "__init__.py":
            continue
        lines = py_file.read_text(encoding="utf-8").splitlines()
        assert len(lines) <= MAX_LINES, (
            f"{py_file} tiene {len(lines)} líneas (> {MAX_LINES})"
        )
        _, levels = extract_imports(py_file)
        assert all(lvl == 0 for lvl in levels), f"Import relativo en {py_file}"


def test_clean_architecture_ring_boundaries() -> None:
    """Respeta las fronteras de los 4 anillos de Clean Architecture."""
    for py_file in iter_python_files(SRC_DIR):
        rel = py_file.relative_to(SRC_DIR)
        ring = rel.parts[0] if len(rel.parts) > 1 else "root"
        modules, _ = extract_imports(py_file)
        roots = {mod.split(".")[0] for mod in modules}
        assert_ring_isolation(ring, py_file, modules, roots)


if __name__ == "__main__":
    test_init_files_are_zero_bytes()
    test_anti_bloat_and_no_relative_imports()
    test_clean_architecture_ring_boundaries()
    print("ARCHITECTURE GAUNTLET OK")
