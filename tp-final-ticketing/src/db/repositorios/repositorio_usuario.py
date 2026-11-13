import sqlite3

from src.db.mapeo import datosUsuario, filaAUsuario
from src.excepciones import ErrorConflicto


class RepositorioUsuario:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar(self, usuario) -> int:
        datos = datosUsuario(usuario)

        if datos["id_usuario"] is None:
            columnas = ("nombre", "email", "contrasena_hash", "rol", "activo")
            valores = (
                datos["nombre"],
                datos["email"],
                datos["contrasena_hash"],
                datos["rol"],
                datos["activo"],
            )
        else:
            columnas = (
                "id_usuario",
                "nombre",
                "email",
                "contrasena_hash",
                "rol",
                "activo",
            )
            valores = (
                datos["id_usuario"],
                datos["nombre"],
                datos["email"],
                datos["contrasena_hash"],
                datos["rol"],
                datos["activo"],
            )

        marcadores = ", ".join("?" for _ in columnas)
        sql = (
            f"INSERT INTO usuario ({', '.join(columnas)}) "
            f"VALUES ({marcadores})"
        )

        try:
            cursor = self.conexion.execute(sql, valores)
        except sqlite3.IntegrityError as error:
            if "usuario.email" in str(error):
                raise ErrorConflicto(
                    "Ya existe un usuario con ese email."
                ) from error
            raise

        return cursor.lastrowid

    def buscarPorId(self, idUsuario):
        fila = self.conexion.execute(
            "SELECT * FROM usuario WHERE id_usuario = ?",
            (idUsuario,),
        ).fetchone()
        return filaAUsuario(fila) if fila else None

    def buscarPorEmail(self, email):
        fila = self.conexion.execute(
            "SELECT * FROM usuario WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
        return filaAUsuario(fila) if fila else None

    def listarActivos(self):
        filas = self.conexion.execute(
            "SELECT * FROM usuario WHERE activo = 1 ORDER BY nombre"
        ).fetchall()
        return [filaAUsuario(fila) for fila in filas]

    def listarPorRol(self, rol):
        filas = self.conexion.execute(
            "SELECT * FROM usuario WHERE rol = ? ORDER BY nombre",
            (rol,),
        ).fetchall()
        return [filaAUsuario(fila) for fila in filas]

    def actualizarActivo(self, idUsuario, activo) -> None:
        self.conexion.execute(
            "UPDATE usuario SET activo = ? WHERE id_usuario = ?",
            (int(activo), idUsuario),
        )
