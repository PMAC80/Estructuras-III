from datetime import datetime

import pytest

from src.excepciones import ErrorValidacion
from src.models.estados import (
    ESTADO_HITO_CUMPLIDO,
    ESTADO_HITO_EN_PROGRESO,
    ESTADO_HITO_PENDIENTE,
    ESTADO_HITO_VENCIDO,
)
from src.models.hito import Hito

FECHA_COMPROMISO = datetime(2026, 2, 1, 10, 0)
FECHA_CUMPLIMIENTO = datetime(2026, 1, 28, 15, 0)


def crear_hito(**cambios):
    datos = {
        "idTicket": 1,
        "descripcion": "Diagnóstico inicial",
        "fechaCompromiso": FECHA_COMPROMISO,
    }
    datos.update(cambios)
    return Hito(**datos)


def test_hito_creaConEstadoPendiente():
    hito = crear_hito(idHito=3, orden=2)

    assert hito.idHito == 3
    assert hito.idTicket == 1
    assert hito.descripcion == "Diagnóstico inicial"
    assert hito.fechaCompromiso == FECHA_COMPROMISO
    assert hito.estado == ESTADO_HITO_PENDIENTE
    assert hito.orden == 2
    assert hito.fechaCumplimiento is None


@pytest.mark.parametrize(
    "cambios",
    [
        {"descripcion": "   "},
        {"fechaCompromiso": "2026-02-01"},
        {"estado": "INVALIDO"},
        {"orden": 0},
        {"idTicket": None},
        {"fechaCumplimiento": "2026-01-01"},
    ],
)
def test_hito_rechazaDatosInvalidos(cambios):
    with pytest.raises(ErrorValidacion):
        crear_hito(**cambios)


def test_hito_completarRegistraFechaYEstado():
    hito = crear_hito()

    hito.completar(FECHA_CUMPLIMIENTO)

    assert hito.estado == ESTADO_HITO_CUMPLIDO
    assert hito.fechaCumplimiento == FECHA_CUMPLIMIENTO


def test_hito_actualizarEstadoValidaEstado():
    hito = crear_hito()

    hito.actualizarEstado(ESTADO_HITO_EN_PROGRESO)
    assert hito.estado == ESTADO_HITO_EN_PROGRESO

    with pytest.raises(ErrorValidacion):
        hito.actualizarEstado("INVALIDO")


def test_hito_estaVencidoSegunFechaYEstado():
    hito = crear_hito(fechaCompromiso=datetime(2026, 1, 10, 9, 0))

    assert hito.estaVencido(datetime(2026, 1, 11, 9, 0)) is True
    assert hito.estaVencido(datetime(2026, 1, 9, 9, 0)) is False

    hito.completar(datetime(2026, 1, 11, 9, 0))
    assert hito.estaVencido(datetime(2026, 1, 12, 9, 0)) is False

    otro_hito = crear_hito(estado=ESTADO_HITO_VENCIDO)
    assert otro_hito.estaVencido(datetime(2026, 1, 1, 9, 0)) is True
