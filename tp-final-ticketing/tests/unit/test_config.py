from pathlib import Path

from src.config import RUTA_POR_DEFECTO, VARIABLE_ENTORNO, resolverRutaBaseDatos


def test_resolverRutaBaseDatos_usaValorPorDefecto():
    ruta = resolverRutaBaseDatos(entorno={})

    assert ruta == Path(RUTA_POR_DEFECTO)


def test_resolverRutaBaseDatos_respetaVariableDeEntorno():
    ruta = resolverRutaBaseDatos(entorno={VARIABLE_ENTORNO: "datos/prueba.db"})

    assert ruta == Path("datos/prueba.db")


def test_resolverRutaBaseDatos_ignoraVariableVacia():
    ruta = resolverRutaBaseDatos(entorno={VARIABLE_ENTORNO: ""})

    assert ruta == Path(RUTA_POR_DEFECTO)
