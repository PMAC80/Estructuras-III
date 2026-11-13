from datetime import datetime

import pytest

from src.excepciones import ErrorValidacion
from src.models.mensaje import Mensaje

FECHA_ENVIO = datetime(2026, 1, 15, 10, 0)


def crear_mensaje(**cambios):
    datos = {
        "idTicket": 1,
        "idAutor": 2,
        "contenido": "Estamos revisando el caso.",
        "fechaEnvio": FECHA_ENVIO,
    }
    datos.update(cambios)
    return Mensaje(**datos)


def test_mensaje_creaConDatosCompletos():
    mensaje = crear_mensaje(idMensaje=7)

    assert mensaje.idMensaje == 7
    assert mensaje.idTicket == 1
    assert mensaje.idAutor == 2
    assert mensaje.contenido == "Estamos revisando el caso."
    assert mensaje.fechaEnvio == FECHA_ENVIO
    assert mensaje.leido is False


def test_mensaje_usaFechaActualSiNoSeIndica():
    mensaje = Mensaje(1, 2, "Mensaje")

    assert isinstance(mensaje.fechaEnvio, datetime)


@pytest.mark.parametrize(
    "cambios",
    [
        {"contenido": "   "},
        {"idTicket": None},
        {"idAutor": 0},
        {"fechaEnvio": "2026-01-15"},
        {"leido": "si"},
    ],
)
def test_mensaje_rechazaDatosInvalidos(cambios):
    with pytest.raises(ErrorValidacion):
        crear_mensaje(**cambios)


def test_mensaje_marcarLeido():
    mensaje = crear_mensaje()

    mensaje.marcarLeido()

    assert mensaje.leido is True
