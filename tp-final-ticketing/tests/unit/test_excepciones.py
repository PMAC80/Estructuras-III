import pytest

from src.excepciones import (
    ErrorAutenticacion,
    ErrorConflicto,
    ErrorDominio,
    ErrorEstado,
    ErrorNoEncontrado,
    ErrorPermiso,
    ErrorValidacion,
)


@pytest.mark.parametrize(
    "excepcion",
    [
        ErrorValidacion,
        ErrorAutenticacion,
        ErrorPermiso,
        ErrorEstado,
        ErrorNoEncontrado,
        ErrorConflicto,
    ],
)
def test_excepciones_heredanDeErrorDominio(excepcion):
    assert issubclass(excepcion, ErrorDominio)
    assert issubclass(excepcion, Exception)


@pytest.mark.parametrize(
    "excepcion",
    [
        ErrorValidacion,
        ErrorAutenticacion,
        ErrorPermiso,
        ErrorEstado,
        ErrorNoEncontrado,
        ErrorConflicto,
    ],
)
def test_excepciones_conservanMensajeEnEspanol(excepcion):
    error = excepcion("El dato ingresado no es válido.")

    assert str(error) == "El dato ingresado no es válido."
