from dataclasses import dataclass


@dataclass(frozen=True)
class Sesion:
    idUsuario: int
    rol: str
    nombre: str
