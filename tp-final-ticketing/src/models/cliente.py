from src.models.estados import ROL_CLIENTE
from src.models.usuario import Usuario
from src.models.validaciones import validarTextoOpcional


class Cliente(Usuario):
    def __init__(
        self,
        idUsuario,
        nombre,
        email,
        contrasenaHash,
        empresa=None,
        telefono=None,
        activo=True,
    ):
        super().__init__(
            idUsuario,
            nombre,
            email,
            contrasenaHash,
            ROL_CLIENTE,
            activo,
        )
        self.empresa = validarTextoOpcional(empresa, "empresa")
        self.telefono = validarTextoOpcional(telefono, "telefono")
