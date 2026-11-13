from datetime import datetime

from src.db.mapeo import filaAAlerta


class RepositorioAlerta:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar(
        self,
        idUsuario,
        idTicket,
        tipo,
        prioridad,
        mensaje,
        estado="PENDIENTE",
        fechaCreacion=None,
    ) -> int:
        fecha = fechaCreacion or datetime.now()
        cursor = self.conexion.execute(
            "INSERT INTO alerta "
            "(id_usuario, id_ticket, tipo, prioridad, mensaje, estado, "
            "fecha_creacion) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                idUsuario,
                idTicket,
                tipo,
                prioridad,
                mensaje,
                estado,
                fecha.isoformat(),
            ),
        )
        return cursor.lastrowid

    def buscarPorId(self, idAlerta):
        fila = self.conexion.execute(
            "SELECT * FROM alerta WHERE id_alerta = ?",
            (idAlerta,),
        ).fetchone()
        return filaAAlerta(fila) if fila else None

    def listarPorUsuario(self, idUsuario, soloPendientes=False):
        sql = "SELECT * FROM alerta WHERE id_usuario = ?"
        if soloPendientes:
            sql += " AND estado = 'PENDIENTE'"
        sql += " ORDER BY fecha_creacion DESC, id_alerta DESC"
        filas = self.conexion.execute(sql, (idUsuario,)).fetchall()
        return [filaAAlerta(fila) for fila in filas]

    def listarPendientes(self, idUsuario):
        return self.listarPorUsuario(idUsuario, soloPendientes=True)

    def marcarLeida(self, idAlerta) -> None:
        self.conexion.execute(
            "UPDATE alerta SET estado = 'LEIDA' WHERE id_alerta = ?",
            (idAlerta,),
        )
