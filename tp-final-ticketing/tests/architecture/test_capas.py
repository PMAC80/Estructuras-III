import ast
from pathlib import Path

CAPAS = {
    "models": {"models", "excepciones"},
    "db": {"db", "models", "excepciones"},
    "controller": {"controller", "db", "models", "excepciones"},
    "gui": {"gui", "controller", "models", "excepciones"},
}


def _resolverModulo(archivo, nodo):
    if isinstance(nodo, ast.Import):
        return [alias.name for alias in nodo.names]
    if nodo.level == 0:
        return [nodo.module] if nodo.module else []

    paquete = ["src", *archivo.parts[:-1]]
    base = paquete[: len(paquete) - nodo.level]
    if nodo.module:
        base.extend(nodo.module.split("."))
    return [".".join(base)]


def _estaPermitido(modulo, capa):
    if not modulo.startswith("src"):
        return True
    if modulo == "src.excepciones":
        return True
    return any(
        modulo == f"src.{permitida}"
        or modulo.startswith(f"src.{permitida}.")
        for permitida in CAPAS[capa]
    )


def buscarInfracciones(raiz):
    raiz = Path(raiz)
    infracciones = []
    for archivo in sorted(raiz.rglob("*.py")):
        relativo = archivo.relative_to(raiz)
        if len(relativo.parts) < 2:
            continue
        capa = relativo.parts[0]
        if capa not in CAPAS:
            continue

        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, (ast.Import, ast.ImportFrom)):
                continue
            for modulo in _resolverModulo(relativo, nodo):
                if modulo and not _estaPermitido(modulo, capa):
                    infracciones.append(
                        (
                            str(archivo),
                            nodo.lineno,
                            capa,
                            modulo,
                        )
                    )
    return infracciones


def test_no_hay_imports_prohibidos_entre_capas():
    raiz = Path(__file__).parents[2] / "src"

    assert buscarInfracciones(raiz) == []


def test_detector_reporta_un_import_prohibido(tmp_path):
    raiz = tmp_path / "src"
    archivo = raiz / "models" / "malo.py"
    archivo.parent.mkdir(parents=True)
    archivo.write_text(
        "from src.gui.gui import GUI\n",
        encoding="utf-8",
    )

    infracciones = buscarInfracciones(raiz)

    assert len(infracciones) == 1
    assert infracciones[0][2] == "models"
    assert infracciones[0][3] == "src.gui.gui"
