from datetime import datetime, timedelta

import pytest

from src.controller.control_notificaciones import ControlNotificaciones
from src.controller.control_usuario import ControlUsuario
from src.db.repositorios.repositorio_alerta import RepositorioAlerta
from src.db.repositorios.repositorio_cliente import RepositorioCliente
from src.db.repositorios.repositorio_hito import RepositorioHito
from src.db.repositorios.repositorio_producto import RepositorioProducto
from src.db.repositorios.repositorio_representante import (
    RepositorioRepresentante,
)
from src.db.repositorios.repositorio_ticket import RepositorioTicket
from src.db.repositorios.repositorio_tipo_producto import (
    RepositorioTipoProducto,
)
from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.excepciones import (
    ErrorNoEncontrado,
    ErrorPermiso,
    ErrorValidacion,
)
from src.models.estados import (
    ESTADO_ASIGNADO,
    ESTADO_NUEVO,
    ESTADO_REABIERTO,
    PRIORIDAD_ALTA,
    PRIORIDAD_MEDIA,
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


def _crear_control(conexion, momento=FECHA):
    usuarios = RepositorioUsuario(conexion)
    clientes = RepositorioCliente(conexion)
    representantes = RepositorioRepresentante(conexion)
    control_usuario = ControlUsuario(
        conexion,
        usuarios,
        clientes,
        representantes,
    )
    control = ControlNotificaciones(
        conexion,
        RepositorioAlerta(conexion),
        RepositorioTicket(conexion),
        usuarios,
        representantes,
        control_usuario,
        reloj=lambda: momento,
    )
    return control, control_usuario, usuarios, representantes


def _registrar_cliente(control_usuario, email="ana@example.com", nombre="Ana"):
    return control_usuario.registrar(
        nombre,
        email,
        CLAVE,
        ROL_CLIENTE,
    )


def _registrar_representante(
    control_usuario,
    email="luis@example.com",
    nombre="Luis",
    legajo="LEG-001",
):
    return control_usuario.registrar(
        nombre,
        email,
        CLAVE,
        ROL_REPRESENTANTE,
        legajo=legajo,
    )


def _registrar_representante_inactivo(
    conexion,
    usuarios,
    representantes,
    email="inactivo@example.com",
    nombre="Inactivo",
    legajo="LEG-INA",
):
    usuario = Usuario.crear(
        None,
        nombre,
        email,
        CLAVE,
        ROL_REPRESENTANTE,
        activo=False,
    )
    id_usuario = usuarios.insertar(usuario)
    representantes.insertar(
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


def _crear_producto(conexion, tipo="Software", producto="Gestor"):
    id_tipo = RepositorioTipoProducto(conexion).insertar(
        TipoProducto(None, tipo)
    )
    id_producto = RepositorioProducto(conexion).insertar(
        Producto(None, producto, "1.0", id_tipo)
    )
    return id_tipo, id_producto


def _crear_ticket(
    conexion,
    id_cliente,
    id_tipo,
    id_producto,
    id_representante=None,
    estado=ESTADO_NUEVO,
    fecha_creacion=FECHA,
    titulo="Ticket",
):
    return RepositorioTicket(conexion).insertar(
        Ticket(
            titulo,
            "Descripción",
            PRIORIDAD_ALTA,
            id_cliente,
            id_producto,
            id_tipo,
            idRepresentante=id_representante,
            estado=estado,
            fechaCreacion=fecha_creacion,
        )
    )


def test_generarAlertaPersistePendiente(db_temporal):
    control, control_usuario, _, _ = _crear_control(db_temporal)
    representante = _registrar_representante(control_usuario)

    id_alerta = control.generarAlerta(
        representante.idUsuario,
        None,
        "MENSAJE_NUEVO",
        PRIORIDAD_MEDIA,
        "Tiene un mensaje nuevo.",
    )

    alerta = RepositorioAlerta(db_temporal).buscarPorId(id_alerta)
    assert alerta.idUsuario == representante.idUsuario
    assert alerta.idTicket is None
    assert alerta.tipo == "MENSAJE_NUEVO"
    assert alerta.prioridad == PRIORIDAD_MEDIA
    assert alerta.estado == "PENDIENTE"
    assert alerta.fechaCreacion == FECHA


def test_generarAlertaValidaPrioridadYDestinatario(db_temporal):
    control, control_usuario, _, _ = _crear_control(db_temporal)
    representante = _registrar_representante(control_usuario)

    with pytest.raises(ErrorValidacion):
        control.generarAlerta(
            representante.idUsuario,
            None,
            "MENSAJE_NUEVO",
            "URGENTE",
            "Mensaje",
        )

    with pytest.raises(ErrorNoEncontrado):
        control.generarAlerta(
            999,
            None,
            "MENSAJE_NUEVO",
            PRIORIDAD_MEDIA,
            "Mensaje",
        )


def test_listarAlertasDelUsuarioActual(db_temporal):
    control, control_usuario, _, _ = _crear_control(db_temporal)
    representante = _registrar_representante(control_usuario)
    otro = _registrar_representante(
        control_usuario,
        email="marta@example.com",
        nombre="Marta",
        legajo="LEG-002",
    )
    control.generarAlerta(
        representante.idUsuario,
        None,
        "MENSAJE_NUEVO",
        PRIORIDAD_MEDIA,
        "Para Luis",
    )
    control.generarAlerta(
        otro.idUsuario,
        None,
        "MENSAJE_NUEVO",
        PRIORIDAD_MEDIA,
        "Para Marta",
    )

    control_usuario.login("luis@example.com", CLAVE)
    alertas = control.listarAlertas()

    assert [alerta.idUsuario for alerta in alertas] == [
        representante.idUsuario
    ]
    assert alertas[0].mensaje == "Para Luis"


def test_listarAlertasPorRol(db_temporal):
    control, control_usuario, _, _ = _crear_control(db_temporal)
    representante = _registrar_representante(control_usuario)
    cliente = _registrar_cliente(control_usuario)
    control.generarAlerta(
        representante.idUsuario,
        None,
        "HITO_VENCIDO",
        PRIORIDAD_ALTA,
        "Para representantes",
    )
    control.generarAlerta(
        cliente.idUsuario,
        None,
        "CAMBIO_ESTADO",
        PRIORIDAD_MEDIA,
        "Para clientes",
    )
    control_usuario.login("luis@example.com", CLAVE)

    alertas = control.listarAlertasDeRol(ROL_REPRESENTANTE)

    assert [alerta.idUsuario for alerta in alertas] == [
        representante.idUsuario
    ]
    with pytest.raises(ErrorPermiso):
        control.listarAlertasDeRol(ROL_CLIENTE)


def test_marcarLeidaNoEliminaYValidaPropietario(db_temporal):
    control, control_usuario, _, _ = _crear_control(db_temporal)
    representante = _registrar_representante(control_usuario)
    otro = _registrar_representante(
        control_usuario,
        email="marta@example.com",
        nombre="Marta",
        legajo="LEG-002",
    )
    id_propia = control.generarAlerta(
        representante.idUsuario,
        None,
        "MENSAJE_NUEVO",
        PRIORIDAD_MEDIA,
        "Propia",
    )
    id_ajena = control.generarAlerta(
        otro.idUsuario,
        None,
        "MENSAJE_NUEVO",
        PRIORIDAD_MEDIA,
        "Ajena",
    )
    control_usuario.login("luis@example.com", CLAVE)

    control.marcarLeida(id_propia)

    alerta = RepositorioAlerta(db_temporal).buscarPorId(id_propia)
    assert alerta.estado == "LEIDA"
    assert RepositorioAlerta(db_temporal).buscarPorId(id_propia) is not None
    assert control.listarAlertas() == []
    assert len(control.listarAlertas(soloPendientes=False)) == 1

    with pytest.raises(ErrorPermiso):
        control.marcarLeida(id_ajena)
    with pytest.raises(ErrorNoEncontrado):
        control.marcarLeida(999)


def test_notificarCambioEstadoGeneraAlertaAlCliente(db_temporal):
    control, control_usuario, _, _ = _crear_control(db_temporal)
    cliente = _registrar_cliente(control_usuario)
    id_tipo, id_producto = _crear_producto(db_temporal)
    id_ticket = _crear_ticket(
        db_temporal,
        cliente.idUsuario,
        id_tipo,
        id_producto,
    )
    ticket = RepositorioTicket(db_temporal).buscarPorId(id_ticket)

    control.notificarCambioEstado(
        ticket,
        ESTADO_NUEVO,
        ESTADO_ASIGNADO,
    )

    alertas = RepositorioAlerta(db_temporal).listarPorUsuario(
        cliente.idUsuario
    )
    assert len(alertas) == 1
    assert alertas[0].tipo == "CAMBIO_ESTADO"
    assert alertas[0].idTicket == id_ticket


def test_notificarMensajeGeneraAlertaAlDestinatario(db_temporal):
    control, control_usuario, _, _ = _crear_control(db_temporal)
    cliente = _registrar_cliente(control_usuario)
    representante = _registrar_representante(control_usuario)
    id_tipo, id_producto = _crear_producto(db_temporal)
    id_ticket = _crear_ticket(
        db_temporal,
        cliente.idUsuario,
        id_tipo,
        id_producto,
        id_representante=representante.idUsuario,
        estado=ESTADO_ASIGNADO,
    )

    control.notificarMensaje(id_ticket, representante.idUsuario)

    alertas = RepositorioAlerta(db_temporal).listarPorUsuario(
        representante.idUsuario
    )
    assert len(alertas) == 1
    assert alertas[0].tipo == "MENSAJE_NUEVO"
    assert alertas[0].idTicket == id_ticket


def test_notificarReaperturaAlRepresentanteAsignado(db_temporal):
    control, control_usuario, _, _ = _crear_control(db_temporal)
    cliente = _registrar_cliente(control_usuario)
    representante = _registrar_representante(control_usuario)
    id_tipo, id_producto = _crear_producto(db_temporal)
    id_ticket = _crear_ticket(
        db_temporal,
        cliente.idUsuario,
        id_tipo,
        id_producto,
        id_representante=representante.idUsuario,
        estado=ESTADO_REABIERTO,
    )
    ticket = RepositorioTicket(db_temporal).buscarPorId(id_ticket)

    control.notificarReapertura(ticket, "El problema persiste.")

    alertas = RepositorioAlerta(db_temporal).listarPorUsuario(
        representante.idUsuario
    )
    assert len(alertas) == 1
    assert alertas[0].tipo == "REAPERTURA"
    assert "persiste" in alertas[0].mensaje


def test_notificarHitoVencidoAlRepresentante(db_temporal):
    control, control_usuario, _, _ = _crear_control(db_temporal)
    cliente = _registrar_cliente(control_usuario)
    representante = _registrar_representante(control_usuario)
    id_tipo, id_producto = _crear_producto(db_temporal)
    id_ticket = _crear_ticket(
        db_temporal,
        cliente.idUsuario,
        id_tipo,
        id_producto,
        id_representante=representante.idUsuario,
        estado=ESTADO_ASIGNADO,
    )
    hito = Hito(id_ticket, "Diagnóstico", FECHA - timedelta(days=1))
    hito.idHito = RepositorioHito(db_temporal).insertar(hito)
    ticket = RepositorioTicket(db_temporal).buscarPorId(id_ticket)

    control.notificarHitoVencido(ticket, hito)

    alertas = RepositorioAlerta(db_temporal).listarPorUsuario(
        representante.idUsuario
    )
    assert len(alertas) == 1
    assert alertas[0].tipo == "HITO_VENCIDO"
    assert alertas[0].prioridad == PRIORIDAD_ALTA


def test_verificarTicketsSinAsignarGeneraAlertaTras24h(db_temporal):
    control, control_usuario, usuarios, representantes = _crear_control(
        db_temporal
    )
    cliente = _registrar_cliente(control_usuario)
    representante = _registrar_representante(control_usuario)
    inactivo = _registrar_representante_inactivo(
        db_temporal,
        usuarios,
        representantes,
    )
    id_tipo, id_producto = _crear_producto(db_temporal)
    id_viejo = _crear_ticket(
        db_temporal,
        cliente.idUsuario,
        id_tipo,
        id_producto,
        fecha_creacion=FECHA - timedelta(hours=25),
        titulo="Viejo",
    )
    id_reciente = _crear_ticket(
        db_temporal,
        cliente.idUsuario,
        id_tipo,
        id_producto,
        fecha_creacion=FECHA - timedelta(hours=1),
        titulo="Reciente",
    )

    control.verificarTicketsSinAsignar()

    alertas_representante = RepositorioAlerta(
        db_temporal
    ).listarPorUsuario(representante.idUsuario)
    assert len(alertas_representante) == 1
    assert alertas_representante[0].tipo == "TICKET_SIN_ASIGNAR"
    assert alertas_representante[0].idTicket == id_viejo
    assert alertas_representante[0].idTicket != id_reciente
    assert (
        RepositorioAlerta(db_temporal).listarPorUsuario(inactivo) == []
    )
