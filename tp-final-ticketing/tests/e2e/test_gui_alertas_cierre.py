from tests.e2e.ayudas_gui import crearEntornoGui
from tests.integration.ayudas_control import (
    CLAVE,
    cerrarSesion,
    crearHitoDirecto,
    crearTicketDirecto,
    iniciarSesion,
    prepararBase,
)


def test_flujoAlertasListaDetalleMarcaLeidaYDetectaSinAlertas(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado="ASIGNADO",
    )
    iniciarSesion(entorno, representante.email)
    id_alerta = entorno.controlNotificaciones.generarAlerta(
        representante.idUsuario,
        id_ticket,
        "CAMBIO_ESTADO",
        "ALTA",
        "Se le asignó un ticket.",
    )
    cerrarSesion(entorno)
    consola.entradas = [
        "2",
        representante.email,
        CLAVE,
        "8",
        str(id_alerta),
        "8",
        "0",
        "3",
    ]

    gui.iniciar()

    assert "Se le asignó un ticket." in consola.texto
    assert "Alerta marcada como leída." in consola.texto
    assert "No hay alertas pendientes." in consola.texto
    assert entorno.alertas.buscarPorId(id_alerta).estado == "LEIDA"


def test_flujoCierreYReaperturaDesdeLaGui(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado="RESUELTO",
    )
    crearHitoDirecto(
        entorno,
        id_ticket,
        estado="CUMPLIDO",
        fecha_cumplimiento=entorno.reloj(),
    )
    consola.entradas = [
        "2",
        representante.email,
        CLAVE,
        "6",
        str(id_ticket),
        "Atención finalizada.",
        "7",
        str(id_ticket),
        "El problema reapareció.",
        "0",
        "3",
    ]

    gui.iniciar()

    ticket = entorno.tickets.buscarPorId(id_ticket)
    assert ticket.estado == "REABIERTO"
    assert ticket.idRepresentante is None
    assert f"Ticket #{id_ticket} cerrado." in consola.texto
    assert f"Ticket #{id_ticket} reabierto." in consola.texto
    tipos = [
        evento.tipoEvento
        for evento in entorno.historial.listarPorTicket(id_ticket)
    ]
    assert tipos == ["CIERRE", "REAPERTURA"]


def test_ticketCerradoBloqueaMensajesYHitosEnLaGui(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado="RESUELTO",
    )
    crearHitoDirecto(
        entorno,
        id_ticket,
        estado="CUMPLIDO",
        fecha_cumplimiento=entorno.reloj(),
    )
    consola.entradas = [
        "2",
        representante.email,
        CLAVE,
        "6",
        str(id_ticket),
        "Cierre definitivo.",
        "3",
        str(id_ticket),
        "s",
        "Mensaje tardío",
        "4",
        str(id_ticket),
        "1",
        "Hito tardío",
        "2026-01-20 10:00",
        "2",
        "0",
        "3",
    ]

    gui.iniciar()

    assert (
        "No se pueden enviar mensajes a un ticket cerrado."
        in consola.texto
    )
    assert "El ticket está cerrado." in consola.texto
    assert entorno.mensajes.listarPorTicket(id_ticket) == []
    assert len(entorno.hitos.listarPorTicket(id_ticket)) == 1
