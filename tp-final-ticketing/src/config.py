import os
from pathlib import Path
from typing import Mapping

RUTA_POR_DEFECTO = "ticketing.db"
VARIABLE_ENTORNO = "TICKETING_DB_PATH"


def resolverRutaBaseDatos(entorno: Mapping[str, str] | None = None) -> Path:
    valores = os.environ if entorno is None else entorno
    ruta = valores.get(VARIABLE_ENTORNO) or RUTA_POR_DEFECTO
    return Path(ruta)
