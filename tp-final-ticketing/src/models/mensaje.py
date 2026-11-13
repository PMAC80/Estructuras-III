from datetime import datetime

from src.excepciones import ErrorValidacion
from src.models.validaciones import (
    validarBooleano,
    validarEnteroPositivo,
    validarEnteroPositivoOpcional,
    validarTextoObligatorio,
)


class Mensaje:
    def __init__(
        self,
        idTicket,
        idAutor,
        contenido,
        idMensaje=None,
        fechaEnvio=None,
        leido=False,
    ):
        self.idMensaje = validarEnteroPositivoOpcional(idMensaje, "idMensaje")
        self.idTicket = validarEnteroPositivo(idTicket, "idTicket")
        self.idAutor = validarEnteroPositivo(idAutor, "idAutor")
        self.contenido = validarTextoObligatorio(contenido, "contenido")
        self.fechaEnvio = (
            self._validarFecha(fechaEnvio, "fechaEnvio") or datetime.now()
        )
        self.leido = validarBooleano(leido, "leido")

    def marcarLeido(self):
        self.leido = True

    @staticmethod
    def _validarFecha(valor, campo):
        if valor is None:
            return None
        if not isinstance(valor, datetime):
            raise ErrorValidacion(f"El campo '{campo}' debe ser una fecha válida.")
        return valor
