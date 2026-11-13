import sqlite3

from src.db.mapeo import datosRepresentante, filaARepresentante
from src.excepciones import ErrorConflicto, ErrorValidacion


class RepositorioRepresentante:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar(self, representante) -> int:
        datos = datosRepresentante(representante)
        if datos["id_usuario"] is None:
            raise ErrorValidacion(
                "El representante debe tener un usuario asociado."
            )

        try:
            self.conexion.execute(
                "INSERT INTO representante (id_usuario, legajo, especialidad) "
                "VALUES (?, ?, ?)",
                (
                    datos["id_usuario"],
                    datos["legajo"],
                    datos["especialidad"],
                ),
            )
        except sqlite3.IntegrityError as error:
            if "representante.legajo" in str(error):
                raise ErrorConflicto(
                    "Ya existe un representante con ese legajo."
                ) from error
            raise

        return datos["id_usuario"]

    def buscarPorId(self, idUsuario):
        fila = self.conexion.execute(
            "SELECT u.*, r.legajo, r.especialidad "
            "FROM representante r "
            "JOIN usuario u ON u.id_usuario = r.id_usuario "
            "WHERE r.id_usuario = ?",
            (idUsuario,),
        ).fetchone()
        return filaARepresentante(fila) if fila else None

    def buscarPorLegajo(self, legajo):
        fila = self.conexion.execute(
            "SELECT u.*, r.legajo, r.especialidad "
            "FROM representante r "
            "JOIN usuario u ON u.id_usuario = r.id_usuario "
            "WHERE r.legajo = ?",
            (legajo,),
        ).fetchone()
        return filaARepresentante(fila) if fila else None

    def listarActivos(self):
        filas = self.conexion.execute(
            "SELECT u.*, r.legajo, r.especialidad "
            "FROM representante r "
            "JOIN usuario u ON u.id_usuario = r.id_usuario "
            "WHERE u.activo = 1 "
            "ORDER BY u.nombre"
        ).fetchall()
        return [filaARepresentante(fila) for fila in filas]
