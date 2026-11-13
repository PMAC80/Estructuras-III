from src.models.estados import (
    ESTADO_ASIGNADO,
    ESTADO_CERRADO,
    ESTADO_EN_PROGRESO,
    ESTADO_HITO_CUMPLIDO,
    ESTADO_HITO_PENDIENTE,
    ESTADO_NUEVO,
    ESTADO_REABIERTO,
)
from tests.e2e.ayudas_gui import crearEntornoGui
from tests.integration.ayudas_control import (
    CLAVE,
    crearProducto,
    crearTipoProducto,
)


def _ejecutar(gui, consola, entradas):
    consola.entradas.extend(entradas)
    gui.iniciar()


def test_flujoE2ECompletoRf1Rf10(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    id_tipo = crearTipoProducto(entorno)
    id_producto = crearProducto(entorno, id_tipo)
    email_cliente = "ana@example.com"
    email_representante = "luis@example.com"

    _ejecutar(
        gui,
        consola,
        [
            "1",
            "Ana",
            email_cliente,
            CLAVE,
            "1",
            "1",
            "Luis",
            email_representante,
            CLAVE,
            "2",
            "LEG-100",
            "2",
            email_cliente,
            CLAVE,
            "1",
            str(id_tipo),
            str(id_producto),
            "No puedo ingresar",
            "Error al iniciar sesión",
            "ALTA",
            "0",
            "3",
        ],
    )

    cliente = entorno.usuarios.buscarPorEmail(email_cliente)
    representante = entorno.usuarios.buscarPorEmail(
        email_representante
    )
    tickets = entorno.tickets.listarPorCliente(cliente.idUsuario)
    assert len(tickets) == 1
    ticket = tickets[0]
    assert ticket.estado == ESTADO_NUEVO
    assert ticket.idRepresentante is None
    assert (
        entorno.historial.listarPorTicket(ticket.idTicket)[0].tipoEvento
        == "CREACION"
    )
    assert "Registro exitoso" in consola.texto
    assert f"Ticket #{ticket.idTicket} creado" in consola.texto

    _ejecutar(
        gui,
        consola,
        [
            "2",
            email_representante,
            CLAVE,
            "1",
            str(ticket.idTicket),
            str(representante.idUsuario),
            "3",
            str(ticket.idTicket),
            "s",
            "Estamos revisando su caso.",
            "8",
            "",
            "4",
            str(ticket.idTicket),
            "1",
            "Diagnóstico inicial",
            "2026-01-11 10:00",
            "1",
            "0",
            "3",
        ],
    )

    ticket = entorno.tickets.buscarPorId(ticket.idTicket)
    assert ticket.estado == ESTADO_ASIGNADO
    assert ticket.idRepresentante == representante.idUsuario
    alertas_representante = entorno.alertas.listarPorUsuario(
        representante.idUsuario
    )
    assert alertas_representante
    assert alertas_representante[0].idTicket == ticket.idTicket
    assert "Se le asignó" in consola.texto
    assert "Mensaje enviado." in consola.texto

    hitos = entorno.hitos.listarPorTicket(ticket.idTicket)
    assert len(hitos) == 1
    assert hitos[0].estado == ESTADO_HITO_PENDIENTE
    id_hito = hitos[0].idHito

    _ejecutar(
        gui,
        consola,
        [
            "2",
            email_representante,
            CLAVE,
            "5",
            str(ticket.idTicket),
            "1",
            "4",
            str(ticket.idTicket),
            "3",
            str(id_hito),
            "6",
            str(ticket.idTicket),
            "",
            "0",
            "3",
        ],
    )

    ticket = entorno.tickets.buscarPorId(ticket.idTicket)
    assert ticket.estado == ESTADO_CERRADO
    assert ticket.fechaCierre is not None
    assert (
        entorno.hitos.buscarPorId(id_hito).estado
        == ESTADO_HITO_CUMPLIDO
    )
    assert "Estado actualizado a EN_PROGRESO." in consola.texto
    assert "resuelto automáticamente" in consola.texto
    assert f"Ticket #{ticket.idTicket} cerrado." in consola.texto

    alertas_cliente = entorno.alertas.listarPorUsuario(
        cliente.idUsuario
    )
    assert alertas_cliente
    id_alerta_cierre = next(
        alerta.idAlerta
        for alerta in alertas_cliente
        if alerta.tipo == "CAMBIO_ESTADO"
        and ticket.idTicket == alerta.idTicket
    )

    _ejecutar(
        gui,
        consola,
        [
            "2",
            email_cliente,
            CLAVE,
            "6",
            str(ticket.idTicket),
            "El problema reapareció.",
            "5",
            str(id_alerta_cierre),
            "0",
            "3",
        ],
    )

    ticket = entorno.tickets.buscarPorId(ticket.idTicket)
    assert ticket.estado == ESTADO_REABIERTO
    assert ticket.idRepresentante is None
    assert f"Ticket #{ticket.idTicket} reabierto." in consola.texto
    assert "Alerta marcada como leída." in consola.texto

    alertas_representante = entorno.alertas.listarPorUsuario(
        representante.idUsuario
    )
    assert any(
        alerta.tipo == "REAPERTURA"
        and alerta.idTicket == ticket.idTicket
        for alerta in alertas_representante
    )

    _ejecutar(
        gui,
        consola,
        [
            "2",
            email_representante,
            CLAVE,
            "1",
            str(ticket.idTicket),
            str(representante.idUsuario),
            "0",
            "3",
        ],
    )

    ticket = entorno.tickets.buscarPorId(ticket.idTicket)
    assert ticket.estado == ESTADO_ASIGNADO
    assert ticket.idRepresentante == representante.idUsuario

    tipos = [
        evento.tipoEvento
        for evento in entorno.historial.listarPorTicket(ticket.idTicket)
    ]
    assert tipos == [
        "CREACION",
        "ASIGNACION",
        "MENSAJE",
        "HITO_CREADO",
        "CAMBIO_ESTADO",
        "HITO_CUMPLIDO",
        "CAMBIO_ESTADO",
        "CIERRE",
        "REAPERTURA",
        "ASIGNACION",
    ]
    assert "Traceback" not in consola.texto
