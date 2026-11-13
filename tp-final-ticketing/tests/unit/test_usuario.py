import pytest

from src.excepciones import ErrorValidacion
from src.models.estados import ROL_CLIENTE, ROL_REPRESENTANTE
from src.models.seguridad import verificarContrasena
from src.models.usuario import Usuario


def test_crearUsuario_normalizaEmailYHasheaContrasena():
    usuario = Usuario.crear(
        1,
        "Ana Pérez",
        " Ana.Perez@Example.COM ",
        "ClaveSegura123!",
        ROL_CLIENTE,
    )

    assert usuario.idUsuario == 1
    assert usuario.nombre == "Ana Pérez"
    assert usuario.email == "ana.perez@example.com"
    assert usuario.rol == ROL_CLIENTE
    assert usuario.activo is True
    assert usuario.contrasenaHash != "ClaveSegura123!"
    assert verificarContrasena("ClaveSegura123!", usuario.contrasenaHash) is True


@pytest.mark.parametrize(
    "email",
    [
        "sin-arroba",
        "@example.com",
        "ana@",
        "ana @example.com",
        "",
    ],
)
def test_crearUsuario_rechazaEmailInvalido(email):
    with pytest.raises(ErrorValidacion):
        Usuario.crear(1, "Ana", email, "ClaveSegura123!", ROL_CLIENTE)


def test_crearUsuario_rechazaNombreVacio():
    with pytest.raises(ErrorValidacion):
        Usuario.crear(1, "   ", "ana@example.com", "ClaveSegura123!", ROL_CLIENTE)


def test_crearUsuario_rechazaRolInvalido():
    with pytest.raises(ErrorValidacion):
        Usuario.crear(1, "Ana", "ana@example.com", "ClaveSegura123!", "ADMIN")


def test_crearUsuario_rechazaContrasenaVacia():
    with pytest.raises(ErrorValidacion):
        Usuario.crear(1, "Ana", "ana@example.com", "", ROL_CLIENTE)


def test_constructor_rechazaContrasenaEnTextoPlano():
    with pytest.raises(ErrorValidacion):
        Usuario(1, "Ana", "ana@example.com", "ClaveSegura123!", ROL_CLIENTE)


def test_usuario_respetaEstadoActivoYRoles():
    cliente = Usuario.crear(
        1, "Ana", "ana@example.com", "ClaveSegura123!", ROL_CLIENTE
    )
    representante = Usuario.crear(
        2,
        "Luis",
        "luis@example.com",
        "ClaveSegura123!",
        ROL_REPRESENTANTE,
        activo=False,
    )

    assert cliente.esCliente() is True
    assert cliente.esRepresentante() is False
    assert representante.esRepresentante() is True
    assert representante.activo is False
