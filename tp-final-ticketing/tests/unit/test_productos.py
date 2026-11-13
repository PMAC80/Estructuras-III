import pytest

from src.excepciones import ErrorValidacion
from src.models.producto import Producto
from src.models.tipo_producto import TipoProducto


def test_tipoProducto_creaYListaProductos():
    tipo = TipoProducto(1, "Software", "Aplicaciones")
    productos = [
        Producto(10, "Gestor", "1.0", idTipoProducto=1),
        Producto(11, "Editor", "2.0", idTipoProducto=2),
        Producto(12, "Visor", "1.5", idTipoProducto=1),
    ]

    assert tipo.nombre == "Software"
    assert tipo.descripcion == "Aplicaciones"
    assert tipo.listarProductos(productos) == [productos[0], productos[2]]


def test_tipoProducto_rechazaNombreVacio():
    with pytest.raises(ErrorValidacion):
        TipoProducto(1, "   ")


def test_producto_creaYDescribe():
    producto = Producto(10, "Gestor", "1.0", idTipoProducto=1)

    assert producto.getDescripcion() == "Gestor 1.0"
    assert producto.perteneceA(TipoProducto(1, "Software")) is True
    assert producto.perteneceA(TipoProducto(2, "Hardware")) is False


def test_producto_rechazaNombreOVersionVacios():
    with pytest.raises(ErrorValidacion):
        Producto(10, "", "1.0", idTipoProducto=1)

    with pytest.raises(ErrorValidacion):
        Producto(10, "Gestor", " ", idTipoProducto=1)


def test_producto_rechazaTipoInvalido():
    with pytest.raises(ErrorValidacion):
        Producto(10, "Gestor", "1.0", idTipoProducto=None)
