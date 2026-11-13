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
    ESTADO_EN_PROGRESO,
    ESTADO_HITO_CUMPLIDO,
    ESTADO_HITO_PENDIENTE,
    ESTADO_REABIERTO,
    ESTADO_RESUELTO,
)
from tests.integration.ayudas_control import (
    FECHA,
    crearEntorno,
    crearHitoDirecto,
    crearTicketDirecto,
    iniciarSesion,
    prepararBase,
    registrarCliente,
    registrarRepresentante,
)


def test_representanteCierraTicketResueltoConHitosCumplidos(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_RESUELTO,
    )
    crearHitoDirecto(
        entorno,
        id_ticket,
        estado=ESTADO_HITO_CUMPLIDO,
        fecha_cumplimiento=FECHA,
    )
    iniciarSesion(entorno, representante.email)

    ticket = entorno.controlTicket.cerrarTicket(
        id_ticket,
        "Atención finalizada.",
    )

    assert ticket.estado == ESTADO_CERRADO
    assert ticket.fechaCierre == FECHA
    persistido = entorno.tickets.buscarPorId(id_ticket)
    assert persistido.estado == ESTADO_CERRADO
    assert persistido.fechaCierre == FECHA

    historial = entorno.historial.listarPorTicket(id_ticket)
    assert historial[-1].tipoEvento == "CIERRE"
    assert historial[-1].idActor == representante.idUsuario
    assert historial[-1].estadoAnterior == ESTADO_RESUELTO
    assert historial[-1].estadoNuevo == ESTADO_CERRADO
    assert historial[-1].detalle == "Atención finalizada."

    alertas = entorno.alertas.listarPorUsuario(cliente.idUsuario)
    assert len(alertas) == 1
    assert alertas[0].tipo == "CAMBIO_ESTADO"
    assert alertas[0].idTicket == id_ticket


def test_cerrarTicketNoResueltoLanzaEstado(db_temporal):
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
        entorno.controlTicket.cerrarTicket(id_ticket)

    assert (
        entorno.tickets.buscarPorId(id_ticket).estado
        == ESTADO_EN_PROGRESO
    )


def test_cerrarTicketSoloPermiteRepresentanteAsignado(db_temporal):
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
        estado=ESTADO_RESUELTO,
    )

    with pytest.raises(ErrorAutenticacion):
        entorno.controlTicket.cerrarTicket(id_ticket)

    iniciarSesion(entorno, cliente.email)
    with pytest.raises(ErrorPermiso):
        entorno.controlTicket.cerrarTicket(id_ticket)

    iniciarSesion(entorno, otro.email)
    with pytest.raises(ErrorPermiso):
        entorno.controlTicket.cerrarTicket(id_ticket)

    iniciarSesion(entorno, representante.email)
    with pytest.raises(ErrorNoEncontrado):
        entorno.controlTicket.cerrarTicket(999)


def test_cerrarConHitosPendientesSinJustificacionLanzaEstado(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_RESUELTO,
    )
    crearHitoDirecto(entorno, id_ticket)
    iniciarSesion(entorno, representante.email)

    with pytest.raises(ErrorEstado, match="justificar"):
        entorno.controlTicket.cerrarTicket(id_ticket)

    assert entorno.tickets.buscarPorId(id_ticket).estado == ESTADO_RESUELTO


def test_cerrarConHitosPendientesConJustificacionEsPermitido(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_RESUELTO,
    )
    id_hito = crearHitoDirecto(entorno, id_ticket)
    iniciarSesion(entorno, representante.email)

    ticket = entorno.controlTicket.cerrarTicket(
        id_ticket,
        "El cliente pidió el cierre con un hito pendiente.",
    )

    assert ticket.estado == ESTADO_CERRADO
    assert (
        entorno.hitos.buscarPorId(id_hito).estado
        == ESTADO_HITO_PENDIENTE
    )
    assert (
        entorno.historial.listarPorTicket(id_ticket)[-1].detalle
        == "El cliente pidió el cierre con un hito pendiente."
    )


def test_cerrarSinHitosRequiereJustificacion(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_RESUELTO,
    )
    iniciarSesion(entorno, representante.email)

    with pytest.raises(ErrorEstado, match="justificar"):
        entorno.controlTicket.cerrarTicket(id_ticket)

    ticket = entorno.controlTicket.cerrarTicket(
        id_ticket,
        "Sin hitos definidos.",
    )
    assert ticket.estado == ESTADO_CERRADO


def test_cerrarTicketBloqueaMensajesYHitosPosteriores(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_RESUELTO,
    )
    crearHitoDirecto(
        entorno,
        id_ticket,
        estado=ESTADO_HITO_CUMPLIDO,
        fecha_cumplimiento=FECHA,
    )
    iniciarSesion(entorno, representante.email)
    entorno.controlTicket.cerrarTicket(id_ticket, "Cerrado.")

    with pytest.raises(ErrorEstado):
        entorno.controlHito.crearHito(
            id_ticket,
            "Hito posterior",
            FECHA + timedelta(days=1),
            orden=2,
        )

    iniciarSesion(entorno, cliente.email)
    with pytest.raises(ErrorEstado, match="cerrado"):
        entorno.controlTicket.agregarMensaje(id_ticket, "Mensaje posterior")


def test_reabrirTicketPorClienteDentroDelPlazoDesasignaYAlerta(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_CERRADO,
        fecha_cierre=FECHA - timedelta(days=5),
    )
    iniciarSesion(entorno, cliente.email)

    ticket = entorno.controlTicket.reabrirTicket(
        id_ticket,
        "El problema persiste.",
    )

    assert ticket.estado == ESTADO_REABIERTO
    assert ticket.idRepresentante is None
    assert ticket.fechaCierre is None
    persistido = entorno.tickets.buscarPorId(id_ticket)
    assert persistido.estado == ESTADO_REABIERTO
    assert persistido.idRepresentante is None
    assert persistido.fechaCierre is None

    historial = entorno.historial.listarPorTicket(id_ticket)
    assert historial[-1].tipoEvento == "REAPERTURA"
    assert historial[-1].idActor == cliente.idUsuario
    assert historial[-1].estadoAnterior == ESTADO_CERRADO
    assert historial[-1].estadoNuevo == ESTADO_REABIERTO
    assert historial[-1].detalle == "El problema persiste."

    alertas = entorno.alertas.listarPorUsuario(representante.idUsuario)
    assert len(alertas) == 1
    assert alertas[0].tipo == "REAPERTURA"
    assert alertas[0].idTicket == id_ticket


def test_reabrirTicketPorRepresentanteAsignado(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_CERRADO,
        fecha_cierre=FECHA - timedelta(days=2),
    )
    iniciarSesion(entorno, representante.email)

    ticket = entorno.controlTicket.reabrirTicket(
        id_ticket,
        "Revisión adicional.",
    )

    assert ticket.estado == ESTADO_REABIERTO
    assert (
        entorno.historial.listarPorTicket(id_ticket)[-1].idActor
        == representante.idUsuario
    )


def test_reabrirTicketLuegoPuedeAsignarse(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        estado=ESTADO_CERRADO,
        fecha_cierre=FECHA - timedelta(days=1),
    )
    iniciarSesion(entorno, cliente.email)
    entorno.controlTicket.reabrirTicket(id_ticket, "Revisar nuevamente.")

    iniciarSesion(entorno, representante.email)
    ticket = entorno.controlTicket.asignarTicket(
        id_ticket,
        representante.idUsuario,
    )

    assert ticket.estado == ESTADO_ASIGNADO


def test_reabrirTicketFueraDelPlazoLanzaEstado(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_CERRADO,
        fecha_cierre=FECHA - timedelta(days=8),
    )
    iniciarSesion(entorno, cliente.email)

    with pytest.raises(ErrorEstado, match="plazo"):
        entorno.controlTicket.reabrirTicket(id_ticket, "Tarde.")

    assert entorno.tickets.buscarPorId(id_ticket).estado == ESTADO_CERRADO


def test_reabrirTicketEnPlazoLimiteEsPermitido(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_CERRADO,
        fecha_cierre=FECHA - timedelta(days=7),
    )
    iniciarSesion(entorno, cliente.email)

    ticket = entorno.controlTicket.reabrirTicket(id_ticket, "En plazo.")

    assert ticket.estado == ESTADO_REABIERTO


def test_reabrirTicketNoCerradoLanzaEstado(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_RESUELTO,
    )
    iniciarSesion(entorno, cliente.email)

    with pytest.raises(ErrorEstado):
        entorno.controlTicket.reabrirTicket(id_ticket, "No cerrado.")


def test_reabrirTicketValidaPermisosMotivoYExistencia(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    ajeno = registrarCliente(
        entorno,
        email="otro@example.com",
        nombre="Otro",
    )
    otro_representante = registrarRepresentante(
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
        estado=ESTADO_CERRADO,
        fecha_cierre=FECHA - timedelta(days=1),
    )

    with pytest.raises(ErrorAutenticacion):
        entorno.controlTicket.reabrirTicket(id_ticket, "Motivo")

    iniciarSesion(entorno, otro_representante.email)
    with pytest.raises(ErrorPermiso):
        entorno.controlTicket.reabrirTicket(id_ticket, "Motivo")

    iniciarSesion(entorno, ajeno.email)
    with pytest.raises(ErrorPermiso):
        entorno.controlTicket.reabrirTicket(id_ticket, "Motivo")

    iniciarSesion(entorno, cliente.email)
    with pytest.raises(ErrorValidacion):
        entorno.controlTicket.reabrirTicket(id_ticket, "   ")
    with pytest.raises(ErrorNoEncontrado):
        entorno.controlTicket.reabrirTicket(999, "Motivo")
