"""Suite automatizada de verificación AST para Clean Architecture y regla Anti-Bloat."""

import ast
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
SCRIPTS_DIR = ROOT_DIR / "data" / "scripts"
MAX_LINES = 60
FORBIDDEN_NAMES = {"entities.py", "ports.py", "handlers.py", "views.py", "utils.py"}
EXTERNAL_FORBIDDEN = {
    "PyQt6",
    "sklearn",
    "pandas",
    "numpy",
    "requests",
    "sqlite3",
    "fpdf",
    "telegram",
    "serial",
    "matplotlib",
    "qrcode",
    "joblib",
}


def _iter_python_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.rglob("*.py") if "__pycache__" not in p.parts)


def _extract_imports(path: Path) -> tuple[list[str], list[int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: list[str] = []
    relative_levels: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            relative_levels.append(node.level)
            if node.module:
                modules.append(node.module)
    return modules, relative_levels


def test_init_files_are_zero_bytes() -> None:
    """Todos los __init__.py bajo src/ deben medir exactamente 0 bytes."""
    for init_file in SRC_DIR.rglob("__init__.py"):
        assert init_file.stat().st_size == 0, f"{init_file} no mide 0 bytes"


def test_anti_bloat_and_no_relative_imports() -> None:
    """Máximo 120 líneas por archivo, sin archivos acumuladores ni imports relativos."""
    for py_file in _iter_python_files(SRC_DIR) + _iter_python_files(SCRIPTS_DIR):
        assert py_file.name not in FORBIDDEN_NAMES, f"Archivo prohibido: {py_file}"
        if py_file.name == "__init__.py":
            continue
        lines = py_file.read_text(encoding="utf-8").splitlines()
        assert len(lines) <= MAX_LINES, (
            f"{py_file} tiene {len(lines)} líneas (> {MAX_LINES})"
        )
        _, levels = _extract_imports(py_file)
        assert all(lvl == 0 for lvl in levels), f"Import relativo en {py_file}"


def test_clean_architecture_ring_boundaries() -> None:
    """Respeta las fronteras de los 4 anillos: domain -> application -> adapters -> infrastructure."""
    for py_file in _iter_python_files(SRC_DIR):
        rel = py_file.relative_to(SRC_DIR)
        ring = rel.parts[0] if len(rel.parts) > 1 else "root"
        modules, _ = _extract_imports(py_file)
        roots = {mod.split(".")[0] for mod in modules}
        assert "data" not in roots, f"Import prohibido de data.* en src: {py_file}"
        if ring == "domain":
            assert not (roots & EXTERNAL_FORBIDDEN), (
                f"Import externo en domain: {py_file}"
            )
            for mod in modules:
                assert not mod.startswith(
                    ("src.application", "src.adapters", "src.infrastructure")
                ), f"Violación de anillo en {py_file}: {mod}"
        elif ring == "application":
            assert not (roots & EXTERNAL_FORBIDDEN), (
                f"Import externo en application: {py_file}"
            )
            for mod in modules:
                assert not mod.startswith(("src.adapters", "src.infrastructure")), (
                    f"Violación de anillo en {py_file}: {mod}"
                )
        elif ring == "adapters":
            assert not (roots & EXTERNAL_FORBIDDEN), (
                f"Import pesado en adapters: {py_file}"
            )
            for mod in modules:
                assert not mod.startswith("src.infrastructure"), (
                    f"Violación de anillo en {py_file}: {mod}"
                )


if __name__ == "__main__":
    test_init_files_are_zero_bytes()
    test_anti_bloat_and_no_relative_imports()
    test_clean_architecture_ring_boundaries()
    print("ARCHITECTURE GAUNTLET OK")
