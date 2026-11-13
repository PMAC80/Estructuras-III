import pytest

from src.excepciones import ErrorValidacion
from src.models.cliente import Cliente
from src.models.estados import ROL_CLIENTE, ROL_REPRESENTANTE
from src.models.representante import Representante
from src.models.seguridad import generarHash
from src.models.usuario import Usuario

HASH = generarHash("ClaveSegura123!")


def test_cliente_heredaDeUsuarioYConservaDatos():
    cliente = Cliente(
        1,
        "Ana",
        "ana@example.com",
        HASH,
        empresa="ACME",
        telefono="123456",
    )

    assert isinstance(cliente, Usuario)
    assert cliente.rol == ROL_CLIENTE
    assert cliente.esCliente() is True
    assert cliente.empresa == "ACME"
    assert cliente.telefono == "123456"


def test_cliente_permiteDatosOpcionales():
    cliente = Cliente(1, "Ana", "ana@example.com", HASH)

    assert cliente.empresa is None
    assert cliente.telefono is None


def test_cliente_rechazaEmpresaNoTexto():
    with pytest.raises(ErrorValidacion):
        Cliente(1, "Ana", "ana@example.com", HASH, empresa=123)


def test_representante_heredaDeUsuarioYConservaDatos():
    representante = Representante(
        2,
        "Luis",
        "luis@example.com",
        HASH,
        legajo="REP-001",
        especialidad="Redes",
    )

    assert isinstance(representante, Usuario)
    assert representante.rol == ROL_REPRESENTANTE
    assert representante.esRepresentante() is True
    assert representante.legajo == "REP-001"
    assert representante.especialidad == "Redes"


def test_representante_permiteDatosOpcionales():
    representante = Representante(2, "Luis", "luis@example.com", HASH)

    assert representante.legajo is None
    assert representante.especialidad is None


@pytest.mark.parametrize("legajo", ["", "  ", "RE", "REP 001", "REP@001"])
def test_representante_rechazaLegajoInvalido(legajo):
    with pytest.raises(ErrorValidacion):
        Representante(2, "Luis", "luis@example.com", HASH, legajo=legajo)
