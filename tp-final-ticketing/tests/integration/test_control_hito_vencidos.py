from datetime import timedelta

import pytest

from src.excepciones import ErrorAutenticacion
from src.models.estados import (
    ESTADO_ASIGNADO,
    ESTADO_HITO_CUMPLIDO,
    ESTADO_HITO_PENDIENTE,
    ESTADO_HITO_VENCIDO,
)
from tests.integration.ayudas_control import (
    FECHA,
    crearEntorno,
    crearHitoDirecto,
    crearTicketDirecto,
    iniciarSesion,
    prepararBase,
)


def test_verificarVencidosMarcaHitoYGeneraAlerta(db_temporal):
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
        descripcion="Entrega vencida",
        fecha_compromiso=FECHA - timedelta(days=1),
    )
    iniciarSesion(entorno, representante.email)

    vencidos = entorno.controlHito.verificarVencidos()

    assert [hito.idHito for hito in vencidos] == [id_hito]
    assert vencidos[0].estado == ESTADO_HITO_VENCIDO
    persistido = entorno.hitos.buscarPorId(id_hito)
    assert persistido.estado == ESTADO_HITO_VENCIDO

    historial = entorno.historial.listarPorTicket(id_ticket)
    assert historial[-1].tipoEvento == "HITO_VENCIDO"
    assert historial[-1].idActor == representante.idUsuario

    alertas = entorno.alertas.listarPorUsuario(representante.idUsuario)
    assert len(alertas) == 1
    assert alertas[0].tipo == "HITO_VENCIDO"
    assert alertas[0].idTicket == id_ticket


def test_verificarVencidosIgnoraFuturosYCumplidos(db_temporal):
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
    id_futuro = crearHitoDirecto(
        entorno,
        id_ticket,
        fecha_compromiso=FECHA + timedelta(days=1),
        orden=1,
    )
    id_cumplido = crearHitoDirecto(
        entorno,
        id_ticket,
        fecha_compromiso=FECHA - timedelta(days=1),
        orden=2,
        estado=ESTADO_HITO_CUMPLIDO,
        fecha_cumplimiento=FECHA - timedelta(days=2),
    )
    iniciarSesion(entorno, representante.email)

    vencidos = entorno.controlHito.verificarVencidos()

    assert vencidos == []
    assert (
        entorno.hitos.buscarPorId(id_futuro).estado
        == ESTADO_HITO_PENDIENTE
    )
    assert (
        entorno.hitos.buscarPorId(id_cumplido).estado
        == ESTADO_HITO_CUMPLIDO
    )
    assert entorno.alertas.listarPorUsuario(representante.idUsuario) == []


def test_verificarVencidosEsIdempotente(db_temporal):
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
    crearHitoDirecto(
        entorno,
        id_ticket,
        fecha_compromiso=FECHA - timedelta(days=1),
    )
    iniciarSesion(entorno, representante.email)

    primera = entorno.controlHito.verificarVencidos()
    segunda = entorno.controlHito.verificarVencidos()

    assert len(primera) == 1
    assert segunda == []
    assert len(entorno.alertas.listarPorUsuario(representante.idUsuario)) == 1


def test_verificarVencidosRequiereSesion(db_temporal):
    entorno = crearEntorno(db_temporal)

    with pytest.raises(ErrorAutenticacion):
        entorno.controlHito.verificarVencidos()
