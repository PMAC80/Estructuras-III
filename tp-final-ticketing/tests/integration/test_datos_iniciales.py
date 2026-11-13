from src.db.conexion import abrirConexion, transaccion
from src.db.datos_iniciales import cargarDatosIniciales
from src.db.esquema import crearEsquema
from src.db.repositorios.repositorio_producto import RepositorioProducto
from src.db.repositorios.repositorio_tipo_producto import (
    RepositorioTipoProducto,
)


def _resumen(conexion):
    repositorio_tipos = RepositorioTipoProducto(conexion)
    repositorio_productos = RepositorioProducto(conexion)
    tipos = repositorio_tipos.listar()
    productos_por_tipo = {
        tipo.idTipoProducto: {
            (producto.nombre, producto.version)
            for producto in repositorio_productos.listarPorTipo(
                tipo.idTipoProducto
            )
        }
        for tipo in tipos
    }
    return {tipo.nombre: productos_por_tipo[tipo.idTipoProducto] for tipo in tipos}


def test_cargaInicialCreaTiposYProductosAsociados(db_temporal):
    cargarDatosIniciales(db_temporal)

    resumen = _resumen(db_temporal)
    assert resumen["Software"] == {
        ("Gestor de Tickets", "1.0"),
        ("Portal del Cliente", "2.0"),
    }
    assert resumen["Hardware"] == {("Servidor", "1.0")}


def test_cargaInicialEsIdempotenteYPersiste(tmp_path):
    ruta = tmp_path / "ticketing.db"
    conexion = abrirConexion(ruta)
    crearEsquema(conexion)
    with transaccion(conexion):
        cargarDatosIniciales(conexion)
    conexion.close()

    conexion = abrirConexion(ruta)
    try:
        resumen_inicial = _resumen(conexion)
        with transaccion(conexion):
            cargarDatosIniciales(conexion)
        assert _resumen(conexion) == resumen_inicial
    finally:
        conexion.close()


def test_cargaInicialAceptaDatosPersonalizados(db_temporal):
    datos = (
        {
            "nombre": "Redes",
            "descripcion": "Conectividad",
            "productos": (("Router", "1.0"),),
        },
    )

    cargarDatosIniciales(db_temporal, datos)
    cargarDatosIniciales(db_temporal, datos)

    assert _resumen(db_temporal) == {"Redes": {("Router", "1.0")}}
