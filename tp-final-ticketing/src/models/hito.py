from datetime import datetime

from src.excepciones import ErrorValidacion
from src.models.estados import (
    ESTADO_HITO_CUMPLIDO,
    ESTADO_HITO_PENDIENTE,
    ESTADO_HITO_VENCIDO,
    ESTADOS_HITO,
)
from src.models.validaciones import (
    validarEnteroPositivo,
    validarEnteroPositivoOpcional,
    validarTextoObligatorio,
)


class Hito:
    def __init__(
        self,
        idTicket,
        descripcion,
        fechaCompromiso,
        idHito=None,
        orden=1,
        estado=ESTADO_HITO_PENDIENTE,
        fechaCumplimiento=None,
    ):
        self.idHito = validarEnteroPositivoOpcional(idHito, "idHito")
        self.idTicket = validarEnteroPositivo(idTicket, "idTicket")
        self.descripcion = validarTextoObligatorio(descripcion, "descripcion")

        self.fechaCompromiso = self._validarFecha(
            fechaCompromiso,
            "fechaCompromiso",
        )
        if self.fechaCompromiso is None:
            raise ErrorValidacion("El campo 'fechaCompromiso' es obligatorio.")

        self.orden = validarEnteroPositivo(orden, "orden")

        if estado not in ESTADOS_HITO:
            raise ErrorValidacion("El estado del hito no es válido.")
        self.estado = estado

        self.fechaCumplimiento = self._validarFecha(
            fechaCumplimiento,
            "fechaCumplimiento",
        )

    def completar(self, fecha=None):
        self.fechaCumplimiento = (
            self._validarFecha(fecha, "fechaCumplimiento") or datetime.now()
        )
        self.estado = ESTADO_HITO_CUMPLIDO

    def actualizarEstado(self, estado):
        if estado not in ESTADOS_HITO:
            raise ErrorValidacion("El estado del hito no es válido.")
        self.estado = estado

    def estaVencido(self, hoy=None) -> bool:
        if self.estado == ESTADO_HITO_CUMPLIDO:
            return False
        if self.estado == ESTADO_HITO_VENCIDO:
            return True

        referencia = hoy or datetime.now()
        if not isinstance(referencia, datetime):
            raise ErrorValidacion("La fecha de referencia no es válida.")
        return self.fechaCompromiso < referencia

    @staticmethod
    def _validarFecha(valor, campo):
        if valor is None:
            return None
        if not isinstance(valor, datetime):
            raise ErrorValidacion(f"El campo '{campo}' debe ser una fecha válida.")
        return valor
