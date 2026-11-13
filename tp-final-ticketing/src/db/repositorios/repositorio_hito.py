from datetime import datetime

from src.db.mapeo import datosHito, filaAHito
from src.excepciones import ErrorValidacion


class RepositorioHito:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar(self, hito) -> int:
        datos = datosHito(hito)

        columnas = (
            "id_ticket",
            "descripcion",
            "fecha_compromiso",
            "fecha_cumplimiento",
            "estado",
            "orden",
        )
        valores = (
            datos["id_ticket"],
            datos["descripcion"],
            datos["fecha_compromiso"],
            datos["fecha_cumplimiento"],
            datos["estado"],
            datos["orden"],
        )

        if datos["id_hito"] is not None:
            columnas = ("id_hito",) + columnas
            valores = (datos["id_hito"],) + valores

        marcadores = ", ".join("?" for _ in columnas)
        sql = f"INSERT INTO hito ({', '.join(columnas)}) VALUES ({marcadores})"
        cursor = self.conexion.execute(sql, valores)
        return cursor.lastrowid

    def buscarPorId(self, idHito):
        fila = self.conexion.execute(
            "SELECT * FROM hito WHERE id_hito = ?",
            (idHito,),
        ).fetchone()
        return filaAHito(fila) if fila else None

    def listarPorTicket(self, idTicket):
        filas = self.conexion.execute(
            "SELECT * FROM hito WHERE id_ticket = ? "
            "ORDER BY orden, id_hito",
            (idTicket,),
        ).fetchall()
        return [filaAHito(fila) for fila in filas]

    def actualizar(self, hito) -> None:
        if hito.idHito is None:
            raise ErrorValidacion("El hito debe tener un identificador.")
        datos = datosHito(hito)
        self.conexion.execute(
            "UPDATE hito SET descripcion = ?, fecha_compromiso = ?, "
            "fecha_cumplimiento = ?, estado = ?, orden = ? "
            "WHERE id_hito = ?",
            (
                datos["descripcion"],
                datos["fecha_compromiso"],
                datos["fecha_cumplimiento"],
                datos["estado"],
                datos["orden"],
                datos["id_hito"],
            ),
        )

    def listarVencidos(self, hoy=None):
        referencia = hoy or datetime.now()
        filas = self.conexion.execute(
            "SELECT * FROM hito "
            "WHERE estado <> 'CUMPLIDO' "
            "AND (estado = 'VENCIDO' OR fecha_compromiso < ?) "
            "ORDER BY fecha_compromiso, id_hito",
            (referencia.isoformat(),),
        ).fetchall()
        return [filaAHito(fila) for fila in filas]
