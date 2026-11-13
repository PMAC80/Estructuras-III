import pytest

from src.db.conexion import abrirConexion
from src.db.esquema import crearEsquema


@pytest.fixture
def db_temporal(tmp_path):
    conexion = abrirConexion(tmp_path / "ticketing_test.db")
    crearEsquema(conexion)
    yield conexion
    conexion.close()
