from datetime import datetime

from src.db.repositorios.repositorio_cliente import RepositorioCliente
from src.db.repositorios.repositorio_producto import RepositorioProducto
from src.db.repositorios.repositorio_representante import (
    RepositorioRepresentante,
)
from src.db.repositorios.repositorio_ticket import RepositorioTicket
from src.db.repositorios.repositorio_tipo_producto import (
    RepositorioTipoProducto,
)
from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.models.cliente import Cliente
from src.models.estados import (
    ESTADO_ASIGNADO,
    ESTADO_CERRADO,
    ESTADO_EN_PROGRESO,
    ESTADO_NUEVO,
    PRIORIDAD_ALTA,
    PRIORIDAD_MEDIA,
    ROL_CLIENTE,
    ROL_REPRESENTANTE,
)
from src.models.producto import Producto
from src.models.representante import Representante
from src.models.ticket import Ticket
from src.models.tipo_producto import TipoProducto
from src.models.usuario import Usuario

CLAVE = "ClaveSegura123!"
FECHA = datetime(2026, 1, 10, 9, 30)
FECHA_CIERRE = datetime(2026, 1, 20, 12, 0)


def _crear_cliente(conexion):
    repositorio = RepositorioUsuario(conexion)
    usuario = Usuario.crear(
        None, "Ana", "ana@example.com", CLAVE, ROL_CLIENTE
    )
    id_usuario = repositorio.insertar(usuario)
    RepositorioCliente(conexion).insertar(
        Cliente(
            id_usuario,
            "Ana",
            "ana@example.com",
            usuario.contrasenaHash,
        )
    )
    return id_usuario


def _crear_representante(conexion):
    repositorio = RepositorioUsuario(conexion)
    usuario = Usuario.crear(
        None, "Luis", "luis@example.com", CLAVE, ROL_REPRESENTANTE
    )
    id_usuario = repositorio.insertar(usuario)
    RepositorioRepresentante(conexion).insertar(
        Representante(
            id_usuario,
            "Luis",
            "luis@example.com",
            usuario.contrasenaHash,
            legajo="REP-001",
        )
    )
    return id_usuario


def _crear_producto(conexion):
    repositorio_tipos = RepositorioTipoProducto(conexion)
    id_tipo = repositorio_tipos.insertar(TipoProducto(None, "Software"))
    repositorio_productos = RepositorioProducto(conexion)
    id_producto = repositorio_productos.insertar(
        Producto(None, "Gestor", "1.0", id_tipo)
    )
    return id_tipo, id_producto


def _crear_ticket(
    id_cliente,
    id_producto,
    id_tipo,
    **cambios,
):
    datos = {
        "titulo": "Error al iniciar sesión",
        "descripcion": "El sistema no permite ingresar.",
        "prioridad": PRIORIDAD_ALTA,
        "idCliente": id_cliente,
        "idProducto": id_producto,
        "idTipoProducto": id_tipo,
        "fechaCreacion": FECHA,
    }
    datos.update(cambios)
    return Ticket(**datos)


def test_insertarYBuscarTicket(db_temporal):
    id_cliente = _crear_cliente(db_temporal)
    id_tipo, id_producto = _crear_producto(db_temporal)
    repositorio = RepositorioTicket(db_temporal)

    id_ticket = repositorio.insertar(
        _crear_ticket(id_cliente, id_producto, id_tipo)
    )

    recuperado = repositorio.buscarPorId(id_ticket)
    assert recuperado.idTicket == id_ticket
    assert recuperado.titulo == "Error al iniciar sesión"
    assert recuperado.estado == ESTADO_NUEVO
    assert recuperado.prioridad == PRIORIDAD_ALTA
    assert recuperado.idCliente == id_cliente
    assert recuperado.idRepresentante is None
    assert recuperado.idProducto == id_producto
    assert recuperado.idTipoProducto == id_tipo
    assert recuperado.fechaCreacion == FECHA
    assert recuperado.fechaCierre is None


def test_listarPorClienteEstadoYSinAsignar(db_temporal):
    id_cliente = _crear_cliente(db_temporal)
    id_representante = _crear_representante(db_temporal)
    id_tipo, id_producto = _crear_producto(db_temporal)
    repositorio = RepositorioTicket(db_temporal)

    id_nuevo = repositorio.insertar(
        _crear_ticket(id_cliente, id_producto, id_tipo)
    )
    id_asignado = repositorio.insertar(
        _crear_ticket(
            id_cliente,
            id_producto,
            id_tipo,
            titulo="Segundo ticket",
            prioridad=PRIORIDAD_MEDIA,
            idRepresentante=id_representante,
            estado=ESTADO_ASIGNADO,
        )
    )

    assert [
        ticket.idTicket
        for ticket in repositorio.listarPorCliente(id_cliente)
    ] == [id_nuevo, id_asignado]
    assert [
        ticket.idTicket
        for ticket in repositorio.listarPorEstado(ESTADO_NUEVO)
    ] == [id_nuevo]
    assert [
        ticket.idTicket for ticket in repositorio.listarSinAsignar()
    ] == [id_nuevo]
    assert [
        ticket.idTicket
        for ticket in repositorio.listarPorRepresentante(id_representante)
    ] == [id_asignado]


def test_asignarYActualizarEstado(db_temporal):
    id_cliente = _crear_cliente(db_temporal)
    id_representante = _crear_representante(db_temporal)
    id_tipo, id_producto = _crear_producto(db_temporal)
    repositorio = RepositorioTicket(db_temporal)

    id_ticket = repositorio.insertar(
        _crear_ticket(id_cliente, id_producto, id_tipo)
    )

    repositorio.asignar(id_ticket, id_representante)
    repositorio.actualizarEstado(id_ticket, ESTADO_ASIGNADO)
    recuperado = repositorio.buscarPorId(id_ticket)
    assert recuperado.idRepresentante == id_representante
    assert recuperado.estado == ESTADO_ASIGNADO

    repositorio.actualizarEstado(id_ticket, ESTADO_EN_PROGRESO)
    assert repositorio.buscarPorId(id_ticket).estado == ESTADO_EN_PROGRESO

    repositorio.actualizarEstado(
        id_ticket,
        ESTADO_CERRADO,
        fechaCierre=FECHA_CIERRE,
    )
    recuperado = repositorio.buscarPorId(id_ticket)
    assert recuperado.estado == ESTADO_CERRADO
    assert recuperado.fechaCierre == FECHA_CIERRE


def test_buscarTicketInexistenteDevuelveNone(db_temporal):
    repositorio = RepositorioTicket(db_temporal)

    assert repositorio.buscarPorId(999) is None
