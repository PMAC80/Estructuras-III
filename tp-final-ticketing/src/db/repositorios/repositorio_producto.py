import sqlite3

from src.db.mapeo import datosProducto, filaAProducto
from src.excepciones import ErrorConflicto


class RepositorioProducto:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar(self, producto) -> int:
        datos = datosProducto(producto)

        if datos["id_producto"] is None:
            columnas = ("nombre", "version", "id_tipo_producto")
            valores = (
                datos["nombre"],
                datos["version"],
                datos["id_tipo_producto"],
            )
        else:
            columnas = ("id_producto", "nombre", "version", "id_tipo_producto")
            valores = (
                datos["id_producto"],
                datos["nombre"],
                datos["version"],
                datos["id_tipo_producto"],
            )

        marcadores = ", ".join("?" for _ in columnas)
        sql = (
            f"INSERT INTO producto ({', '.join(columnas)}) "
            f"VALUES ({marcadores})"
        )

        try:
            cursor = self.conexion.execute(sql, valores)
        except sqlite3.IntegrityError as error:
            if "producto.nombre" in str(error):
                raise ErrorConflicto(
                    "Ya existe un producto con ese nombre y versión "
                    "para el tipo indicado."
                ) from error
            raise

        return cursor.lastrowid

    def buscarPorId(self, idProducto):
        fila = self.conexion.execute(
            "SELECT * FROM producto WHERE id_producto = ?",
            (idProducto,),
        ).fetchone()
        return filaAProducto(fila) if fila else None

    def listarPorTipo(self, idTipoProducto):
        filas = self.conexion.execute(
            "SELECT * FROM producto WHERE id_tipo_producto = ? "
            "ORDER BY id_producto",
            (idTipoProducto,),
        ).fetchall()
        return [filaAProducto(fila) for fila in filas]
