"""Helpers AST y constantes para la verificación arquitectónica."""

import ast
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
TESTS_DIR = ROOT_DIR / "tests"
SCRIPTS_DIR = ROOT_DIR / "data" / "scripts"
MAX_LINES = 60
FORBIDDEN_NAMES = {"entities.py", "ports.py", "handlers.py", "views.py", "utils.py"}
EXTERNAL_FORBIDDEN = {"PyQt6", "sklearn", "pandas", "numpy", "requests", "sqlite3"}
EXTERNAL_FORBIDDEN |= {"fpdf", "telegram", "serial", "matplotlib", "qrcode", "joblib"}
RING_FORBIDDEN_PREFIXES: dict[str, tuple[str, ...]] = {
    "domain": ("src.application", "src.adapters", "src.infrastructure"),
    "application": ("src.adapters", "src.infrastructure"),
    "adapters": ("src.infrastructure",),
}


def iter_python_files(directory: Path) -> list[Path]:
    """Retorna archivos .py ordenados dentro de un directorio sin __pycache__."""
    if not directory.exists():
        return []
    return sorted(p for p in directory.rglob("*.py") if "__pycache__" not in p.parts)


def extract_imports(path: Path) -> tuple[list[str], list[int]]:
    """Extrae módulos importados y niveles relativos de un archivo."""
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


def assert_ring_isolation(
    ring: str, py_file: Path, modules: list[str], roots: set[str]
) -> None:
    """Valida aislamiento de anillo y dependencias externas permitidas."""
    assert "data" not in roots, f"Import prohibido de data.* en src: {py_file}"
    if prefixes := RING_FORBIDDEN_PREFIXES.get(ring):
        assert not (roots & EXTERNAL_FORBIDDEN), f"Import externo en {ring}: {py_file}"
        bad = [m for m in modules if m.startswith(prefixes)]
        assert not bad, f"Violación de anillo en {py_file}: {bad[0]}"
