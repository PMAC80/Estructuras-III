from datetime import datetime

from src.db.repositorios.repositorio_alerta import RepositorioAlerta
from src.db.repositorios.repositorio_usuario import RepositorioUsuario
from src.models.estados import ROL_REPRESENTANTE
from src.models.usuario import Usuario

CLAVE = "ClaveSegura123!"
FECHA = datetime(2026, 1, 10, 9, 0)
FECHA_POSTERIOR = datetime(2026, 1, 10, 10, 0)


def _crear_usuario(conexion, email, nombre="Luis"):
    repositorio = RepositorioUsuario(conexion)
    return repositorio.insertar(
        Usuario.crear(
            None,
            nombre,
            email,
            CLAVE,
            ROL_REPRESENTANTE,
        )
    )


def test_insertarYListarAlerta(db_temporal):
    id_usuario = _crear_usuario(db_temporal, "luis@example.com")
    repositorio = RepositorioAlerta(db_temporal)

    id_alerta = repositorio.insertar(
        id_usuario,
        None,
        "TICKET_SIN_ASIGNAR",
        "ALTA",
        "Ticket sin asignar",
        fechaCreacion=FECHA,
    )

    alertas = repositorio.listarPorUsuario(id_usuario)
    assert len(alertas) == 1
    alerta = alertas[0]
    assert alerta.idAlerta == id_alerta
    assert alerta.idUsuario == id_usuario
    assert alerta.idTicket is None
    assert alerta.tipo == "TICKET_SIN_ASIGNAR"
    assert alerta.prioridad == "ALTA"
    assert alerta.mensaje == "Ticket sin asignar"
    assert alerta.estado == "PENDIENTE"
    assert alerta.fechaCreacion == FECHA


def test_listarPendientesYMarcarLeida(db_temporal):
    id_usuario = _crear_usuario(db_temporal, "luis@example.com")
    repositorio = RepositorioAlerta(db_temporal)
    id_primera = repositorio.insertar(
        id_usuario,
        None,
        "MENSAJE_NUEVO",
        "MEDIA",
        "Mensaje nuevo",
        fechaCreacion=FECHA,
    )
    id_segunda = repositorio.insertar(
        id_usuario,
        None,
        "HITO_VENCIDO",
        "ALTA",
        "Hito vencido",
        fechaCreacion=FECHA_POSTERIOR,
    )

    repositorio.marcarLeida(id_primera)

    pendientes = repositorio.listarPendientes(id_usuario)
    assert [alerta.idAlerta for alerta in pendientes] == [id_segunda]

    todas = repositorio.listarPorUsuario(id_usuario)
    assert [alerta.idAlerta for alerta in todas] == [id_segunda, id_primera]
    assert {alerta.estado for alerta in todas} == {"PENDIENTE", "LEIDA"}


def test_alertasFiltradasPorUsuario(db_temporal):
    id_usuario = _crear_usuario(db_temporal, "luis@example.com")
    id_otro_usuario = _crear_usuario(
        db_temporal,
        "marta@example.com",
        nombre="Marta",
    )
    repositorio = RepositorioAlerta(db_temporal)
    repositorio.insertar(
        id_otro_usuario,
        None,
        "REAPERTURA",
        "ALTA",
        "Ticket reabierto",
        fechaCreacion=FECHA,
    )

    assert repositorio.listarPorUsuario(id_usuario) == []
    assert len(repositorio.listarPorUsuario(id_otro_usuario)) == 1
