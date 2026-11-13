import pytest

from src.models.seguridad import (
    ALGORITMO,
    ITERACIONES,
    generarHash,
    verificarContrasena,
)


def test_generarHash_noAlmacenaContrasenaEnTextoPlano():
    contrasena = "ClaveSegura123!"
    hash_almacenado = generarHash(contrasena)

    assert contrasena not in hash_almacenado
    partes = hash_almacenado.split("$")
    assert len(partes) == 4
    assert partes[0] == ALGORITMO
    assert int(partes[1]) == ITERACIONES


def test_generarHash_usaSaltAleatorio():
    contrasena = "ClaveSegura123!"

    primer_hash = generarHash(contrasena)
    segundo_hash = generarHash(contrasena)

    assert primer_hash != segundo_hash


def test_verificarContrasena_aceptaContrasenaCorrecta():
    contrasena = "ClaveSegura123!"
    hash_almacenado = generarHash(contrasena)

    assert verificarContrasena(contrasena, hash_almacenado) is True


def test_verificarContrasena_rechazaContrasenaIncorrecta():
    hash_almacenado = generarHash("ClaveSegura123!")

    assert verificarContrasena("OtraClave456!", hash_almacenado) is False


@pytest.mark.parametrize(
    "hash_invalido",
    [
        "",
        "texto-plano",
        "pbkdf2_sha256$200000$salt$hash$extra",
        "pbkdf2_sha256$no-numerico$00ff$00ff",
        "otro_algoritmo$200000$00ff$00ff",
    ],
)
def test_verificarContrasena_rechazaHashInvalido(hash_invalido):
    assert verificarContrasena("ClaveSegura123!", hash_invalido) is False


def test_iteraciones_minimas_de_seguridad():
    assert ITERACIONES >= 200_000
