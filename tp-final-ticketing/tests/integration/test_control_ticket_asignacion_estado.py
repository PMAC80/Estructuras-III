import pytest

from src.excepciones import (
    ErrorEstado,
    ErrorNoEncontrado,
    ErrorPermiso,
)
from src.models.estados import (
    ESTADO_ASIGNADO,
    ESTADO_EN_PROGRESO,
    ESTADO_NUEVO,
    ESTADO_REABIERTO,
    ESTADO_RESUELTO,
    EVENTO_INICIAR,
    EVENTO_RESOLVER,
)
from tests.integration.ayudas_control import (
    crearEntorno,
    crearTicketDirecto,
    iniciarSesion,
    prepararBase,
    registrarRepresentante,
    registrarRepresentanteInactivo,
)


def test_asignarTicketValidoActualizaEstadoHistorialYAlerta(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
    )
    iniciarSesion(entorno, representante.email)

    ticket = entorno.controlTicket.asignarTicket(
        id_ticket,
        representante.idUsuario,
    )

    assert ticket.estado == ESTADO_ASIGNADO
    assert ticket.idRepresentante == representante.idUsuario
    persistido = entorno.tickets.buscarPorId(id_ticket)
    assert persistido.estado == ESTADO_ASIGNADO
    assert persistido.idRepresentante == representante.idUsuario

    historial = entorno.historial.listarPorTicket(id_ticket)
    assert len(historial) == 1
    assert historial[0].tipoEvento == "ASIGNACION"
    assert historial[0].idActor == representante.idUsuario
    assert historial[0].estadoAnterior == ESTADO_NUEVO
    assert historial[0].estadoNuevo == ESTADO_ASIGNADO

    alertas = entorno.alertas.listarPorUsuario(representante.idUsuario)
    assert len(alertas) == 1
    assert alertas[0].idTicket == id_ticket
    assert alertas[0].tipo == "CAMBIO_ESTADO"


def test_asignarTicketARepresentanteInactivoLanzaEstado(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    inactivo = registrarRepresentanteInactivo(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
    )
    iniciarSesion(entorno, representante.email)

    with pytest.raises(ErrorEstado, match="activo"):
        entorno.controlTicket.asignarTicket(id_ticket, inactivo)

    assert entorno.tickets.buscarPorId(id_ticket).estado == ESTADO_NUEVO


def test_asignarTicketEnEstadoInvalidoLanzaEstado(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_EN_PROGRESO,
    )
    iniciarSesion(entorno, representante.email)

    with pytest.raises(ErrorEstado):
        entorno.controlTicket.asignarTicket(
            id_ticket,
            representante.idUsuario,
        )


def test_asignarTicketValidaExistenciaDeTicketYRepresentante(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
    )
    iniciarSesion(entorno, representante.email)

    with pytest.raises(ErrorNoEncontrado):
        entorno.controlTicket.asignarTicket(999, representante.idUsuario)
    with pytest.raises(ErrorNoEncontrado):
        entorno.controlTicket.asignarTicket(id_ticket, 999)


def test_asignarTicketRequiereRolRepresentante(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
    )
    iniciarSesion(entorno, cliente.email)

    with pytest.raises(ErrorPermiso):
        entorno.controlTicket.asignarTicket(
            id_ticket,
            cliente.idUsuario,
        )


def test_asignarTicketReabiertoCambiaAAsignado(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        estado=ESTADO_REABIERTO,
    )
    iniciarSesion(entorno, representante.email)

    ticket = entorno.controlTicket.asignarTicket(
        id_ticket,
        representante.idUsuario,
    )

    assert ticket.estado == ESTADO_ASIGNADO


def test_cambiarEstadoPermitidoPersisteHistorialYAlerta(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_ASIGNADO,
    )
    iniciarSesion(entorno, representante.email)

    ticket = entorno.controlTicket.cambiarEstado(
        id_ticket,
        EVENTO_INICIAR,
    )

    assert ticket.estado == ESTADO_EN_PROGRESO
    assert (
        entorno.tickets.buscarPorId(id_ticket).estado
        == ESTADO_EN_PROGRESO
    )
    historial = entorno.historial.listarPorTicket(id_ticket)
    assert historial[-1].tipoEvento == "CAMBIO_ESTADO"
    assert historial[-1].estadoAnterior == ESTADO_ASIGNADO
    assert historial[-1].estadoNuevo == ESTADO_EN_PROGRESO
    assert historial[-1].idActor == representante.idUsuario

    alertas = entorno.alertas.listarPorUsuario(cliente.idUsuario)
    assert len(alertas) == 1
    assert alertas[0].tipo == "CAMBIO_ESTADO"
    assert alertas[0].idTicket == id_ticket


def test_cambiarEstadoProhibidoNoPersiste(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_NUEVO,
    )
    iniciarSesion(entorno, representante.email)

    with pytest.raises(ErrorEstado):
        entorno.controlTicket.cambiarEstado(id_ticket, EVENTO_INICIAR)

    assert entorno.tickets.buscarPorId(id_ticket).estado == ESTADO_NUEVO
    assert entorno.historial.listarPorTicket(id_ticket) == []


def test_resolverManualmenteCambiaAResuelto(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_EN_PROGRESO,
    )
    iniciarSesion(entorno, representante.email)

    ticket = entorno.controlTicket.cambiarEstado(
        id_ticket,
        EVENTO_RESOLVER,
    )

    assert ticket.estado == ESTADO_RESUELTO


def test_cambiarEstadoSoloPermiteRepresentanteAsignado(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    otro = registrarRepresentante(
        entorno,
        email="marta@example.com",
        nombre="Marta",
        legajo="LEG-002",
    )
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_ASIGNADO,
    )

    iniciarSesion(entorno, cliente.email)
    with pytest.raises(ErrorPermiso):
        entorno.controlTicket.cambiarEstado(id_ticket, EVENTO_INICIAR)

    iniciarSesion(entorno, otro.email)
    with pytest.raises(ErrorPermiso):
        entorno.controlTicket.cambiarEstado(id_ticket, EVENTO_INICIAR)
