from datetime import datetime

import pytest

from src.excepciones import ErrorEstado
from src.models.estados import (
    ESTADO_ASIGNADO,
    ESTADO_CERRADO,
    ESTADO_EN_PROGRESO,
    ESTADO_NUEVO,
    ESTADO_REABIERTO,
    ESTADO_RESUELTO,
    EVENTO_ASIGNAR,
    EVENTO_CERRAR,
    EVENTO_INICIAR,
    EVENTO_REABRIR,
    EVENTO_RESOLVER,
    PRIORIDAD_MEDIA,
)
from src.models.ticket import Ticket

FECHA_CREACION = datetime(2026, 1, 10, 9, 0)
FECHA_CIERRE = datetime(2026, 1, 20, 12, 0)


def crear_ticket():
    return Ticket(
        "Título",
        "Descripción",
        PRIORIDAD_MEDIA,
        1,
        10,
        1,
        fechaCreacion=FECHA_CREACION,
    )


def test_transiciones_permitidas_recorrenCicloCompleto():
    ticket = crear_ticket()

    ticket.cambiarEstado(EVENTO_ASIGNAR)
    assert ticket.estado == ESTADO_ASIGNADO

    ticket.cambiarEstado(EVENTO_INICIAR)
    assert ticket.estado == ESTADO_EN_PROGRESO

    ticket.cambiarEstado(EVENTO_RESOLVER)
    assert ticket.estado == ESTADO_RESUELTO

    ticket.cambiarEstado(EVENTO_CERRAR, fecha=FECHA_CIERRE)
    assert ticket.estado == ESTADO_CERRADO
    assert ticket.fechaCierre == FECHA_CIERRE

    ticket.cambiarEstado(EVENTO_REABRIR)
    assert ticket.estado == ESTADO_REABIERTO
    assert ticket.fechaCierre is None

    ticket.cambiarEstado(EVENTO_ASIGNAR)
    assert ticket.estado == ESTADO_ASIGNADO


@pytest.mark.parametrize(
    "estado,evento",
    [
        (ESTADO_NUEVO, EVENTO_CERRAR),
        (ESTADO_NUEVO, EVENTO_INICIAR),
        (ESTADO_ASIGNADO, EVENTO_CERRAR),
        (ESTADO_ASIGNADO, EVENTO_REABRIR),
        (ESTADO_EN_PROGRESO, EVENTO_REABRIR),
        (ESTADO_RESUELTO, EVENTO_REABRIR),
        (ESTADO_CERRADO, EVENTO_INICIAR),
        (ESTADO_CERRADO, EVENTO_CERRAR),
        (ESTADO_REABIERTO, EVENTO_RESOLVER),
    ],
)
def test_transiciones_prohibidas_lanzanErrorEstado(estado, evento):
    ticket = crear_ticket()
    ticket.estado = estado

    with pytest.raises(ErrorEstado):
        ticket.cambiarEstado(evento)


def test_evento_desconocido_lanzaErrorEstado():
    ticket = crear_ticket()

    with pytest.raises(ErrorEstado):
        ticket.cambiarEstado("EVENTO_INEXISTENTE")


def test_puedeTransicionar_devuelveBooleano():
    ticket = crear_ticket()

    assert ticket.puedeTransicionar(EVENTO_ASIGNAR) is True
    assert ticket.puedeTransicionar(EVENTO_CERRAR) is False
