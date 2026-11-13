from datetime import datetime

from src.db.mapeo import (
    datosAlerta,
    datosCliente,
    datosHistorial,
    datosHito,
    datosMensaje,
    datosProducto,
    datosRepresentante,
    datosTicket,
    datosTipoProducto,
    datosUsuario,
    filaAAlerta,
    filaACliente,
    filaAHistorial,
    filaAHito,
    filaAMensaje,
    filaAProducto,
    filaARepresentante,
    filaATicket,
    filaATipoProducto,
    filaAUsuario,
)
from src.db.registros import RegistroAlerta, RegistroHistorial
from src.models.cliente import Cliente
from src.models.estados import (
    ESTADO_ASIGNADO,
    ESTADO_HITO_PENDIENTE,
    PRIORIDAD_ALTA,
    ROL_CLIENTE,
    ROL_REPRESENTANTE,
)
from src.models.hito import Hito
from src.models.mensaje import Mensaje
from src.models.producto import Producto
from src.models.representante import Representante
from src.models.seguridad import generarHash
from src.models.ticket import Ticket
from src.models.tipo_producto import TipoProducto
from src.models.usuario import Usuario

FECHA = datetime(2026, 1, 10, 9, 30)
HASH = generarHash("ClaveSegura123!")


def test_roundtrip_usuario():
    original = Usuario(1, "Ana", "ana@example.com", HASH, ROL_CLIENTE, True)

    recuperado = filaAUsuario(datosUsuario(original))

    assert recuperado.idUsuario == 1
    assert recuperado.nombre == "Ana"
    assert recuperado.email == "ana@example.com"
    assert recuperado.contrasenaHash == HASH
    assert recuperado.rol == ROL_CLIENTE
    assert recuperado.activo is True


def test_roundtrip_cliente():
    original = Cliente(
        1,
        "Ana",
        "ana@example.com",
        HASH,
        empresa="ACME",
        telefono="123456",
    )

    recuperado = filaACliente(datosCliente(original))

    assert isinstance(recuperado, Cliente)
    assert recuperado.idUsuario == 1
    assert recuperado.rol == ROL_CLIENTE
    assert recuperado.empresa == "ACME"
    assert recuperado.telefono == "123456"
    assert recuperado.activo is True


def test_roundtrip_representante():
    original = Representante(
        2,
        "Luis",
        "luis@example.com",
        HASH,
        legajo="REP-001",
        especialidad="Redes",
        activo=False,
    )

    recuperado = filaARepresentante(datosRepresentante(original))

    assert isinstance(recuperado, Representante)
    assert recuperado.idUsuario == 2
    assert recuperado.rol == ROL_REPRESENTANTE
    assert recuperado.legajo == "REP-001"
    assert recuperado.especialidad == "Redes"
    assert recuperado.activo is False


def test_roundtrip_tipoProducto():
    original = TipoProducto(1, "Software", "Aplicaciones")

    recuperado = filaATipoProducto(datosTipoProducto(original))

    assert recuperado.idTipoProducto == 1
    assert recuperado.nombre == "Software"
    assert recuperado.descripcion == "Aplicaciones"


def test_roundtrip_producto():
    original = Producto(10, "Gestor", "1.0", idTipoProducto=1)

    recuperado = filaAProducto(datosProducto(original))

    assert recuperado.idProducto == 10
    assert recuperado.nombre == "Gestor"
    assert recuperado.version == "1.0"
    assert recuperado.idTipoProducto == 1


def test_roundtrip_ticket():
    original = Ticket(
        "Error al iniciar sesión",
        "El sistema no permite ingresar.",
        PRIORIDAD_ALTA,
        1,
        10,
        1,
        idTicket=5,
        idRepresentante=2,
        estado=ESTADO_ASIGNADO,
        fechaCreacion=FECHA,
    )

    recuperado = filaATicket(datosTicket(original))

    assert recuperado.idTicket == 5
    assert recuperado.titulo == "Error al iniciar sesión"
    assert recuperado.estado == ESTADO_ASIGNADO
    assert recuperado.prioridad == PRIORIDAD_ALTA
    assert recuperado.idCliente == 1
    assert recuperado.idRepresentante == 2
    assert recuperado.idProducto == 10
    assert recuperado.idTipoProducto == 1
    assert recuperado.fechaCreacion == FECHA
    assert recuperado.fechaCierre is None


def test_roundtrip_hito():
    original = Hito(
        1,
        "Diagnóstico inicial",
        FECHA,
        idHito=3,
        orden=2,
        estado=ESTADO_HITO_PENDIENTE,
    )

    recuperado = filaAHito(datosHito(original))

    assert recuperado.idHito == 3
    assert recuperado.idTicket == 1
    assert recuperado.descripcion == "Diagnóstico inicial"
    assert recuperado.fechaCompromiso == FECHA
    assert recuperado.orden == 2
    assert recuperado.estado == ESTADO_HITO_PENDIENTE
    assert recuperado.fechaCumplimiento is None


def test_roundtrip_mensaje():
    original = Mensaje(
        1,
        2,
        "Estamos revisando el caso.",
        idMensaje=7,
        fechaEnvio=FECHA,
        leido=True,
    )

    recuperado = filaAMensaje(datosMensaje(original))

    assert recuperado.idMensaje == 7
    assert recuperado.idTicket == 1
    assert recuperado.idAutor == 2
    assert recuperado.contenido == "Estamos revisando el caso."
    assert recuperado.fechaEnvio == FECHA
    assert recuperado.leido is True


def test_roundtrip_historial():
    original = RegistroHistorial(
        1,
        1,
        2,
        "CREACION",
        None,
        "NUEVO",
        "Ticket creado",
        FECHA,
    )

    recuperado = filaAHistorial(datosHistorial(original))

    assert recuperado == original


def test_roundtrip_alerta():
    original = RegistroAlerta(
        1,
        2,
        1,
        "TICKET_SIN_ASIGNAR",
        "ALTA",
        "Ticket sin asignar",
        "PENDIENTE",
        FECHA,
    )

    recuperado = filaAAlerta(datosAlerta(original))

    assert recuperado == original
