from datetime import datetime

from src.db.repositorios.repositorio_cliente import RepositorioCliente
from src.db.repositorios.repositorio_mensaje import RepositorioMensaje
from src.db.repositorios.repositorio_producto import RepositorioProducto
from src.db.repositorios.repositorio_ticket import RepositorioTicket
from src.db.repositorios.repositorio_tipo_producto import (
    RepositorioTipoProducto,
)
from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.models.cliente import Cliente
from src.models.estados import PRIORIDAD_ALTA, ROL_CLIENTE
from src.models.mensaje import Mensaje
from src.models.producto import Producto
from src.models.ticket import Ticket
from src.models.tipo_producto import TipoProducto
from src.models.usuario import Usuario

CLAVE = "ClaveSegura123!"
FECHA = datetime(2026, 1, 10, 9, 0)
FECHA_POSTERIOR = datetime(2026, 1, 10, 10, 0)


def _crear_ticket(conexion):
    repositorio_usuarios = RepositorioUsuario(conexion)
    usuario = Usuario.crear(
        None, "Ana", "ana@example.com", CLAVE, ROL_CLIENTE
    )
    id_cliente = repositorio_usuarios.insertar(usuario)
    RepositorioCliente(conexion).insertar(
        Cliente(
            id_cliente,
            "Ana",
            "ana@example.com",
            usuario.contrasenaHash,
        )
    )

    repositorio_tipos = RepositorioTipoProducto(conexion)
    id_tipo = repositorio_tipos.insertar(TipoProducto(None, "Software"))
    repositorio_productos = RepositorioProducto(conexion)
    id_producto = repositorio_productos.insertar(
        Producto(None, "Gestor", "1.0", id_tipo)
    )

    repositorio_tickets = RepositorioTicket(conexion)
    id_ticket = repositorio_tickets.insertar(
        Ticket(
            "Título",
            "Descripción",
            PRIORIDAD_ALTA,
            id_cliente,
            id_producto,
            id_tipo,
            fechaCreacion=FECHA,
        )
    )
    return id_ticket, id_cliente


def test_insertarYBuscarMensaje(db_temporal):
    id_ticket, id_autor = _crear_ticket(db_temporal)
    repositorio = RepositorioMensaje(db_temporal)
    mensaje = Mensaje(
        id_ticket,
        id_autor,
        "Estamos revisando el caso.",
        fechaEnvio=FECHA,
    )

    id_mensaje = repositorio.insertar(mensaje)
    recuperado = repositorio.buscarPorId(id_mensaje)

    assert recuperado.idMensaje == id_mensaje
    assert recuperado.idTicket == id_ticket
    assert recuperado.idAutor == id_autor
    assert recuperado.contenido == "Estamos revisando el caso."
    assert recuperado.fechaEnvio == FECHA
    assert recuperado.leido is False


def test_listarMensajesPorTicketEnOrdenCronologico(db_temporal):
    id_ticket, id_autor = _crear_ticket(db_temporal)
    repositorio = RepositorioMensaje(db_temporal)
    id_posterior = repositorio.insertar(
        Mensaje(
            id_ticket,
            id_autor,
            "Segundo mensaje",
            fechaEnvio=FECHA_POSTERIOR,
        )
    )
    id_anterior = repositorio.insertar(
        Mensaje(
            id_ticket,
            id_autor,
            "Primer mensaje",
            fechaEnvio=FECHA,
        )
    )

    mensajes = repositorio.listarPorTicket(id_ticket)

    assert [mensaje.idMensaje for mensaje in mensajes] == [
        id_anterior,
        id_posterior,
    ]


def test_marcarMensajeComoLeido(db_temporal):
    id_ticket, id_autor = _crear_ticket(db_temporal)
    repositorio = RepositorioMensaje(db_temporal)
    id_mensaje = repositorio.insertar(
        Mensaje(id_ticket, id_autor, "Mensaje", fechaEnvio=FECHA)
    )

    repositorio.marcarLeido(id_mensaje)

    assert repositorio.buscarPorId(id_mensaje).leido is True


def test_listarMensajesDeOtroTicketNoSeMezclan(db_temporal):
    id_ticket, id_autor = _crear_ticket(db_temporal)
    repositorio = RepositorioMensaje(db_temporal)
    repositorio.insertar(
        Mensaje(id_ticket, id_autor, "Mensaje", fechaEnvio=FECHA)
    )

    assert repositorio.listarPorTicket(999) == []
