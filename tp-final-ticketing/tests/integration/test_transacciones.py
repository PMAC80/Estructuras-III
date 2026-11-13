import pytest

from src.db.conexion import abrirConexion, transaccion
from src.db.esquema import crearEsquema
from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.models.estados import ROL_CLIENTE
from src.models.usuario import Usuario

CLAVE = "ClaveSegura123!"


def _usuario(email="ana@example.com"):
    return Usuario.crear(None, "Ana", email, CLAVE, ROL_CLIENTE)


def _contarUsuarios(conexion):
    return conexion.execute("SELECT COUNT(*) FROM usuario").fetchone()[0]


def test_transaccionConfirmaAlSalir(tmp_path):
    ruta = tmp_path / "ticketing.db"
    conexion = abrirConexion(ruta)
    crearEsquema(conexion)

    with transaccion(conexion):
        RepositorioUsuario(conexion).insertar(_usuario())

    conexion.close()

    conexion_reabierta = abrirConexion(ruta)
    try:
        assert _contarUsuarios(conexion_reabierta) == 1
    finally:
        conexion_reabierta.close()


def test_transaccionRevierteSiHayExcepcion(db_temporal):
    with pytest.raises(ValueError, match="fallo simulado"):
        with transaccion(db_temporal):
            RepositorioUsuario(db_temporal).insertar(_usuario())
            raise ValueError("fallo simulado")

    assert _contarUsuarios(db_temporal) == 0


def test_repositorioNoConfirmaPorSiSolo(tmp_path):
    ruta = tmp_path / "ticketing.db"
    conexion = abrirConexion(ruta)
    crearEsquema(conexion)

    RepositorioUsuario(conexion).insertar(_usuario())
    conexion.close()

    conexion_reabierta = abrirConexion(ruta)
    try:
        assert _contarUsuarios(conexion_reabierta) == 0
    finally:
        conexion_reabierta.close()
