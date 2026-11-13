import re
from pathlib import Path

RAIZ = Path(__file__).parents[2]
MATRIZ = RAIZ / "specs" / "001-ticketing" / "aceptacion.md"
REFERENCIA = re.compile(r"(tests/[\w/]+\.py)::(\w+)")


def test_matrizCubreRf1Rf10ConTestsExistentes():
    texto = MATRIZ.read_text(encoding="utf-8")

    for numero in range(1, 11):
        assert f"RF{numero}" in texto

    referencias = REFERENCIA.findall(texto)
    assert referencias

    for archivo, nombre in referencias:
        ruta = RAIZ / archivo
        assert ruta.exists(), archivo
        fuente = ruta.read_text(encoding="utf-8")
        assert f"def {nombre}(" in fuente, f"{archivo}::{nombre}"
