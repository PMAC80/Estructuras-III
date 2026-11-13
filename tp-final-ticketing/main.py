from src.config import resolverRutaBaseDatos
from src.controller.control_hito import ControlHito
from src.controller.control_notificaciones import ControlNotificaciones
from src.controller.control_ticket import ControlTicket
from src.controller.control_usuario import ControlUsuario
from src.db.conexion import abrirConexion
from src.db.datos_iniciales import cargarDatosIniciales
from src.db.esquema import crearEsquema
from src.db.repositorios.repositorio_alerta import RepositorioAlerta
from src.db.repositorios.repositorio_cliente import RepositorioCliente
from src.db.repositorios.repositorio_historial import RepositorioHistorial
from src.db.repositorios.repositorio_hito import RepositorioHito
from src.db.repositorios.repositorio_mensaje import RepositorioMensaje
from src.db.repositorios.repositorio_producto import RepositorioProducto
from src.db.repositorios.repositorio_representante import (
    RepositorioRepresentante,
)
from src.db.repositorios.repositorio_ticket import RepositorioTicket
from src.db.repositorios.repositorio_tipo_producto import (
    RepositorioTipoProducto,
)
from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.gui.consola import ConsolaReal
from src.gui.gui import GUI


class Aplicacion:
    def __init__(
        self,
        conexion,
        gui,
        controlUsuario,
        controlTicket,
        controlHito,
        controlNotificaciones,
    ):
        self.conexion = conexion
        self.gui = gui
        self.controlUsuario = controlUsuario
        self.controlTicket = controlTicket
        self.controlHito = controlHito
        self.controlNotificaciones = controlNotificaciones

    def iniciar(self):
        self.gui.iniciar()

    def cerrar(self):
        self.conexion.close()


def crearAplicacion(rutaBd=None, consola=None, cargarIniciales=True):
    ruta = rutaBd if rutaBd is not None else resolverRutaBaseDatos()
    conexion = abrirConexion(ruta)
    crearEsquema(conexion)
    if cargarIniciales:
        cargarDatosIniciales(conexion)

    usuarios = RepositorioUsuario(conexion)
    clientes = RepositorioCliente(conexion)
    representantes = RepositorioRepresentante(conexion)
    tipos = RepositorioTipoProducto(conexion)
    productos = RepositorioProducto(conexion)
    tickets = RepositorioTicket(conexion)
    hitos = RepositorioHito(conexion)
    mensajes = RepositorioMensaje(conexion)
    historial = RepositorioHistorial(conexion)
    alertas = RepositorioAlerta(conexion)

    controlUsuario = ControlUsuario(
        conexion,
        usuarios,
        clientes,
        representantes,
    )
    controlNotificaciones = ControlNotificaciones(
        conexion,
        alertas,
        tickets,
        usuarios,
        representantes,
        controlUsuario,
    )
    controlTicket = ControlTicket(
        conexion,
        tickets,
        historial,
        mensajes,
        hitos,
        productos,
        tipos,
        clientes,
        representantes,
        controlUsuario,
        controlNotificaciones,
    )
    controlHito = ControlHito(
        conexion,
        hitos,
        tickets,
        historial,
        controlUsuario,
        controlNotificaciones,
        controlTicket,
    )
    gui = GUI(
        consola or ConsolaReal(),
        controlUsuario,
        controlTicket,
        controlHito,
        controlNotificaciones,
    )

    return Aplicacion(
        conexion,
        gui,
        controlUsuario,
        controlTicket,
        controlHito,
        controlNotificaciones,
    )


def main():
    aplicacion = crearAplicacion()
    try:
        aplicacion.iniciar()
    finally:
        aplicacion.cerrar()


if __name__ == "__main__":
    main()
