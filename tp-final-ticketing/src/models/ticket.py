from datetime import datetime

from src.excepciones import ErrorEstado, ErrorValidacion
from src.models.estados import (
    ESTADO_CERRADO,
    ESTADO_NUEVO,
    ESTADO_REABIERTO,
    ESTADOS,
    PRIORIDADES,
    TRANSICIONES,
)
from src.models.validaciones import (
    validarEnteroPositivo,
    validarEnteroPositivoOpcional,
    validarTextoObligatorio,
)


class Ticket:
    def __init__(
        self,
        titulo,
        descripcion,
        prioridad,
        idCliente,
        idProducto,
        idTipoProducto,
        idTicket=None,
        idRepresentante=None,
        estado=ESTADO_NUEVO,
        fechaCreacion=None,
        fechaCierre=None,
    ):
        self.idTicket = validarEnteroPositivoOpcional(idTicket, "idTicket")
        self.titulo = validarTextoObligatorio(titulo, "titulo")
        self.descripcion = validarTextoObligatorio(descripcion, "descripcion")

        if prioridad not in PRIORIDADES:
            raise ErrorValidacion("La prioridad debe ser BAJA, MEDIA o ALTA.")
        self.prioridad = prioridad

        self.idCliente = validarEnteroPositivo(idCliente, "idCliente")
        self.idRepresentante = validarEnteroPositivoOpcional(
            idRepresentante,
            "idRepresentante",
        )
        self.idProducto = validarEnteroPositivo(idProducto, "idProducto")
        self.idTipoProducto = validarEnteroPositivo(idTipoProducto, "idTipoProducto")

        if estado not in ESTADOS:
            raise ErrorValidacion("El estado del ticket no es válido.")
        self.estado = estado

        self.fechaCreacion = (
            self._validarFecha(fechaCreacion, "fechaCreacion") or datetime.now()
        )
        self.fechaCierre = self._validarFecha(fechaCierre, "fechaCierre")

    def puedeTransicionar(self, evento) -> bool:
        return (self.estado, evento) in TRANSICIONES

    def cambiarEstado(self, evento, fecha=None):
        destino = TRANSICIONES.get((self.estado, evento))
        if destino is None:
            raise ErrorEstado(
                f"No se puede aplicar el evento '{evento}' al estado '{self.estado}'."
            )

        fechaCierre = self.fechaCierre
        if destino == ESTADO_CERRADO:
            fechaCierre = self._validarFecha(fecha, "fechaCierre") or datetime.now()
        elif destino == ESTADO_REABIERTO:
            fechaCierre = None

        self.estado = destino
        self.fechaCierre = fechaCierre
        return self.estado

    @staticmethod
    def _validarFecha(valor, campo):
        if valor is None:
            return None
        if not isinstance(valor, datetime):
            raise ErrorValidacion(f"El campo '{campo}' debe ser una fecha válida.")
        return valor
