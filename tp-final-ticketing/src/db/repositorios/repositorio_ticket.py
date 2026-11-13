from src.db.mapeo import datosTicket, filaATicket


class RepositorioTicket:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar(self, ticket) -> int:
        datos = datosTicket(ticket)

        columnas = (
            "titulo",
            "descripcion",
            "estado",
            "prioridad",
            "fecha_creacion",
            "fecha_cierre",
            "id_cliente",
            "id_representante",
            "id_producto",
            "id_tipo_producto",
        )
        valores = (
            datos["titulo"],
            datos["descripcion"],
            datos["estado"],
            datos["prioridad"],
            datos["fecha_creacion"],
            datos["fecha_cierre"],
            datos["id_cliente"],
            datos["id_representante"],
            datos["id_producto"],
            datos["id_tipo_producto"],
        )

        if datos["id_ticket"] is not None:
            columnas = ("id_ticket",) + columnas
            valores = (datos["id_ticket"],) + valores

        marcadores = ", ".join("?" for _ in columnas)
        sql = (
            f"INSERT INTO ticket ({', '.join(columnas)}) "
            f"VALUES ({marcadores})"
        )
        cursor = self.conexion.execute(sql, valores)
        return cursor.lastrowid

    def buscarPorId(self, idTicket):
        fila = self.conexion.execute(
            "SELECT * FROM ticket WHERE id_ticket = ?",
            (idTicket,),
        ).fetchone()
        return filaATicket(fila) if fila else None

    def listarPorCliente(self, idCliente):
        filas = self.conexion.execute(
            "SELECT * FROM ticket WHERE id_cliente = ? ORDER BY id_ticket",
            (idCliente,),
        ).fetchall()
        return [filaATicket(fila) for fila in filas]

    def listarPorRepresentante(self, idRepresentante):
        filas = self.conexion.execute(
            "SELECT * FROM ticket WHERE id_representante = ? "
            "ORDER BY id_ticket",
            (idRepresentante,),
        ).fetchall()
        return [filaATicket(fila) for fila in filas]

    def listarPorEstado(self, estado):
        filas = self.conexion.execute(
            "SELECT * FROM ticket WHERE estado = ? ORDER BY id_ticket",
            (estado,),
        ).fetchall()
        return [filaATicket(fila) for fila in filas]

    def listarSinAsignar(self):
        filas = self.conexion.execute(
            "SELECT * FROM ticket "
            "WHERE estado = 'NUEVO' AND id_representante IS NULL "
            "ORDER BY id_ticket"
        ).fetchall()
        return [filaATicket(fila) for fila in filas]

    def asignar(self, idTicket, idRepresentante) -> None:
        self.conexion.execute(
            "UPDATE ticket SET id_representante = ? WHERE id_ticket = ?",
            (idRepresentante, idTicket),
        )

    def actualizarEstado(self, idTicket, estado, fechaCierre=None) -> None:
        fecha_texto = fechaCierre.isoformat() if fechaCierre else None
        self.conexion.execute(
            "UPDATE ticket SET estado = ?, fecha_cierre = ? "
            "WHERE id_ticket = ?",
            (estado, fecha_texto, idTicket),
        )
