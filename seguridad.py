"""
seguridad.py - Autenticación con JWT (JSON Web Token).

Flujo:
 1. El usuario envía usuario y contraseña a POST /api/v1/token.
 2. Si son correctos, la API devuelve un token firmado con fecha de expiración.
 3. El cliente envía el token en cada solicitud:  Authorization: Bearer <token>
 4. La API verifica firma y vigencia; si fallan, responde 401 Unauthorized.
"""

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from datos import buscar_usuario

# La clave secreta firma los tokens. En producción se lee de una variable de
# entorno o de un gestor de secretos (Azure Key Vault, AWS Secrets Manager),
# NUNCA se escribe en el código ni se sube a GitHub.
CLAVE_SECRETA = os.getenv("JWT_SECRET", "clave-solo-para-desarrollo-cambiar-en-produccion")
ALGORITMO = "HS256"
MINUTOS_EXPIRACION = int(os.getenv("JWT_MINUTOS", "30"))

# Indica a FastAPI/Swagger dónde se obtiene el token (habilita el botón Authorize)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


# --------------------------- Contraseñas ----------------------------------
def generar_hash(password: str, sal: bytes, iteraciones: int = 100_000) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, iteraciones)
    return (f"pbkdf2_sha256${iteraciones}$"
            f"{base64.b64encode(sal).decode()}${base64.b64encode(dk).decode()}")


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        _, iteraciones, sal_b64, _ = password_hash.split("$")
        calculado = generar_hash(password, base64.b64decode(sal_b64), int(iteraciones))
    except ValueError:
        return False
    return hmac.compare_digest(calculado, password_hash)


def autenticar_usuario(usuario: str, password: str):
    datos_usuario = buscar_usuario(usuario)
    if not datos_usuario or not verificar_password(password, datos_usuario["password_hash"]):
        return None
    return datos_usuario


# ------------------------------ Tokens ------------------------------------
def crear_token(usuario: str) -> str:
    ahora = datetime.now(timezone.utc)
    contenido = {
        "sub": usuario,                                      # a quién pertenece
        "iat": ahora,                                        # cuándo se emitió
        "exp": ahora + timedelta(minutes=MINUTOS_EXPIRACION),  # cuándo vence
    }
    return jwt.encode(contenido, CLAVE_SECRETA, algorithm=ALGORITMO)


def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    """Dependencia que protege un endpoint: valida el token recibido."""
    error_401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        contenido = jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])
    except jwt.PyJWTError:          # firma alterada, token vencido o mal formado
        raise error_401
    datos_usuario = buscar_usuario(contenido.get("sub", ""))
    if datos_usuario is None:
        raise error_401
    return datos_usuario
