from datetime import datetime

from src.db.repositorios.repositorio_cliente import RepositorioCliente
from src.db.repositorios.repositorio_historial import RepositorioHistorial
from src.db.repositorios.repositorio_producto import RepositorioProducto
from src.db.repositorios.repositorio_ticket import RepositorioTicket
from src.db.repositorios.repositorio_tipo_producto import (
    RepositorioTipoProducto,
)
from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.models.cliente import Cliente
from src.models.estados import PRIORIDAD_ALTA, ROL_CLIENTE
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


def test_insertarYListarHistorialEnOrdenCronologico(db_temporal):
    id_ticket, id_actor = _crear_ticket(db_temporal)
    repositorio = RepositorioHistorial(db_temporal)

    id_posterior = repositorio.insertar(
        id_ticket,
        id_actor,
        "ASIGNACION",
        "NUEVO",
        "ASIGNADO",
        "Asignado a Luis",
        FECHA_POSTERIOR,
    )
    id_anterior = repositorio.insertar(
        id_ticket,
        id_actor,
        "CREACION",
        None,
        "NUEVO",
        "Ticket creado",
        FECHA,
    )

    registros = repositorio.listarPorTicket(id_ticket)

    assert [registro.idEvento for registro in registros] == [
        id_anterior,
        id_posterior,
    ]
    assert registros[0].tipoEvento == "CREACION"
    assert registros[0].estadoAnterior is None
    assert registros[0].estadoNuevo == "NUEVO"
    assert registros[1].estadoAnterior == "NUEVO"
    assert registros[1].estadoNuevo == "ASIGNADO"


def test_historialAdmiteActorDeSistema(db_temporal):
    id_ticket, _ = _crear_ticket(db_temporal)
    repositorio = RepositorioHistorial(db_temporal)

    id_evento = repositorio.insertar(
        id_ticket,
        None,
        "ALERTA",
        None,
        None,
        "Alerta generada por el sistema",
        FECHA,
    )

    registro = repositorio.listarPorTicket(id_ticket)[0]
    assert registro.idEvento == id_evento
    assert registro.idActor is None


def test_historialNoExponeOperacionesDeModificacion(db_temporal):
    repositorio = RepositorioHistorial(db_temporal)

    assert not hasattr(repositorio, "actualizar")
    assert not hasattr(repositorio, "eliminar")
    assert not hasattr(repositorio, "borrar")


def test_listarHistorialDeOtroTicketDevuelveListaVacia(db_temporal):
    repositorio = RepositorioHistorial(db_temporal)

    assert repositorio.listarPorTicket(999) == []
