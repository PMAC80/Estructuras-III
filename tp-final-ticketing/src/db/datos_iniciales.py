from src.db.repositorios.repositorio_producto import RepositorioProducto
from src.db.repositorios.repositorio_tipo_producto import (
    RepositorioTipoProducto,
)
from src.models.producto import Producto
from src.models.tipo_producto import TipoProducto

DATOS_INICIALES = (
    {
        "nombre": "Software",
        "descripcion": "Aplicaciones y sistemas informáticos",
        "productos": (
            ("Gestor de Tickets", "1.0"),
            ("Portal del Cliente", "2.0"),
        ),
    },
    {
        "nombre": "Hardware",
        "descripcion": "Equipos y dispositivos físicos",
        "productos": (("Servidor", "1.0"),),
    },
)


def cargarDatosIniciales(conexion, datos=None) -> None:
    definiciones = DATOS_INICIALES if datos is None else datos
    repositorio_tipos = RepositorioTipoProducto(conexion)
    repositorio_productos = RepositorioProducto(conexion)

    tipos_existentes = {
        tipo.nombre: tipo for tipo in repositorio_tipos.listar()
    }

    for definicion in definiciones:
        nombre_tipo = definicion["nombre"]
        tipo = tipos_existentes.get(nombre_tipo)

        if tipo is None:
            id_tipo = repositorio_tipos.insertar(
                TipoProducto(
                    None,
                    nombre_tipo,
                    definicion.get("descripcion"),
                )
            )
        else:
            id_tipo = tipo.idTipoProducto

        productos_existentes = {
            (producto.nombre, producto.version)
            for producto in repositorio_productos.listarPorTipo(id_tipo)
        }

        for nombre_producto, version in definicion.get("productos", ()):
            if (nombre_producto, version) not in productos_existentes:
                repositorio_productos.insertar(
                    Producto(None, nombre_producto, version, id_tipo)
                )
