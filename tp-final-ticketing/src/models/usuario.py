from src.excepciones import ErrorValidacion
from src.models.estados import ROL_CLIENTE, ROL_REPRESENTANTE, ROLES
from src.models.seguridad import ALGORITMO, generarHash
from src.models.validaciones import (
    validarBooleano,
    validarEmail,
    validarEnteroPositivoOpcional,
    validarTextoObligatorio,
)


def _validarHash(contrasenaHash) -> str:
    mensaje = "La contraseña debe estar almacenada de forma segura."
    if not isinstance(contrasenaHash, str):
        raise ErrorValidacion(mensaje)

    partes = contrasenaHash.split("$")
    if len(partes) != 4 or partes[0] != ALGORITMO:
        raise ErrorValidacion(mensaje)

    try:
        int(partes[1])
        bytes.fromhex(partes[2])
        bytes.fromhex(partes[3])
    except ValueError:
        raise ErrorValidacion(mensaje) from None

    return contrasenaHash


class Usuario:
    def __init__(self, idUsuario, nombre, email, contrasenaHash, rol, activo=True):
        self.idUsuario = validarEnteroPositivoOpcional(idUsuario, "idUsuario")
        self.nombre = validarTextoObligatorio(nombre, "nombre")
        self.email = validarEmail(email)
        self.contrasenaHash = _validarHash(contrasenaHash)

        if rol not in ROLES:
            raise ErrorValidacion("El rol debe ser CLIENTE o REPRESENTANTE.")
        self.rol = rol
        self.activo = validarBooleano(activo, "activo")

    @classmethod
    def crear(cls, idUsuario, nombre, email, contrasena, rol, activo=True):
        if not isinstance(contrasena, str) or not contrasena:
            raise ErrorValidacion("La contraseña es obligatoria.")
        return cls(
            idUsuario,
            nombre,
            email,
            generarHash(contrasena),
            rol,
            activo,
        )

    def esCliente(self) -> bool:
        return self.rol == ROL_CLIENTE

    def esRepresentante(self) -> bool:
        return self.rol == ROL_REPRESENTANTE
