from dataclasses import dataclass
from datetime import datetime, timedelta

from src.controller.control_hito import ControlHito
from src.controller.control_notificaciones import ControlNotificaciones
from src.controller.control_ticket import ControlTicket
from src.controller.control_usuario import ControlUsuario
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
from src.models.estados import (
    ESTADO_HITO_PENDIENTE,
    ESTADO_NUEVO,
    PRIORIDAD_ALTA,
    ROL_CLIENTE,
    ROL_REPRESENTANTE,
)
from src.models.hito import Hito
from src.models.producto import Producto
from src.models.representante import Representante
from src.models.ticket import Ticket
from src.models.tipo_producto import TipoProducto
from src.models.usuario import Usuario

CLAVE = "ClaveSegura123!"
FECHA = datetime(2026, 1, 10, 9, 0)


class RelojFijo:
    def __init__(self, momento=FECHA):
        self.momento = momento

    def __call__(self):
        return self.momento

    def avanzar(self, delta):
        self.momento = self.momento + delta


@dataclass
class Entorno:
    conexion: object
    usuarios: RepositorioUsuario
    clientes: RepositorioCliente
    representantes: RepositorioRepresentante
    tipos: RepositorioTipoProducto
    productos: RepositorioProducto
    tickets: RepositorioTicket
    hitos: RepositorioHito
    mensajes: RepositorioMensaje
    historial: RepositorioHistorial
    alertas: RepositorioAlerta
    reloj: RelojFijo
    controlUsuario: ControlUsuario
    controlNotificaciones: ControlNotificaciones
    controlTicket: ControlTicket
    controlHito: ControlHito


def crearEntorno(conexion, momento=FECHA):
    reloj = RelojFijo(momento)
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
        reloj,
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
        reloj,
    )
    controlHito = ControlHito(
        conexion,
        hitos,
        tickets,
        historial,
        controlUsuario,
        controlNotificaciones,
        controlTicket,
        reloj,
    )

    return Entorno(
        conexion,
        usuarios,
        clientes,
        representantes,
        tipos,
        productos,
        tickets,
        hitos,
        mensajes,
        historial,
        alertas,
        reloj,
        controlUsuario,
        controlNotificaciones,
        controlTicket,
        controlHito,
    )


def registrarCliente(
    entorno,
    email="ana@example.com",
    nombre="Ana",
    clave=CLAVE,
):
    return entorno.controlUsuario.registrar(
        nombre,
        email,
        clave,
        ROL_CLIENTE,
    )


def registrarRepresentante(
    entorno,
    email="luis@example.com",
    nombre="Luis",
    legajo="LEG-001",
    clave=CLAVE,
):
    return entorno.controlUsuario.registrar(
        nombre,
        email,
        clave,
        ROL_REPRESENTANTE,
        legajo=legajo,
    )


def registrarRepresentanteInactivo(
    entorno,
    email="inactivo@example.com",
    nombre="Inactivo",
    legajo="LEG-INA",
    clave=CLAVE,
):
    usuario = Usuario.crear(
        None,
        nombre,
        email,
        clave,
        ROL_REPRESENTANTE,
        activo=False,
    )
    id_usuario = entorno.usuarios.insertar(usuario)
    entorno.representantes.insertar(
        Representante(
            id_usuario,
            nombre,
            email,
            usuario.contrasenaHash,
            legajo=legajo,
            activo=False,
        )
    )
    return id_usuario


def crearTipoProducto(entorno, nombre="Software", descripcion=None):
    return entorno.tipos.insertar(
        TipoProducto(None, nombre, descripcion)
    )


def crearProducto(
    entorno,
    id_tipo,
    nombre="Gestor",
    version="1.0",
):
    return entorno.productos.insertar(
        Producto(None, nombre, version, id_tipo)
    )


def prepararBase(entorno):
    cliente = registrarCliente(entorno)
    representante = registrarRepresentante(entorno)
    id_tipo = crearTipoProducto(entorno)
    id_producto = crearProducto(entorno, id_tipo)
    return cliente, representante, id_tipo, id_producto


def crearTicketDirecto(
    entorno,
    id_cliente,
    id_producto,
    id_tipo,
    id_representante=None,
    estado=ESTADO_NUEVO,
    fecha_creacion=None,
    fecha_cierre=None,
    titulo="Ticket",
    prioridad=PRIORIDAD_ALTA,
):
    return entorno.tickets.insertar(
        Ticket(
            titulo,
            "Descripción",
            prioridad,
            id_cliente,
            id_producto,
            id_tipo,
            idRepresentante=id_representante,
            estado=estado,
            fechaCreacion=fecha_creacion or entorno.reloj(),
            fechaCierre=fecha_cierre,
        )
    )


def crearHitoDirecto(
    entorno,
    id_ticket,
    descripcion="Hito",
    fecha_compromiso=None,
    orden=1,
    estado=ESTADO_HITO_PENDIENTE,
    fecha_cumplimiento=None,
):
    return entorno.hitos.insertar(
        Hito(
            id_ticket,
            descripcion,
            fecha_compromiso or (entorno.reloj() + timedelta(days=1)),
            orden=orden,
            estado=estado,
            fechaCumplimiento=fecha_cumplimiento,
        )
    )


def iniciarSesion(entorno, email, clave=CLAVE):
    return entorno.controlUsuario.login(email, clave)


def cerrarSesion(entorno):
    entorno.controlUsuario.logout()
