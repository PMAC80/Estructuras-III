from datetime import timedelta

import pytest

from src.excepciones import (
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
    ESTADO_HITO_EN_PROGRESO,
    ESTADO_HITO_PENDIENTE,
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


def test_crearHitoValidoPersisteYRegistraHistorial(db_temporal):
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

    hito = entorno.controlHito.crearHito(
        id_ticket,
        "Entrega de módulo",
        FECHA + timedelta(days=2),
        orden=1,
    )

    assert hito.idHito is not None
    assert hito.idTicket == id_ticket
    assert hito.descripcion == "Entrega de módulo"
    assert hito.fechaCompromiso == FECHA + timedelta(days=2)
    assert hito.orden == 1
    assert hito.estado == ESTADO_HITO_PENDIENTE

    persistido = entorno.hitos.buscarPorId(hito.idHito)
    assert persistido.descripcion == "Entrega de módulo"
    historial = entorno.historial.listarPorTicket(id_ticket)
    assert historial[-1].tipoEvento == "HITO_CREADO"
    assert historial[-1].idActor == representante.idUsuario


def test_crearHitoConFechaAnteriorAlTicketLanzaValidacion(db_temporal):
    entorno = crearEntorno(db_temporal)
    cliente, representante, id_tipo, id_producto = prepararBase(entorno)
    id_ticket = crearTicketDirecto(
        entorno,
        cliente.idUsuario,
        id_producto,
        id_tipo,
        id_representante=representante.idUsuario,
        estado=ESTADO_ASIGNADO,
        fecha_creacion=FECHA,
    )
    iniciarSesion(entorno, representante.email)

    with pytest.raises(ErrorValidacion):
        entorno.controlHito.crearHito(
            id_ticket,
            "Hito inválido",
            FECHA - timedelta(days=1),
        )


def test_crearHitoRequiereRepresentanteAsignado(db_temporal):
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
        entorno.controlHito.crearHito(
            id_ticket,
            "Hito",
            FECHA + timedelta(days=1),
        )

    iniciarSesion(entorno, otro.email)
    with pytest.raises(ErrorPermiso):
        entorno.controlHito.crearHito(
            id_ticket,
            "Hito",
            FECHA + timedelta(days=1),
        )

    with pytest.raises(ErrorNoEncontrado):
        entorno.controlHito.crearHito(
            999,
            "Hito",
            FECHA + timedelta(days=1),
        )


def test_crearHitoEnTicketCerradoLanzaEstado(db_temporal):
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
    iniciarSesion(entorno, representante.email)

    with pytest.raises(ErrorEstado, match="cerrado"):
        entorno.controlHito.crearHito(
            id_ticket,
            "Hito",
            FECHA + timedelta(days=1),
        )


def test_actualizarHitoPersisteYRegistraHistorial(db_temporal):
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
    id_hito = crearHitoDirecto(
        entorno,
        id_ticket,
        descripcion="Original",
        fecha_compromiso=FECHA + timedelta(days=1),
    )
    iniciarSesion(entorno, representante.email)

    hito = entorno.controlHito.actualizarHito(
        id_hito,
        descripcion="Actualizado",
        fechaCompromiso=FECHA + timedelta(days=3),
        estado=ESTADO_HITO_EN_PROGRESO,
    )

    assert hito.descripcion == "Actualizado"
    assert hito.fechaCompromiso == FECHA + timedelta(days=3)
    assert hito.estado == ESTADO_HITO_EN_PROGRESO
    persistido = entorno.hitos.buscarPorId(id_hito)
    assert persistido.descripcion == "Actualizado"
    assert historialTipo(entorno, id_ticket) == "HITO_ACTUALIZADO"


def test_actualizarHitoTicketCerradoLanzaEstado(db_temporal):
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
    id_hito = crearHitoDirecto(entorno, id_ticket)
    iniciarSesion(entorno, representante.email)

    with pytest.raises(ErrorEstado, match="cerrado"):
        entorno.controlHito.actualizarHito(
            id_hito,
            descripcion="No permitido",
        )


def test_completarHitoPersisteFechaYHistorial(db_temporal):
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
    id_hito = crearHitoDirecto(entorno, id_ticket)
    iniciarSesion(entorno, representante.email)

    hito = entorno.controlHito.completarHito(id_hito)

    assert hito.estado == ESTADO_HITO_CUMPLIDO
    assert hito.fechaCumplimiento == FECHA
    persistido = entorno.hitos.buscarPorId(id_hito)
    assert persistido.estado == ESTADO_HITO_CUMPLIDO
    assert persistido.fechaCumplimiento == FECHA
    assert historialTipo(entorno, id_ticket) == "HITO_CUMPLIDO"


def test_completarUltimoHitoResuelveTicket(db_temporal):
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
    crearHitoDirecto(
        entorno,
        id_ticket,
        descripcion="Primero",
        orden=1,
        estado=ESTADO_HITO_CUMPLIDO,
        fecha_cumplimiento=FECHA,
    )
    id_ultimo = crearHitoDirecto(
        entorno,
        id_ticket,
        descripcion="Último",
        orden=2,
    )
    iniciarSesion(entorno, representante.email)

    hito = entorno.controlHito.completarHito(id_ultimo)

    assert hito.estado == ESTADO_HITO_CUMPLIDO
    assert entorno.tickets.buscarPorId(id_ticket).estado == ESTADO_RESUELTO

    alertas = entorno.alertas.listarPorUsuario(cliente.idUsuario)
    assert len(alertas) == 1
    assert alertas[0].tipo == "CAMBIO_ESTADO"


def test_completarHitoNoUltimoNoResuelveTicket(db_temporal):
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
    id_primero = crearHitoDirecto(
        entorno,
        id_ticket,
        descripcion="Primero",
        orden=1,
    )
    crearHitoDirecto(
        entorno,
        id_ticket,
        descripcion="Segundo",
        orden=2,
    )
    iniciarSesion(entorno, representante.email)

    entorno.controlHito.completarHito(id_primero)

    assert (
        entorno.tickets.buscarPorId(id_ticket).estado
        == ESTADO_EN_PROGRESO
    )


def test_listarHitosValidaAccesoAlTicket(db_temporal):
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
    id_hito = crearHitoDirecto(entorno, id_ticket)

    iniciarSesion(entorno, cliente.email)
    assert [hito.idHito for hito in entorno.controlHito.listarHitos(id_ticket)] == [
        id_hito
    ]

    iniciarSesion(entorno, ajeno.email)
    with pytest.raises(ErrorPermiso):
        entorno.controlHito.listarHitos(id_ticket)

    with pytest.raises(ErrorNoEncontrado):
        entorno.controlHito.listarHitos(999)


def historialTipo(entorno, id_ticket):
    return entorno.historial.listarPorTicket(id_ticket)[-1].tipoEvento
