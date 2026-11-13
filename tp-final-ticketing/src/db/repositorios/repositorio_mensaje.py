from src.db.mapeo import datosMensaje, filaAMensaje


class RepositorioMensaje:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar(self, mensaje) -> int:
        datos = datosMensaje(mensaje)

        columnas = (
            "id_ticket",
            "id_autor",
            "contenido",
            "fecha_envio",
            "leido",
        )
        valores = (
            datos["id_ticket"],
            datos["id_autor"],
            datos["contenido"],
            datos["fecha_envio"],
            datos["leido"],
        )

        if datos["id_mensaje"] is not None:
            columnas = ("id_mensaje",) + columnas
            valores = (datos["id_mensaje"],) + valores

        marcadores = ", ".join("?" for _ in columnas)
        sql = (
            f"INSERT INTO mensaje ({', '.join(columnas)}) "
            f"VALUES ({marcadores})"
        )
        cursor = self.conexion.execute(sql, valores)
        return cursor.lastrowid

    def buscarPorId(self, idMensaje):
        fila = self.conexion.execute(
            "SELECT * FROM mensaje WHERE id_mensaje = ?",
            (idMensaje,),
        ).fetchone()
        return filaAMensaje(fila) if fila else None

    def listarPorTicket(self, idTicket):
        filas = self.conexion.execute(
            "SELECT * FROM mensaje WHERE id_ticket = ? "
            "ORDER BY fecha_envio, id_mensaje",
            (idTicket,),
        ).fetchall()
        return [filaAMensaje(fila) for fila in filas]

    def marcarLeido(self, idMensaje) -> None:
        self.conexion.execute(
            "UPDATE mensaje SET leido = 1 WHERE id_mensaje = ?",
            (idMensaje,),
        )
