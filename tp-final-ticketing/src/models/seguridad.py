import hashlib
import hmac
import secrets

ALGORITMO = "pbkdf2_sha256"
ITERACIONES = 200_000
LONGITUD_SALT = 16
LONGITUD_HASH = 32


def generarHash(contrasena: str) -> str:
    salt = secrets.token_bytes(LONGITUD_SALT)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        salt,
        ITERACIONES,
        dklen=LONGITUD_HASH,
    )
    return f"{ALGORITMO}${ITERACIONES}${salt.hex()}${hash_bytes.hex()}"


def verificarContrasena(contrasena: str, hashAlmacenado: str) -> bool:
    try:
        algoritmo, iteraciones_texto, salt_texto, hash_texto = hashAlmacenado.split("$")
        if algoritmo != ALGORITMO:
            return False
        iteraciones = int(iteraciones_texto)
        salt = bytes.fromhex(salt_texto)
        hash_esperado = bytes.fromhex(hash_texto)
    except (AttributeError, ValueError):
        return False

    hash_calculado = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        salt,
        iteraciones,
        dklen=len(hash_esperado),
    )
    return hmac.compare_digest(hash_calculado, hash_esperado)
