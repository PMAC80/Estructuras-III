import pytest

from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.excepciones import ErrorConflicto
from src.models.estados import ROL_CLIENTE, ROL_REPRESENTANTE
from src.models.usuario import Usuario

CLAVE = "ClaveSegura123!"


def test_insertarYBuscarUsuario(db_temporal):
    repositorio = RepositorioUsuario(db_temporal)
    usuario = Usuario.crear(
        None,
        "Ana",
        "Ana@Example.com",
        CLAVE,
        ROL_CLIENTE,
    )

    id_usuario = repositorio.insertar(usuario)

    assert id_usuario == 1
    recuperado = repositorio.buscarPorEmail("ana@example.com")
    assert recuperado.idUsuario == id_usuario
    assert recuperado.email == "ana@example.com"
    assert recuperado.activo is True
    assert repositorio.buscarPorId(id_usuario).nombre == "Ana"


def test_buscarUsuarioInexistenteDevuelveNone(db_temporal):
    repositorio = RepositorioUsuario(db_temporal)

    assert repositorio.buscarPorId(999) is None
    assert repositorio.buscarPorEmail("nadie@example.com") is None


def test_rechazaEmailDuplicado(db_temporal):
    repositorio = RepositorioUsuario(db_temporal)
    repositorio.insertar(
        Usuario.crear(None, "Ana", "ana@example.com", CLAVE, ROL_CLIENTE)
    )

    with pytest.raises(ErrorConflicto):
        repositorio.insertar(
            Usuario.crear(None, "Otra", "ana@example.com", CLAVE, ROL_CLIENTE)
        )


def test_listarActivosYActualizarEstado(db_temporal):
    repositorio = RepositorioUsuario(db_temporal)
    id_ana = repositorio.insertar(
        Usuario.crear(None, "Ana", "ana@example.com", CLAVE, ROL_CLIENTE)
    )
    id_luis = repositorio.insertar(
        Usuario.crear(
            None,
            "Luis",
            "luis@example.com",
            CLAVE,
            ROL_REPRESENTANTE,
            activo=False,
        )
    )

    assert [usuario.idUsuario for usuario in repositorio.listarActivos()] == [id_ana]
    assert repositorio.buscarPorId(id_luis).activo is False

    repositorio.actualizarActivo(id_luis, True)

    assert repositorio.buscarPorId(id_luis).activo is True
    assert len(repositorio.listarActivos()) == 2
