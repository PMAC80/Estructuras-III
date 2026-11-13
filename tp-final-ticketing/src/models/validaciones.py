import re

from src.excepciones import ErrorValidacion


def validarTextoObligatorio(valor, campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ErrorValidacion(f"El campo '{campo}' es obligatorio.")
    return valor.strip()


def validarTextoOpcional(valor, campo: str):
    if valor is None:
        return None
    if not isinstance(valor, str):
        raise ErrorValidacion(f"El campo '{campo}' debe ser texto.")
    texto = valor.strip()
    return texto or None


def validarEmail(email) -> str:
    texto = validarTextoObligatorio(email, "email").lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", texto):
        raise ErrorValidacion("El email ingresado no es válido.")
    return texto


def validarEnteroPositivo(valor, campo: str) -> int:
    if (
        valor is None
        or isinstance(valor, bool)
        or not isinstance(valor, int)
        or valor <= 0
    ):
        raise ErrorValidacion(f"El campo '{campo}' debe ser un entero positivo.")
    return valor


def validarEnteroPositivoOpcional(valor, campo: str):
    if valor is None:
        return None
    return validarEnteroPositivo(valor, campo)


def validarBooleano(valor, campo: str) -> bool:
    if not isinstance(valor, bool):
        raise ErrorValidacion(f"El campo '{campo}' debe ser booleano.")
    return valor
