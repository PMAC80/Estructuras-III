from src.models.validaciones import (
    validarEnteroPositivo,
    validarEnteroPositivoOpcional,
    validarTextoObligatorio,
)


class Producto:
    def __init__(self, idProducto, nombre, version, idTipoProducto):
        self.idProducto = validarEnteroPositivoOpcional(idProducto, "idProducto")
        self.nombre = validarTextoObligatorio(nombre, "nombre")
        self.version = validarTextoObligatorio(version, "version")
        self.idTipoProducto = validarEnteroPositivo(idTipoProducto, "idTipoProducto")

    def getDescripcion(self) -> str:
        return f"{self.nombre} {self.version}"

    def perteneceA(self, tipoProducto) -> bool:
        return self.idTipoProducto == tipoProducto.idTipoProducto
