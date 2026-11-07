"""
main.py - API REST de Trámites (código base del Taller 3).

Ejecutar:                                     uvicorn main:app --reload
Documentación interactiva (Swagger UI):       http://localhost:8000/docs
Contrato OpenAPI:                             http://localhost:8000/openapi.json
"""

from datetime import date

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

import datos
from seguridad import autenticar_usuario, crear_token, obtener_usuario_actual

app = FastAPI(
    title="API de Trámites",
    version="1.0.0",
    description="API que expone de forma segura el servicio de trámites "
                "de un sistema heredado. Taller 3 - Gestión de Servicios en la Nube.",
)


# ------------------------- Modelos (esquemas) -----------------------------
# Definen qué datos entran y salen. FastAPI los usa para validar y para
# generar el contrato OpenAPI automáticamente.
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TramiteNuevo(BaseModel):
    tipo: str = Field(..., min_length=3, max_length=100,
                      examples=["Certificado de matrícula"])


class Tramite(BaseModel):
    id: int
    tipo: str
    estado: str
    fecha: date
    # Nota: el campo "propietario" NO se expone; es un dato interno.


# ------------------------------ Endpoints ---------------------------------
@app.get("/", tags=["Estado"])
def estado_servicio():
    """Verifica que la API está en línea (health check)."""
    return {"servicio": "API de Trámites", "estado": "en línea"}


@app.post("/api/v1/token", response_model=Token, tags=["Autenticación"])
def obtener_token(formulario: OAuth2PasswordRequestForm = Depends()):
    """Recibe usuario y contraseña y devuelve un token JWT."""
    usuario = autenticar_usuario(formulario.username, formulario.password)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=crear_token(usuario["usuario"]))


@app.get("/api/v1/tramites", response_model=list[Tramite], tags=["Trámites"])
def listar_tramites(usuario=Depends(obtener_usuario_actual)):
    """Lista los trámites del usuario autenticado."""
    return datos.listar_tramites(usuario["usuario"])


@app.get("/api/v1/tramites/{tramite_id}", response_model=Tramite, tags=["Trámites"],
         responses={404: {"description": "Trámite no encontrado"}})
def consultar_tramite(tramite_id: int, usuario=Depends(obtener_usuario_actual)):
    """Consulta el estado de un trámite del usuario autenticado."""
    tramite = datos.buscar_tramite(tramite_id)
    # Si el trámite no existe o pertenece a otra persona se responde 404,
    # para no revelar información de otros usuarios.
    if tramite is None or tramite["propietario"] != usuario["usuario"]:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")
    return tramite


@app.post("/api/v1/tramites", response_model=Tramite,
          status_code=status.HTTP_201_CREATED, tags=["Trámites"])
def registrar_tramite(nuevo: TramiteNuevo, usuario=Depends(obtener_usuario_actual)):
    """Registra un nuevo trámite a nombre del usuario autenticado."""
    return datos.registrar_tramite(nuevo.tipo, usuario["usuario"])
