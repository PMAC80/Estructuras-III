import re

from src.excepciones import ErrorValidacion
from src.models.estados import ROL_REPRESENTANTE
from src.models.usuario import Usuario
from src.models.validaciones import validarTextoOpcional


def _validarLegajo(legajo):
    if legajo is None:
        return None
    if not isinstance(legajo, str):
        raise ErrorValidacion("El campo 'legajo' debe ser texto.")
    texto = legajo.strip()
    if not re.fullmatch(r"[A-Za-z0-9-]{3,20}", texto):
        raise ErrorValidacion(
            "El legajo debe tener entre 3 y 20 caracteres alfanuméricos o guiones."
        )
    return texto


class Representante(Usuario):
    def __init__(
        self,
        idUsuario,
        nombre,
        email,
        contrasenaHash,
        legajo=None,
        especialidad=None,
        activo=True,
    ):
        super().__init__(
            idUsuario,
            nombre,
            email,
            contrasenaHash,
            ROL_REPRESENTANTE,
            activo,
        )
        self.legajo = _validarLegajo(legajo)
        self.especialidad = validarTextoOpcional(especialidad, "especialidad")
