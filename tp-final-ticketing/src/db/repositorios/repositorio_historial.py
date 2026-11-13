from datetime import datetime

from src.db.mapeo import filaAHistorial


class RepositorioHistorial:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar(
        self,
        idTicket,
        idActor,
        tipoEvento,
        estadoAnterior=None,
        estadoNuevo=None,
        detalle=None,
        fecha=None,
    ) -> int:
        fechaEvento = fecha or datetime.now()
        cursor = self.conexion.execute(
            "INSERT INTO historial "
            "(id_ticket, id_actor, tipo_evento, estado_anterior, "
            "estado_nuevo, detalle, fecha) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                idTicket,
                idActor,
                tipoEvento,
                estadoAnterior,
                estadoNuevo,
                detalle,
                fechaEvento.isoformat(),
            ),
        )
        return cursor.lastrowid

    def listarPorTicket(self, idTicket):
        filas = self.conexion.execute(
            "SELECT * FROM historial WHERE id_ticket = ? "
            "ORDER BY fecha, id_evento",
            (idTicket,),
        ).fetchall()
        return [filaAHistorial(fila) for fila in filas]
