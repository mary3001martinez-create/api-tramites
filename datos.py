"""
datos.py - Simulación del SISTEMA HEREDADO.

En una organización real, estas funciones consultarían la base de datos
del sistema heredado (por ejemplo, una base Oracle o SQL Server, o un
servicio SOAP). Aquí se usan diccionarios en memoria para que el taller
funcione sin instalar ninguna base de datos.

>>> ADAPTE este archivo al servicio de SU organización (inventario,
>>> calificaciones, solicitudes, etc.): cambie los campos y los datos.
"""

from datetime import date

# ---------------------------------------------------------------------------
# Usuarios autorizados a usar la API.
# La contraseña NUNCA se guarda en texto plano: se guarda su "hash".
# Usuarios de prueba:  ana / ana123   y   luis / luis123
# ---------------------------------------------------------------------------
USUARIOS = {
    "ana": {
        "usuario": "ana",
        "nombre": "Ana Torres",
        # hash PBKDF2-SHA256 de "ana123" (ver seguridad.py)
        "password_hash": "pbkdf2_sha256$100000$c2FsLWFuYQ==$qltsgcn6xIJpa7crMiL0BkrEHV92+WI3fDO2/hcGngM=",
    },
    "luis": {
        "usuario": "luis",
        "nombre": "Luis Mora",
        # hash PBKDF2-SHA256 de "luis123"
        "password_hash": "pbkdf2_sha256$100000$c2FsLWx1aXM=$Q604fA7gfLg4Z0zSp4yWtYOSQqVy4H5KbpYwc9fj+qQ=",
    },
}

# ---------------------------------------------------------------------------
# Trámites registrados en el "sistema heredado".
# ---------------------------------------------------------------------------
TRAMITES = {
    1: {"id": 1, "tipo": "Certificado de matrícula", "estado": "Aprobado",
        "fecha": date(2026, 10, 2), "propietario": "ana"},
    2: {"id": 2, "tipo": "Homologación de asignaturas", "estado": "En revisión",
        "fecha": date(2026, 10, 15), "propietario": "ana"},
    3: {"id": 3, "tipo": "Certificado de notas", "estado": "Recibido",
        "fecha": date(2026, 10, 20), "propietario": "luis"},
}


def buscar_usuario(usuario: str):
    return USUARIOS.get(usuario)


def listar_tramites(propietario: str):
    return [t for t in TRAMITES.values() if t["propietario"] == propietario]


def buscar_tramite(tramite_id: int):
    return TRAMITES.get(tramite_id)


def registrar_tramite(tipo: str, propietario: str):
    nuevo_id = max(TRAMITES) + 1 if TRAMITES else 1
    tramite = {"id": nuevo_id, "tipo": tipo, "estado": "Recibido",
               "fecha": date.today(), "propietario": propietario}
    TRAMITES[nuevo_id] = tramite
    return tramite
