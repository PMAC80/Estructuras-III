import sqlite3

import pytest

from src.db.conexion import abrirConexion, usarConexion


def test_abrirConexion_configuraRowFactoryYForeignKeys(tmp_path):
    conexion = abrirConexion(tmp_path / "sub" / "ticketing.db")
    try:
        assert conexion.row_factory is sqlite3.Row
        assert conexion.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        conexion.close()


def test_abrirConexion_creaDirectorioPadre(tmp_path):
    ruta = tmp_path / "datos" / "ticketing.db"

    conexion = abrirConexion(ruta)
    conexion.close()

    assert ruta.parent.is_dir()


def test_usarConexion_cierraAlSalir(tmp_path):
    with usarConexion(tmp_path / "ticketing.db") as conexion:
        conexion.execute("CREATE TABLE prueba (id INTEGER)")

    with pytest.raises(sqlite3.ProgrammingError):
        conexion.execute("SELECT 1")
