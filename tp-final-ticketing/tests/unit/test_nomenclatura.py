import ast
import re
from pathlib import Path

from src.gui import menus

CLASES = re.compile(r"^[A-Z][A-Za-z0-9]*$")
METODOS = re.compile(r"^_?[a-z][A-Za-z0-9]*$")
PALABRAS_INGLESAS = {
    "invalid",
    "required",
    "not found",
    "success",
    "welcome",
    "logout",
    "login",
    "sign in",
}


def _definiciones(raiz):
    for archivo in Path(raiz).rglob("*.py"):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ClassDef):
                yield archivo, "clase", nodo.name
            elif isinstance(
                nodo,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                if nodo.name.startswith("__") and nodo.name.endswith(
                    "__"
                ):
                    continue
                yield archivo, "método", nodo.name


def test_clasesYMetodosRespetanLaNomenclaturaDelProyecto():
    raiz = Path(__file__).parents[2] / "src"
    invalidos = []

    for archivo, tipo, nombre in _definiciones(raiz):
        patron = CLASES if tipo == "clase" else METODOS
        if not patron.fullmatch(nombre):
            invalidos.append(f"{archivo}: {tipo} {nombre}")

    assert invalidos == []


def test_menusYTextosDeInterfazEstanEnEspanol():
    etiquetas = [
        *menus.MENU_INICIAL.values(),
        *menus.MENU_CLIENTE.values(),
        *menus.MENU_REPRESENTANTE.values(),
    ]

    assert "Registrarse" in etiquetas
    assert "Iniciar sesión" in etiquetas
    assert "Cerrar sesión" in etiquetas
    assert all(
        palabra not in etiqueta.lower()
        for etiqueta in etiquetas
        for palabra in PALABRAS_INGLESAS
    )


def test_mensajesDeLaInterfazNoUsanTerminosEnIngles():
    raiz = Path(__file__).parents[2] / "src" / "gui"
    textos = []

    for archivo in raiz.glob("*.py"):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        textos.extend(
            nodo.value
            for nodo in ast.walk(arbol)
            if isinstance(nodo, ast.Constant)
            and isinstance(nodo.value, str)
        )

    assert any("sesión" in texto for texto in textos)
    assert all(
        palabra not in texto.lower()
        for texto in textos
        for palabra in PALABRAS_INGLESAS
    )
