from src.db.mapeo import datosCliente, filaACliente
from src.excepciones import ErrorValidacion


class RepositorioCliente:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar(self, cliente) -> int:
        datos = datosCliente(cliente)
        if datos["id_usuario"] is None:
            raise ErrorValidacion("El cliente debe tener un usuario asociado.")

        self.conexion.execute(
            "INSERT INTO cliente (id_usuario, empresa, telefono) "
            "VALUES (?, ?, ?)",
            (datos["id_usuario"], datos["empresa"], datos["telefono"]),
        )
        return datos["id_usuario"]

    def buscarPorId(self, idUsuario):
        fila = self.conexion.execute(
            "SELECT u.*, c.empresa, c.telefono "
            "FROM cliente c "
            "JOIN usuario u ON u.id_usuario = c.id_usuario "
            "WHERE c.id_usuario = ?",
            (idUsuario,),
        ).fetchone()
        return filaACliente(fila) if fila else None

    def listar(self):
        filas = self.conexion.execute(
            "SELECT u.*, c.empresa, c.telefono "
            "FROM cliente c "
            "JOIN usuario u ON u.id_usuario = c.id_usuario "
            "ORDER BY u.nombre"
        ).fetchall()
        return [filaACliente(fila) for fila in filas]
