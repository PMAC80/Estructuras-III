from datetime import datetime

import pytest

from src.excepciones import ErrorValidacion
from src.models.estados import (
    ESTADO_NUEVO,
    PRIORIDAD_ALTA,
)
from src.models.ticket import Ticket

FECHA = datetime(2026, 1, 10, 9, 30)


def crear_ticket(**cambios):
    datos = {
        "titulo": "Error al iniciar sesión",
        "descripcion": "El sistema no permite ingresar.",
        "prioridad": PRIORIDAD_ALTA,
        "idCliente": 1,
        "idProducto": 10,
        "idTipoProducto": 1,
        "fechaCreacion": FECHA,
    }
    datos.update(cambios)
    return Ticket(**datos)


def test_ticket_creaConEstadoNuevo():
    ticket = crear_ticket()

    assert ticket.estado == ESTADO_NUEVO
    assert ticket.fechaCreacion == FECHA
    assert ticket.fechaCierre is None
    assert ticket.idRepresentante is None


def test_ticket_usaFechaActualSiNoSeIndica():
    ticket = Ticket(
        "Título",
        "Descripción",
        PRIORIDAD_ALTA,
        1,
        10,
        1,
    )

    assert isinstance(ticket.fechaCreacion, datetime)


@pytest.mark.parametrize(
    "cambios",
    [
        {"titulo": "   "},
        {"descripcion": ""},
        {"prioridad": "URGENTE"},
        {"idCliente": None},
        {"idProducto": 0},
        {"idTipoProducto": None},
        {"estado": "INVALIDO"},
        {"fechaCreacion": "2026-01-10"},
        {"idRepresentante": 0},
    ],
)
def test_ticket_rechazaDatosInvalidos(cambios):
    with pytest.raises(ErrorValidacion):
        crear_ticket(**cambios)


def test_ticket_conservaDatosIngresados():
    ticket = crear_ticket(idTicket=5, idRepresentante=2)

    assert ticket.idTicket == 5
    assert ticket.idRepresentante == 2
    assert ticket.titulo == "Error al iniciar sesión"
    assert ticket.idCliente == 1
    assert ticket.idProducto == 10
    assert ticket.idTipoProducto == 1
