import sqlite3

from src.db.mapeo import datosTipoProducto, filaATipoProducto
from src.excepciones import ErrorConflicto


class RepositorioTipoProducto:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar(self, tipoProducto) -> int:
        datos = datosTipoProducto(tipoProducto)

        if datos["id_tipo_producto"] is None:
            columnas = ("nombre", "descripcion")
            valores = (datos["nombre"], datos["descripcion"])
        else:
            columnas = ("id_tipo_producto", "nombre", "descripcion")
            valores = (
                datos["id_tipo_producto"],
                datos["nombre"],
                datos["descripcion"],
            )

        marcadores = ", ".join("?" for _ in columnas)
        sql = (
            f"INSERT INTO tipo_producto ({', '.join(columnas)}) "
            f"VALUES ({marcadores})"
        )

        try:
            cursor = self.conexion.execute(sql, valores)
        except sqlite3.IntegrityError as error:
            if "tipo_producto.nombre" in str(error):
                raise ErrorConflicto(
                    "Ya existe un tipo de producto con ese nombre."
                ) from error
            raise

        return cursor.lastrowid

    def buscarPorId(self, idTipoProducto):
        fila = self.conexion.execute(
            "SELECT * FROM tipo_producto WHERE id_tipo_producto = ?",
            (idTipoProducto,),
        ).fetchone()
        return filaATipoProducto(fila) if fila else None

    def listar(self):
        filas = self.conexion.execute(
            "SELECT * FROM tipo_producto ORDER BY nombre"
        ).fetchall()
        return [filaATipoProducto(fila) for fila in filas]
