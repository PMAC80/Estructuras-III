from src.models.estados import (
    ESTADO_ASIGNADO,
    ESTADO_EN_PROGRESO,
    ESTADO_HITO_CUMPLIDO,
    ESTADO_RESUELTO,
)
from tests.e2e.ayudas_gui import crearEntornoGui
from tests.integration.ayudas_control import (
    CLAVE,
    crearHitoDirecto,
    crearTicketDirecto,
    prepararBase,
    registrarCliente,
)


def test_flujoCrearTicketMuestraIdentificadorYPersiste(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    consola.entradas = [
        "2",
        cliente.email,
        CLAVE,
        "1",
        str(id_tipo),
        str(id_producto),
        "No puedo ingresar",
        "Error al iniciar sesión",
        "ALTA",
        "0",
        "3",
    ]

    gui.iniciar()

    tickets = entorno.tickets.listarPorCliente(cliente.idUsuario)
    assert len(tickets) == 1
    assert tickets[0].titulo == "No puedo ingresar"
    assert tickets[0].prioridad == "ALTA"
    assert f"Ticket #{tickets[0].idTicket} creado" in consola.texto


def test_flujoAsignarTicketListaNuevosYConfirma(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
    )
    consola.entradas = [
        "2",
        representante.email,
        CLAVE,
        "1",
        str(id_ticket),
        str(representante.idUsuario),
        "0",
        "3",
    ]

    gui.iniciar()

    ticket = entorno.tickets.buscarPorId(id_ticket)
    assert ticket.estado == ESTADO_ASIGNADO
    assert ticket.idRepresentante == representante.idUsuario
    assert f"Ticket #{id_ticket} asignado" in consola.texto


def test_flujoMensajesPermiteEnviarYVisualizar(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_ASIGNADO,
    )
    consola.entradas = [
        "2",
        cliente.email,
        CLAVE,
        "3",
        str(id_ticket),
        "s",
        "Necesito ayuda con el acceso.",
        "0",
        "3",
    ]

    gui.iniciar()

    mensajes = entorno.mensajes.listarPorTicket(id_ticket)
    assert len(mensajes) == 1
    assert mensajes[0].contenido == "Necesito ayuda con el acceso."
    assert "Mensaje enviado." in consola.texto
    assert "Necesito ayuda con el acceso." in consola.texto


def test_flujoMensajesMuestraErrorDeAccesoAjeno(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
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
    consola.entradas = [
        "2",
        ajeno.email,
        CLAVE,
        "3",
        str(id_ticket),
        "0",
        "3",
    ]

    gui.iniciar()

    assert "No tiene acceso a este ticket." in consola.texto
    assert entorno.mensajes.listarPorTicket(id_ticket) == []


def test_flujoHitosPermiteCrearHito(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_ASIGNADO,
    )
    consola.entradas = [
        "2",
        representante.email,
        CLAVE,
        "4",
        str(id_ticket),
        "1",
        "Entrega del módulo",
        "2026-01-15 10:00",
        "1",
        "0",
        "3",
    ]

    gui.iniciar()

    hitos = entorno.hitos.listarPorTicket(id_ticket)
    assert len(hitos) == 1
    assert hitos[0].descripcion == "Entrega del módulo"
    assert "Hito creado." in consola.texto


def test_flujoHitosPermiteActualizarHito(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_ASIGNADO,
    )
    id_hito = crearHitoDirecto(entorno, id_ticket)
    consola.entradas = [
        "2",
        representante.email,
        CLAVE,
        "4",
        str(id_ticket),
        "2",
        str(id_hito),
        "Entrega actualizada",
        "2026-01-16 12:00",
        "2",
        "0",
        "3",
    ]

    gui.iniciar()

    hito = entorno.hitos.buscarPorId(id_hito)
    assert hito.descripcion == "Entrega actualizada"
    assert hito.orden == 2
    assert "Hito actualizado." in consola.texto


def test_flujoCompletarHitosResuelveTicket(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_EN_PROGRESO,
    )
    id_primero = crearHitoDirecto(
        entorno,
        id_ticket,
        descripcion="Primero",
        orden=1,
    )
    id_segundo = crearHitoDirecto(
        entorno,
        id_ticket,
        descripcion="Segundo",
        orden=2,
    )
    consola.entradas = [
        "2",
        representante.email,
        CLAVE,
        "4",
        str(id_ticket),
        "3",
        str(id_primero),
        "4",
        str(id_ticket),
        "3",
        str(id_segundo),
        "0",
        "3",
    ]

    gui.iniciar()

    assert (
        entorno.hitos.buscarPorId(id_primero).estado
        == ESTADO_HITO_CUMPLIDO
    )
    assert (
        entorno.hitos.buscarPorId(id_segundo).estado
        == ESTADO_HITO_CUMPLIDO
    )
    assert entorno.tickets.buscarPorId(id_ticket).estado == ESTADO_RESUELTO
    assert "resuelto automáticamente" in consola.texto
