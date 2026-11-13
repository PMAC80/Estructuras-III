import pytest

from src.controller.control_usuario import ControlUsuario
from src.controller.sesion import Sesion
from src.db.repositorios.repositorio_cliente import RepositorioCliente
from src.db.repositorios.repositorio_representante import (
    RepositorioRepresentante,
)
from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.excepciones import (
    ErrorAutenticacion,
    ErrorConflicto,
    ErrorPermiso,
    ErrorValidacion,
)
from src.models.cliente import Cliente
from src.models.estados import ROL_CLIENTE, ROL_REPRESENTANTE
from src.models.usuario import Usuario

CLAVE = "ClaveSegura123!"


def _control(conexion):
    return ControlUsuario(
        conexion,
        RepositorioUsuario(conexion),
        RepositorioCliente(conexion),
        RepositorioRepresentante(conexion),
    )


def test_registrarClientePersisteUsuarioYPerfil(db_temporal):
    control = _control(db_temporal)

    usuario = control.registrar(
        "Ana",
        "Ana@Example.com",
        CLAVE,
        ROL_CLIENTE,
        empresa="Acme",
        telefono="1234",
    )

    assert usuario.idUsuario is not None
    assert usuario.rol == ROL_CLIENTE
    assert usuario.email == "ana@example.com"

    persistido = RepositorioUsuario(db_temporal).buscarPorId(usuario.idUsuario)
    assert persistido.contrasenaHash != CLAVE
    assert persistido.contrasenaHash.startswith("pbkdf2_sha256$")

    cliente = RepositorioCliente(db_temporal).buscarPorId(usuario.idUsuario)
    assert cliente.nombre == "Ana"
    assert cliente.empresa == "Acme"
    assert cliente.telefono == "1234"


def test_registrarRepresentantePersistePerfil(db_temporal):
    control = _control(db_temporal)

    usuario = control.registrar(
        "Luis",
        "luis@example.com",
        CLAVE,
        ROL_REPRESENTANTE,
        legajo="LEG-001",
        especialidad="Redes",
    )

    representante = RepositorioRepresentante(db_temporal).buscarPorId(
        usuario.idUsuario
    )
    assert representante.nombre == "Luis"
    assert representante.legajo == "LEG-001"
    assert representante.especialidad == "Redes"


def test_registrarEmailDuplicadoLanzaConflicto(db_temporal):
    control = _control(db_temporal)
    control.registrar("Ana", "ana@example.com", CLAVE, ROL_CLIENTE)

    with pytest.raises(ErrorConflicto, match="email"):
        control.registrar("Otra", "ana@example.com", CLAVE, ROL_CLIENTE)


def test_registrarRolInvalidoLanzaValidacion(db_temporal):
    control = _control(db_temporal)

    with pytest.raises(ErrorValidacion, match="rol"):
        control.registrar("Ana", "ana@example.com", CLAVE, "ADMIN")


def test_registrarContrasenaInseguraLanzaValidacion(db_temporal):
    control = _control(db_temporal)

    with pytest.raises(ErrorValidacion, match="contraseña"):
        control.registrar("Ana", "ana@example.com", "corta", ROL_CLIENTE)

    with pytest.raises(ErrorValidacion, match="contraseña"):
        control.registrar("Ana", "ana@example.com", "sololetras", ROL_CLIENTE)


def test_loginValidoCreaSesion(db_temporal):
    control = _control(db_temporal)
    usuario = control.registrar(
        "Ana",
        "ana@example.com",
        CLAVE,
        ROL_CLIENTE,
    )

    sesion = control.login("ana@example.com", CLAVE)

    assert isinstance(sesion, Sesion)
    assert sesion.idUsuario == usuario.idUsuario
    assert sesion.rol == ROL_CLIENTE
    assert sesion.nombre == "Ana"
    assert control.obtenerSesion() == sesion


def test_loginCredencialesInvalidasNoCreanSesion(db_temporal):
    control = _control(db_temporal)
    control.registrar("Ana", "ana@example.com", CLAVE, ROL_CLIENTE)

    with pytest.raises(ErrorAutenticacion, match="incorrect"):
        control.login("ana@example.com", "Incorrecta123")

    with pytest.raises(ErrorAutenticacion, match="incorrect"):
        control.login("nadie@example.com", CLAVE)

    assert control.obtenerSesion() is None


def test_loginUsuarioInactivoLanzaAutenticacion(db_temporal):
    usuario = Usuario.crear(
        None,
        "Ina",
        "ina@example.com",
        CLAVE,
        ROL_CLIENTE,
        activo=False,
    )
    id_usuario = RepositorioUsuario(db_temporal).insertar(usuario)
    RepositorioCliente(db_temporal).insertar(
        Cliente(
            id_usuario,
            "Ina",
            "ina@example.com",
            usuario.contrasenaHash,
            activo=False,
        )
    )

    control = _control(db_temporal)
    with pytest.raises(ErrorAutenticacion, match="habilitada"):
        control.login("ina@example.com", CLAVE)
    assert control.obtenerSesion() is None


def test_loginCamposVaciosLanzaValidacion(db_temporal):
    control = _control(db_temporal)

    with pytest.raises(ErrorValidacion):
        control.login("", CLAVE)
    with pytest.raises(ErrorValidacion):
        control.login("ana@example.com", "")


def test_logoutEliminaSesion(db_temporal):
    control = _control(db_temporal)
    control.registrar("Ana", "ana@example.com", CLAVE, ROL_CLIENTE)
    control.login("ana@example.com", CLAVE)

    control.logout()

    assert control.obtenerSesion() is None
    with pytest.raises(ErrorAutenticacion):
        control.requerirSesion()


def test_requerirRolSinSesionLanzaAutenticacion(db_temporal):
    control = _control(db_temporal)

    with pytest.raises(ErrorAutenticacion):
        control.requerirRol(ROL_CLIENTE)


def test_requerirRolIncorrectoLanzaPermiso(db_temporal):
    control = _control(db_temporal)
    control.registrar("Ana", "ana@example.com", CLAVE, ROL_CLIENTE)
    sesion = control.login("ana@example.com", CLAVE)

    assert control.requerirRol(ROL_CLIENTE) == sesion
    with pytest.raises(ErrorPermiso):
        control.requerirRol(ROL_REPRESENTANTE)
