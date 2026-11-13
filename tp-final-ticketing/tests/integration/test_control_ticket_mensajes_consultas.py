from datetime import timedelta

import pytest

from src.excepciones import (
    ErrorAutenticacion,
    ErrorEstado,
    ErrorNoEncontrado,
    ErrorPermiso,
    ErrorValidacion,
)
from src.models.estados import (
    ESTADO_ASIGNADO,
    ESTADO_CERRADO,
)
from tests.integration.ayudas_control import (
    FECHA,
    crearEntorno,
    crearTicketDirecto,
    iniciarSesion,
    prepararBase,
    registrarCliente,
    registrarRepresentante,
)


def test_agregarMensajeDeClientePersisteHistorialYAlerta(db_temporal):
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
    iniciarSesion(entorno, cliente.email)

    mensaje = entorno.controlTicket.agregarMensaje(
        id_ticket,
        "Sigue sin funcionar.",
    )

    assert mensaje.idMensaje is not None
    assert mensaje.idAutor == cliente.idUsuario
    assert mensaje.fechaEnvio == FECHA
    assert mensaje.leido is False
    persistido = entorno.mensajes.buscarPorId(mensaje.idMensaje)
    assert persistido.contenido == "Sigue sin funcionar."

    historial = entorno.historial.listarPorTicket(id_ticket)
    assert historial[-1].tipoEvento == "MENSAJE"
    assert historial[-1].idActor == cliente.idUsuario

    alertas = entorno.alertas.listarPorUsuario(representante.idUsuario)
    assert len(alertas) == 1
    assert alertas[0].tipo == "MENSAJE_NUEVO"
    assert alertas[0].idTicket == id_ticket


def test_agregarMensajeDeRepresentanteAlertaAlCliente(db_temporal):
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

    mensaje = entorno.controlTicket.agregarMensaje(
        id_ticket,
        "Estamos revisando el caso.",
    )

    assert mensaje.idAutor == representante.idUsuario
    alertas = entorno.alertas.listarPorUsuario(cliente.idUsuario)
    assert len(alertas) == 1
    assert alertas[0].tipo == "MENSAJE_NUEVO"


def test_agregarMensajeUsuarioAjenoLanzaPermiso(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    ajeno = registrarCliente(
        entorno,
        email="otro@example.com",
        nombre="Otro",
    )
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_ASIGNADO,
    )
    iniciarSesion(entorno, ajeno.email)

    with pytest.raises(ErrorPermiso):
        entorno.controlTicket.agregarMensaje(id_ticket, "Hola")


def test_agregarMensajeATicketCerradoLanzaEstado(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_CERRADO,
        fecha_cierre=FECHA,
    )
    iniciarSesion(entorno, cliente.email)

    with pytest.raises(ErrorEstado, match="cerrado"):
        entorno.controlTicket.agregarMensaje(id_ticket, "Hola")


def test_agregarMensajeValidaContenidoTicketYSesion(db_temporal):
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

    with pytest.raises(ErrorAutenticacion):
        entorno.controlTicket.agregarMensaje(id_ticket, "Hola")

    iniciarSesion(entorno, cliente.email)
    with pytest.raises(ErrorValidacion):
        entorno.controlTicket.agregarMensaje(id_ticket, "   ")
    with pytest.raises(ErrorNoEncontrado):
        entorno.controlTicket.agregarMensaje(999, "Hola")


def test_listarTicketsDeClienteSoloDevuelvePropios(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    otro = registrarCliente(
        entorno,
        email="otro@example.com",
        nombre="Otro",
    )
    id_propio = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
    )
    crearTicketDirecto(
        entorno,
        otro.idUsuario,
        id_producto,
        id_tipo,
    )
    iniciarSesion(entorno, cliente.email)

    tickets = entorno.controlTicket.listarTickets()

    assert [ticket.idTicket for ticket in tickets] == [id_propio]


def test_listarTicketsDeRepresentanteSoloDevuelveAsignados(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    otro = registrarRepresentante(
        entorno,
        email="marta@example.com",
        nombre="Marta",
        legajo="LEG-002",
    )
    id_propio = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_ASIGNADO,
    )
    crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=otro.idUsuario,
        estado=ESTADO_ASIGNADO,
    )
    crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
    )
    iniciarSesion(entorno, representante.email)

    tickets = entorno.controlTicket.listarTickets()

    assert [ticket.idTicket for ticket in tickets] == [id_propio]


def test_listarTicketsSinSesionLanzaAutenticacion(db_temporal):
    entorno = crearEntorno(db_temporal)

    with pytest.raises(ErrorAutenticacion):
        entorno.controlTicket.listarTickets()


def test_obtenerHistorialEnOrdenCronologico(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
    )
    id_posterior = entorno.historial.insertar(
        id_ticket,
        cliente.idUsuario,
        "POSTERIOR",
        detalle="Segundo",
        fecha=FECHA + timedelta(hours=1),
    )
    id_anterior = entorno.historial.insertar(
        id_ticket,
        cliente.idUsuario,
        "ANTERIOR",
        detalle="Primero",
        fecha=FECHA,
    )
    iniciarSesion(entorno, cliente.email)

    historial = entorno.controlTicket.obtenerHistorial(id_ticket)

    assert [evento.idEvento for evento in historial] == [
        id_anterior,
        id_posterior,
    ]


def test_obtenerHistorialDeTicketAjenoLanzaPermiso(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    ajeno = registrarCliente(
        entorno,
        email="otro@example.com",
        nombre="Otro",
    )
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
    )
    iniciarSesion(entorno, ajeno.email)

    with pytest.raises(ErrorPermiso):
        entorno.controlTicket.obtenerHistorial(id_ticket)
    with pytest.raises(ErrorNoEncontrado):
        entorno.controlTicket.obtenerHistorial(999)


def test_registrarHistorialUsaActorDeLaSesion(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
    )
    iniciarSesion(entorno, cliente.email)

    entorno.controlTicket.registrarHistorial(
        id_ticket,
        "NOTA",
        detalle="Evento manual",
    )

    historial = entorno.controlTicket.obtenerHistorial(id_ticket)
    assert historial[-1].tipoEvento == "NOTA"
    assert historial[-1].idActor == cliente.idUsuario
    assert historial[-1].detalle == "Evento manual"
