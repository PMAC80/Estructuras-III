from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RegistroHistorial:
    idEvento: int | None
    idTicket: int
    idActor: int | None
    tipoEvento: str
    estadoAnterior: str | None
    estadoNuevo: str | None
    detalle: str | None
    fecha: datetime


@dataclass(frozen=True)
class RegistroAlerta:
    idAlerta: int | None
    idUsuario: int
    idTicket: int | None
    tipo: str
    prioridad: str
    mensaje: str
    estado: str
    fechaCreacion: datetime
