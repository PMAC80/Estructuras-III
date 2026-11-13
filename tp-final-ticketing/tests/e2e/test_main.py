from src.db.repositorios.repositorio_tipo_producto import (
    RepositorioTipoProducto,
)
from tests.e2e.ayudas_gui import ConsolaFake


def test_crearAplicacionConBaseTemporalCargaDatosYArranca(tmp_path):
    from main import crearAplicacion

    consola = ConsolaFake(["3"])
    aplicacion = crearAplicacion(
        rutaBd=tmp_path / "ticketing.db",
        consola=consola,
    )

    tipos = RepositorioTipoProducto(aplicacion.conexion).listar()
    assert tipos

    aplicacion.iniciar()
    aplicacion.cerrar()

    assert "Hasta luego." in consola.texto


def test_crearAplicacionPermiteDesactivarDatosIniciales(tmp_path):
    from main import crearAplicacion

    aplicacion = crearAplicacion(
        rutaBd=tmp_path / "ticketing.db",
        consola=ConsolaFake(["3"]),
        cargarIniciales=False,
    )

    assert RepositorioTipoProducto(aplicacion.conexion).listar() == []
    aplicacion.cerrar()
