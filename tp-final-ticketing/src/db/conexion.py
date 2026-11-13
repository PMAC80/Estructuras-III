import sqlite3
from contextlib import contextmanager
from pathlib import Path


def _resolverRuta(ruta) -> str:
    if isinstance(ruta, Path):
        ruta_texto = str(ruta)
    else:
        ruta_texto = str(ruta)

    if ruta_texto == ":memory:":
        return ruta_texto

    ruta_path = Path(ruta_texto)
    if ruta_path.parent != Path("."):
        ruta_path.parent.mkdir(parents=True, exist_ok=True)
    return str(ruta_path)


def abrirConexion(ruta) -> sqlite3.Connection:
    conexion = sqlite3.connect(_resolverRuta(ruta))
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


@contextmanager
def usarConexion(ruta):
    conexion = abrirConexion(ruta)
    try:
        yield conexion
    finally:
        conexion.close()


@contextmanager
def transaccion(conexion):
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
