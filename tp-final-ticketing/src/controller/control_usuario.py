from src.controller.sesion import Sesion
from src.db.conexion import transaccion
from src.excepciones import (
    ErrorAutenticacion,
    ErrorPermiso,
    ErrorValidacion,
)
from src.models.cliente import Cliente
from src.models.estados import ROL_CLIENTE, ROL_REPRESENTANTE
from src.models.representante import Representante
from src.models.seguridad import verificarContrasena
from src.models.usuario import Usuario
from src.models.validaciones import validarEmail, validarTextoObligatorio

LONGITUD_MINIMA_CONTRASENA = 8


def _validarContrasena(contrasena) -> str:
    if not isinstance(contrasena, str) or len(contrasena) < (
        LONGITUD_MINIMA_CONTRASENA
    ):
        raise ErrorValidacion(
            "La contraseña debe tener al menos 8 caracteres."
        )
    if not any(caracter.isalpha() for caracter in contrasena):
        raise ErrorValidacion("La contraseña debe incluir letras y números.")
    if not any(caracter.isdigit() for caracter in contrasena):
        raise ErrorValidacion("La contraseña debe incluir letras y números.")
    return contrasena


class ControlUsuario:
    def __init__(
        self,
        conexion,
        repositorioUsuarios,
        repositorioClientes,
        repositorioRepresentantes,
    ):
        self.conexion = conexion
        self.repositorioUsuarios = repositorioUsuarios
        self.repositorioClientes = repositorioClientes
        self.repositorioRepresentantes = repositorioRepresentantes
        self.sesion = None

    def registrar(
        self,
        nombre,
        email,
        contrasena,
        rol,
        empresa=None,
        telefono=None,
        legajo=None,
        especialidad=None,
    ):
        _validarContrasena(contrasena)
        usuario = Usuario.crear(None, nombre, email, contrasena, rol)

        with transaccion(self.conexion):
            idUsuario = self.repositorioUsuarios.insertar(usuario)
            usuario.idUsuario = idUsuario

            if rol == ROL_CLIENTE:
                self.repositorioClientes.insertar(
                    Cliente(
                        idUsuario,
                        usuario.nombre,
                        usuario.email,
                        usuario.contrasenaHash,
                        empresa,
                        telefono,
                    )
                )
            elif rol == ROL_REPRESENTANTE:
                self.repositorioRepresentantes.insertar(
                    Representante(
                        idUsuario,
                        usuario.nombre,
                        usuario.email,
                        usuario.contrasenaHash,
                        legajo,
                        especialidad,
                    )
                )

        return self.repositorioUsuarios.buscarPorId(idUsuario)

    def login(self, email, contrasena):
        emailValidado = validarEmail(email)
        validarTextoObligatorio(contrasena, "contraseña")

        usuario = self.repositorioUsuarios.buscarPorEmail(emailValidado)
        if usuario is None:
            raise ErrorAutenticacion("Email o contraseña incorrectos.")
        if not usuario.activo:
            raise ErrorAutenticacion("La cuenta no está habilitada.")
        if not verificarContrasena(contrasena, usuario.contrasenaHash):
            raise ErrorAutenticacion("Email o contraseña incorrectos.")

        self.sesion = Sesion(
            usuario.idUsuario,
            usuario.rol,
            usuario.nombre,
        )
        return self.sesion

    def logout(self) -> None:
        self.sesion = None

    def obtenerSesion(self):
        return self.sesion

    def estaAutenticado(self) -> bool:
        return self.sesion is not None

    def requerirSesion(self):
        if self.sesion is None:
            raise ErrorAutenticacion("Debe iniciar sesión.")
        return self.sesion

    def requerirRol(self, *roles):
        sesion = self.requerirSesion()
        if roles and sesion.rol not in roles:
            raise ErrorPermiso(
                "No tiene permiso para realizar esta operación."
            )
        return sesion
