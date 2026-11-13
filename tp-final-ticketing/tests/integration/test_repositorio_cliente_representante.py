import pytest

from src.db.repositorios.repositorio_cliente import RepositorioCliente
from src.db.repositorios.repositorio_representante import (
    RepositorioRepresentante,
)
from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.excepciones import ErrorConflicto, ErrorValidacion
from src.models.cliente import Cliente
from src.models.estados import ROL_CLIENTE, ROL_REPRESENTANTE
from src.models.representante import Representante
from src.models.seguridad import generarHash
from src.models.usuario import Usuario

CLAVE = "ClaveSegura123!"
HASH = generarHash(CLAVE)


def _crear_cliente(conexion):
    repositorio = RepositorioUsuario(conexion)
    usuario = Usuario.crear(
        None,
        "Ana",
        "ana@example.com",
        CLAVE,
        ROL_CLIENTE,
    )
    id_usuario = repositorio.insertar(usuario)
    return Cliente(
        id_usuario,
        "Ana",
        "ana@example.com",
        usuario.contrasenaHash,
        empresa="ACME",
        telefono="123456",
    )


def _crear_representante(
    conexion,
    email="luis@example.com",
    legajo="REP-001",
    activo=True,
):
    repositorio = RepositorioUsuario(conexion)
    usuario = Usuario.crear(
        None,
        "Luis",
        email,
        CLAVE,
        ROL_REPRESENTANTE,
        activo=activo,
    )
    id_usuario = repositorio.insertar(usuario)
    return Representante(
        id_usuario,
        "Luis",
        email,
        usuario.contrasenaHash,
        legajo=legajo,
        activo=activo,
    )


def test_insertarYBuscarCliente(db_temporal):
    cliente = _crear_cliente(db_temporal)
    repositorio = RepositorioCliente(db_temporal)

    id_usuario = repositorio.insertar(cliente)
    recuperado = repositorio.buscarPorId(id_usuario)

    assert isinstance(recuperado, Cliente)
    assert recuperado.idUsuario == id_usuario
    assert recuperado.rol == ROL_CLIENTE
    assert recuperado.empresa == "ACME"
    assert recuperado.telefono == "123456"
    assert recuperado.activo is True


def test_clienteSinUsuarioAsociado_lanzaErrorValidacion(db_temporal):
    cliente = Cliente(
        None,
        "Ana",
        "ana@example.com",
        HASH,
    )
    repositorio = RepositorioCliente(db_temporal)

    with pytest.raises(ErrorValidacion):
        repositorio.insertar(cliente)


def test_insertarBuscarYListarRepresentantesActivos(db_temporal):
    representante_activo = _crear_representante(
        db_temporal,
        email="luis@example.com",
        legajo="REP-001",
    )
    representante_inactivo = _crear_representante(
        db_temporal,
        email="marta@example.com",
        legajo="REP-002",
        activo=False,
    )
    repositorio = RepositorioRepresentante(db_temporal)

    repositorio.insertar(representante_activo)
    repositorio.insertar(representante_inactivo)

    recuperado = repositorio.buscarPorId(representante_inactivo.idUsuario)
    assert isinstance(recuperado, Representante)
    assert recuperado.rol == ROL_REPRESENTANTE
    assert recuperado.legajo == "REP-002"
    assert recuperado.activo is False

    activos = repositorio.listarActivos()
    assert [representante.idUsuario for representante in activos] == [
        representante_activo.idUsuario
    ]
    assert (
        repositorio.buscarPorLegajo("REP-001").idUsuario
        == representante_activo.idUsuario
    )


def test_rechazaLegajoDuplicado(db_temporal):
    primer_representante = _crear_representante(
        db_temporal,
        email="luis@example.com",
        legajo="REP-001",
    )
    segundo_representante = _crear_representante(
        db_temporal,
        email="marta@example.com",
        legajo="REP-001",
    )
    repositorio = RepositorioRepresentante(db_temporal)
    repositorio.insertar(primer_representante)

    with pytest.raises(ErrorConflicto):
        repositorio.insertar(segundo_representante)


def test_representanteSinUsuarioAsociado_lanzaErrorValidacion(db_temporal):
    representante = Representante(
        None,
        "Luis",
        "luis@example.com",
        HASH,
        legajo="REP-003",
    )
    repositorio = RepositorioRepresentante(db_temporal)

    with pytest.raises(ErrorValidacion):
        repositorio.insertar(representante)
