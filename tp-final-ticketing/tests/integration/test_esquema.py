import sqlite3

import pytest

from src.db.conexion import abrirConexion
from src.db.esquema import crearEsquema

TABLAS_ESPERADAS = {
    "usuario",
    "cliente",
    "representante",
    "tipo_producto",
    "producto",
    "ticket",
    "hito",
    "mensaje",
    "historial",
    "alerta",
}

INDICES_ESPERADOS = {
    "idx_ticket_estado",
    "idx_ticket_cliente",
    "idx_ticket_representante",
    "idx_alerta_usuario_estado",
    "idx_hito_ticket",
    "idx_mensaje_ticket",
    "idx_historial_ticket",
    "idx_producto_tipo",
}


def _preparar_datos_ticket(conexion):
    conexion.execute(
        "INSERT INTO usuario (id_usuario, nombre, email, contrasena_hash, rol, activo) "
        "VALUES (1, 'Cliente', 'cliente@example.com', 'hash', 'CLIENTE', 1)"
    )
    conexion.execute(
        "INSERT INTO cliente (id_usuario, empresa) VALUES (1, 'ACME')"
    )
    conexion.execute(
        "INSERT INTO tipo_producto (id_tipo_producto, nombre) VALUES (1, 'Software')"
    )
    conexion.execute(
        "INSERT INTO producto (id_producto, nombre, version, id_tipo_producto) "
        "VALUES (1, 'Gestor', '1.0', 1)"
    )


def test_crearEsquema_esIdempotenteYCreaTablasIndices(tmp_path):
    conexion = abrirConexion(tmp_path / "ticketing.db")
    try:
        crearEsquema(conexion)
        crearEsquema(conexion)

        tablas = {
            fila["name"]
            for fila in conexion.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        indices = {
            fila["name"]
            for fila in conexion.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index'"
            )
        }

        assert TABLAS_ESPERADAS <= tablas
        assert INDICES_ESPERADOS <= indices
    finally:
        conexion.close()


def test_esquema_rechazaRolInvalido(tmp_path):
    conexion = abrirConexion(tmp_path / "ticketing.db")
    try:
        crearEsquema(conexion)
        with pytest.raises(sqlite3.IntegrityError):
            conexion.execute(
                "INSERT INTO usuario "
                "(nombre, email, contrasena_hash, rol, activo) "
                "VALUES ('Ana', 'ana@example.com', 'hash', 'ADMIN', 1)"
            )
    finally:
        conexion.close()


def test_esquema_exigeIntegridadReferencial(tmp_path):
    conexion = abrirConexion(tmp_path / "ticketing.db")
    try:
        crearEsquema(conexion)
        with pytest.raises(sqlite3.IntegrityError):
            conexion.execute(
                "INSERT INTO cliente (id_usuario, empresa) VALUES (999, 'ACME')"
            )
    finally:
        conexion.close()


def test_esquema_rechazaEstadoDeTicketInvalido(tmp_path):
    conexion = abrirConexion(tmp_path / "ticketing.db")
    try:
        crearEsquema(conexion)
        _preparar_datos_ticket(conexion)

        with pytest.raises(sqlite3.IntegrityError):
            conexion.execute(
                "INSERT INTO ticket "
                "(titulo, descripcion, estado, prioridad, fecha_creacion, "
                "id_cliente, id_producto, id_tipo_producto) "
                "VALUES ('Título', 'Descripción', 'INVALIDO', 'ALTA', "
                "'2026-01-01T10:00:00', 1, 1, 1)"
            )
    finally:
        conexion.close()


def test_esquema_rechazaPrioridadDeTicketInvalida(tmp_path):
    conexion = abrirConexion(tmp_path / "ticketing.db")
    try:
        crearEsquema(conexion)
        _preparar_datos_ticket(conexion)

        with pytest.raises(sqlite3.IntegrityError):
            conexion.execute(
                "INSERT INTO ticket "
                "(titulo, descripcion, estado, prioridad, fecha_creacion, "
                "id_cliente, id_producto, id_tipo_producto) "
                "VALUES ('Título', 'Descripción', 'NUEVO', 'URGENTE', "
                "'2026-01-01T10:00:00', 1, 1, 1)"
            )
    finally:
        conexion.close()
