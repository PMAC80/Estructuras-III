from src.models.validaciones import (
    validarEnteroPositivoOpcional,
    validarTextoObligatorio,
    validarTextoOpcional,
)


class TipoProducto:
    def __init__(self, idTipoProducto, nombre, descripcion=None):
        self.idTipoProducto = validarEnteroPositivoOpcional(
            idTipoProducto,
            "idTipoProducto",
        )
        self.nombre = validarTextoObligatorio(nombre, "nombre")
        self.descripcion = validarTextoOpcional(descripcion, "descripcion")

    def listarProductos(self, productos):
        return [
            producto
            for producto in productos
            if producto.idTipoProducto == self.idTipoProducto
        ]
