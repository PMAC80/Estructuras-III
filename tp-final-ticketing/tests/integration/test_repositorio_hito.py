from datetime import datetime

from src.db.repositorios.repositorio_cliente import RepositorioCliente
from src.db.repositorios.repositorio_hito import RepositorioHito
from src.db.repositorios.repositorio_producto import RepositorioProducto
from src.db.repositorios.repositorio_ticket import RepositorioTicket
from src.db.repositorios.repositorio_tipo_producto import (
    RepositorioTipoProducto,
)
from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.models.cliente import Cliente
from src.models.estados import (
    ESTADO_HITO_CUMPLIDO,
    ESTADO_HITO_PENDIENTE,
    ESTADO_HITO_VENCIDO,
    PRIORIDAD_ALTA,
    ROL_CLIENTE,
)
from src.models.hito import Hito
from src.models.producto import Producto
from src.models.ticket import Ticket
from src.models.tipo_producto import TipoProducto
from src.models.usuario import Usuario

CLAVE = "ClaveSegura123!"
FECHA_PASADA = datetime(2026, 1, 1, 9, 0)
HOY = datetime(2026, 1, 10, 9, 0)
FECHA_FUTURA = datetime(2026, 2, 1, 9, 0)


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
    return repositorio_tickets.insertar(
        Ticket(
            "Título",
            "Descripción",
            PRIORIDAD_ALTA,
            id_cliente,
            id_producto,
            id_tipo,
            fechaCreacion=HOY,
        )
    )


def test_insertarYBuscarHito(db_temporal):
    id_ticket = _crear_ticket(db_temporal)
    repositorio = RepositorioHito(db_temporal)
    hito = Hito(
        id_ticket,
        "Diagnóstico inicial",
        FECHA_FUTURA,
        orden=1,
    )

    id_hito = repositorio.insertar(hito)
    recuperado = repositorio.buscarPorId(id_hito)

    assert recuperado.idHito == id_hito
    assert recuperado.idTicket == id_ticket
    assert recuperado.descripcion == "Diagnóstico inicial"
    assert recuperado.fechaCompromiso == FECHA_FUTURA
    assert recuperado.estado == ESTADO_HITO_PENDIENTE
    assert recuperado.orden == 1


def test_listarHitosPorTicketOrdenados(db_temporal):
    id_ticket = _crear_ticket(db_temporal)
    repositorio = RepositorioHito(db_temporal)
    id_segundo = repositorio.insertar(
        Hito(id_ticket, "Segundo paso", FECHA_FUTURA, orden=2)
    )
    id_primero = repositorio.insertar(
        Hito(id_ticket, "Primer paso", FECHA_FUTURA, orden=1)
    )

    hitos = repositorio.listarPorTicket(id_ticket)

    assert [hito.idHito for hito in hitos] == [id_primero, id_segundo]


def test_actualizarHitoCompletado(db_temporal):
    id_ticket = _crear_ticket(db_temporal)
    repositorio = RepositorioHito(db_temporal)
    hito = Hito(id_ticket, "Diagnóstico inicial", FECHA_FUTURA)
    hito.idHito = repositorio.insertar(hito)

    hito.completar(HOY)
    repositorio.actualizar(hito)

    recuperado = repositorio.buscarPorId(hito.idHito)
    assert recuperado.estado == ESTADO_HITO_CUMPLIDO
    assert recuperado.fechaCumplimiento == HOY


def test_listarHitosVencidos(db_temporal):
    id_ticket = _crear_ticket(db_temporal)
    repositorio = RepositorioHito(db_temporal)

    id_vencido = repositorio.insertar(
        Hito(id_ticket, "Vencido", FECHA_PASADA, orden=1)
    )
    hito_cumplido = Hito(id_ticket, "Cumplido", FECHA_PASADA, orden=2)
    hito_cumplido.idHito = repositorio.insertar(hito_cumplido)
    hito_cumplido.completar(HOY)
    repositorio.actualizar(hito_cumplido)
    repositorio.insertar(
        Hito(id_ticket, "Futuro", FECHA_FUTURA, orden=3)
    )

    vencidos = repositorio.listarVencidos(HOY)

    assert [hito.idHito for hito in vencidos] == [id_vencido]


def test_listarVencidosIncluyeEstadoVencido(db_temporal):
    id_ticket = _crear_ticket(db_temporal)
    repositorio = RepositorioHito(db_temporal)

    id_vencido = repositorio.insertar(
        Hito(
            id_ticket,
            "Marcado vencido",
            FECHA_FUTURA,
            estado=ESTADO_HITO_VENCIDO,
        )
    )

    assert [hito.idHito for hito in repositorio.listarVencidos(HOY)] == [
        id_vencido
    ]
