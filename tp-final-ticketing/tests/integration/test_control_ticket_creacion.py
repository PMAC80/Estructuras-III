import pytest

from src.excepciones import (
    ErrorAutenticacion,
    ErrorNoEncontrado,
    ErrorPermiso,
    ErrorValidacion,
)
from src.models.estados import (
    ESTADO_NUEVO,
    PRIORIDAD_ALTA,
    PRIORIDAD_MEDIA,
)
from tests.integration.ayudas_control import (
    FECHA,
    cerrarSesion,
    crearEntorno,
    crearTipoProducto,
    iniciarSesion,
    prepararBase,
)


def test_crearTicketValidoRegistraEstadoClienteEHistorial(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    iniciarSesion(entorno, cliente.email)

    ticket = entorno.controlTicket.crearTicket(
        "No puedo iniciar sesión",
        "El sistema rechaza mi clave.",
        PRIORIDAD_ALTA,
        id_producto,
        id_tipo,
    )

    assert ticket.idTicket is not None
    assert ticket.estado == ESTADO_NUEVO
    assert ticket.idCliente == cliente.idUsuario
    assert ticket.idRepresentante is None
    assert ticket.idProducto == id_producto
    assert ticket.idTipoProducto == id_tipo
    assert ticket.fechaCreacion == FECHA

    historial = entorno.historial.listarPorTicket(ticket.idTicket)
    assert len(historial) == 1
    evento = historial[0]
    assert evento.tipoEvento == "CREACION"
    assert evento.idActor == cliente.idUsuario
    assert evento.estadoAnterior is None
    assert evento.estadoNuevo == ESTADO_NUEVO


def test_crearTicketConDatosInvalidosLanzaValidacion(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    iniciarSesion(entorno, cliente.email)

    with pytest.raises(ErrorValidacion):
        entorno.controlTicket.crearTicket(
            "",
            "Descripción",
            PRIORIDAD_ALTA,
            id_producto,
            id_tipo,
        )
    with pytest.raises(ErrorValidacion):
        entorno.controlTicket.crearTicket(
            "Título",
            "Descripción",
            "URGENTE",
            id_producto,
            id_tipo,
        )


def test_crearTicketConProductoDeOtroTipoLanzaValidacion(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    otro_tipo = crearTipoProducto(entorno, "Hardware")
    iniciarSesion(entorno, cliente.email)

    with pytest.raises(ErrorValidacion, match="tipo"):
        entorno.controlTicket.crearTicket(
            "Título",
            "Descripción",
            PRIORIDAD_MEDIA,
            id_producto,
            otro_tipo,
        )


def test_crearTicketConProductoInexistenteLanzaNoEncontrado(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, _, id_tipo, _ = prepararBase(entorno)
    iniciarSesion(entorno, cliente.email)

    with pytest.raises(ErrorNoEncontrado):
        entorno.controlTicket.crearTicket(
            "Título",
            "Descripción",
            PRIORIDAD_MEDIA,
            999,
            id_tipo,
        )


def test_crearTicketRequiereSesionDeCliente(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)

    with pytest.raises(ErrorAutenticacion):
        entorno.controlTicket.crearTicket(
            "Título",
            "Descripción",
            PRIORIDAD_MEDIA,
            id_producto,
            id_tipo,
        )

    iniciarSesion(entorno, representante.email)
    with pytest.raises(ErrorPermiso):
        entorno.controlTicket.crearTicket(
            "Título",
            "Descripción",
            PRIORIDAD_MEDIA,
            id_producto,
            id_tipo,
        )

    cerrarSesion(entorno)
    iniciarSesion(entorno, cliente.email)
    ticket = entorno.controlTicket.crearTicket(
        "Título",
        "Descripción",
        PRIORIDAD_MEDIA,
        id_producto,
        id_tipo,
    )
    assert ticket.idCliente == cliente.idUsuario
