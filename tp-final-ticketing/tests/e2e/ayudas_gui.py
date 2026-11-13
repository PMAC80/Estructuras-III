from src.gui.gui import GUI
from tests.integration.ayudas_control import crearEntorno


class ConsolaFake:
    def __init__(self, entradas=()):
        self.entradas = list(entradas)
        self.salidas = []

    def leer(self, mensaje=""):
        if mensaje:
            self.salidas.append(mensaje)
        if not self.entradas:
            raise AssertionError(
                "La consola fake se quedó sin entradas programadas."
            )
        return self.entradas.pop(0)

    def escribir(self, mensaje=""):
        self.salidas.append(str(mensaje))

    @property
    def texto(self):
        return "\n".join(self.salidas)


def crearEntornoGui(conexion, entradas=()):
    entorno = crearEntorno(conexion)
    consola = ConsolaFake(entradas)
    gui = GUI(
        consola,
        entorno.controlUsuario,
        entorno.controlTicket,
        entorno.controlHito,
        entorno.controlNotificaciones,
    )
    return entorno, gui, consola
