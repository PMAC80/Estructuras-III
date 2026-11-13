from src.models.estados import ROL_CLIENTE, ROL_REPRESENTANTE
from tests.e2e.ayudas_gui import crearEntornoGui
from tests.integration.ayudas_control import (
    CLAVE,
    registrarCliente,
    registrarRepresentante,
)


def test_registroYLoginDesdeLaGui(db_temporal):
    entorno, gui, consola = crearEntornoGui(
        db_temporal,
        [
            "1",
            "Ana",
            "ana@example.com",
            CLAVE,
            "1",
            "2",
            "ana@example.com",
            CLAVE,
            "0",
            "3",
        ],
    )

    gui.iniciar()

    assert "Registro exitoso" in consola.texto
    assert "Bienvenido/a, Ana" in consola.texto
    assert entorno.controlUsuario.obtenerSesion() is None
    assert (
        entorno.usuarios.buscarPorEmail("ana@example.com").rol
        == ROL_CLIENTE
    )


def test_registroDeRepresentanteDesdeLaGuiSolicitaLegajo(db_temporal):
    entorno, gui, consola = crearEntornoGui(
        db_temporal,
        [
            "1",
            "Luis",
            "luis@example.com",
            CLAVE,
            "2",
            "LEG-100",
            "3",
        ],
    )

    gui.iniciar()

    representante = entorno.usuarios.buscarPorEmail("luis@example.com")
    assert representante.rol == ROL_REPRESENTANTE
    assert entorno.representantes.buscarPorId(
        representante.idUsuario
    ).legajo == "LEG-100"
    assert "Registro exitoso" in consola.texto


def test_loginConCredencialesInvalidasMuestraErrorYNoCreaSesion(db_temporal):
    entorno, gui, consola = crearEntornoGui(
        db_temporal,
        ["2", "ana@example.com", "ClaveIncorrecta1", "3"],
    )
    registrarCliente(entorno)

    gui.iniciar()

    assert "Email o contraseña incorrectos." in consola.texto
    assert entorno.controlUsuario.obtenerSesion() is None


def test_menuClienteMuestraSoloOpcionesDelClienteYLogoutVuelveAlInicio(
    db_temporal,
):
    entorno, gui, consola = crearEntornoGui(
        db_temporal,
        ["2", "ana@example.com", CLAVE, "0", "3"],
    )
    registrarCliente(entorno)

    gui.iniciar()

    assert "Crear ticket" in consola.texto
    assert "Reabrir ticket" in consola.texto
    assert "Asignar ticket" not in consola.texto
    assert "Cerrar ticket" not in consola.texto
    assert "Sesión cerrada." in consola.texto
    assert consola.texto.count("=== Sistema de Ticketing ===") == 2
    assert entorno.controlUsuario.obtenerSesion() is None


def test_menuRepresentanteMuestraSoloOpcionesDelRepresentante(db_temporal):
    entorno, gui, consola = crearEntornoGui(
        db_temporal,
        ["2", "luis@example.com", CLAVE, "0", "3"],
    )
    registrarRepresentante(entorno)

    gui.iniciar()

    assert "Asignar ticket" in consola.texto
    assert "Cerrar ticket" in consola.texto
    assert "Actualizar estado" in consola.texto
    assert "Crear ticket" not in consola.texto
