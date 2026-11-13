import pytest

from src.db.repositorios.repositorio_producto import RepositorioProducto
from src.db.repositorios.repositorio_tipo_producto import (
    RepositorioTipoProducto,
)
from src.excepciones import ErrorConflicto
from src.models.producto import Producto
from src.models.tipo_producto import TipoProducto


def test_insertarBuscarYListarTipoProducto(db_temporal):
    repositorio = RepositorioTipoProducto(db_temporal)

    id_tipo = repositorio.insertar(
        TipoProducto(None, "Software", "Aplicaciones")
    )

    assert id_tipo == 1
    recuperado = repositorio.buscarPorId(id_tipo)
    assert recuperado.nombre == "Software"
    assert recuperado.descripcion == "Aplicaciones"
    assert [tipo.nombre for tipo in repositorio.listar()] == ["Software"]


def test_rechazaNombreDuplicadoDeTipoProducto(db_temporal):
    repositorio = RepositorioTipoProducto(db_temporal)
    repositorio.insertar(TipoProducto(None, "Software"))

    with pytest.raises(ErrorConflicto):
        repositorio.insertar(TipoProducto(None, "Software"))


def test_insertarBuscarYListarProductosPorTipo(db_temporal):
    repositorio_tipos = RepositorioTipoProducto(db_temporal)
    id_software = repositorio_tipos.insertar(TipoProducto(None, "Software"))
    id_hardware = repositorio_tipos.insertar(TipoProducto(None, "Hardware"))

    repositorio = RepositorioProducto(db_temporal)
    id_gestor = repositorio.insertar(
        Producto(None, "Gestor", "1.0", id_software)
    )
    id_editor = repositorio.insertar(
        Producto(None, "Editor", "2.0", id_software)
    )
    repositorio.insertar(Producto(None, "Servidor", "1.0", id_hardware))

    recuperado = repositorio.buscarPorId(id_gestor)
    assert recuperado.nombre == "Gestor"
    assert recuperado.version == "1.0"
    assert recuperado.idTipoProducto == id_software

    productos_software = repositorio.listarPorTipo(id_software)
    assert [producto.idProducto for producto in productos_software] == [
        id_gestor,
        id_editor,
    ]


def test_rechazaProductoDuplicado(db_temporal):
    repositorio_tipos = RepositorioTipoProducto(db_temporal)
    id_software = repositorio_tipos.insertar(TipoProducto(None, "Software"))

    repositorio = RepositorioProducto(db_temporal)
    repositorio.insertar(Producto(None, "Gestor", "1.0", id_software))

    with pytest.raises(ErrorConflicto):
        repositorio.insertar(Producto(None, "Gestor", "1.0", id_software))
