from tests.e2e.ayudas_gui import crearEntornoGui
from tests.integration.ayudas_control import (
    CLAVE,
    prepararBase,
)


def test_opcionNoNumericaEnMenuInicialNoGeneraTraceback(db_temporal):
    _, gui, consola = crearEntornoGui(db_temporal, ["abc", "3"])

    gui.iniciar()

    assert "Opción inválida." in consola.texto
    assert "Traceback" not in consola.texto


def test_entradaNoNumericaEnFlujoMuestraMensajeClaro(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    consola.entradas = [
        "2",
        cliente.email,
        CLAVE,
        "1",
        "no-es-numero",
        "0",
        "3",
    ]

    gui.iniciar()

    assert "Debe ingresar un número válido." in consola.texto
    assert "Traceback" not in consola.texto


def test_opcionInexistenteEnMenuDeRolMuestraError(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, _, _, _ = prepararBase(entorno)
    consola.entradas = [
        "2",
        cliente.email,
        CLAVE,
        "9",
        "0",
        "3",
    ]

    gui.iniciar()

    assert "Opción inválida." in consola.texto
    assert "Traceback" not in consola.texto


def test_errorDeDominioMuestraMensajeYNoCreaTicket(db_temporal):
    entorno, gui, consola = crearEntornoGui(db_temporal)
    cliente, _, id_tipo, id_producto = prepararBase(entorno)
    consola.entradas = [
        "2",
        cliente.email,
        CLAVE,
        "1",
        str(id_tipo),
        str(id_producto),
        "Título",
        "Descripción",
        "URGENTE",
        "0",
        "3",
    ]

    gui.iniciar()

    assert (
        "Error: La prioridad debe ser BAJA, MEDIA o ALTA."
        in consola.texto
    )
    assert "Traceback" not in consola.texto
    assert entorno.tickets.listarPorCliente(cliente.idUsuario) == []
