import uuid
from fastapi import Header, HTTPException
from dotenv import load_dotenv
from db.db_queries import get_allowed_users
import time

load_dotenv()

_usuarios_cacheados = []
_ultima_carga = 0
MINUTOS_REFRESCO = 20

ALLOWED_USERS = get_allowed_users()


def obtener_usuarios_cacheados():
    global _usuarios_cacheados, _ultima_carga
    ahora = time.time()
    if ahora - _ultima_carga > (MINUTOS_REFRESCO * 60) or not _usuarios_cacheados:
        _usuarios_cache = get_allowed_users()
        _ultima_carga = ahora

        return _usuarios_cache


async def verify_auth_headers(
    user: str = Header(..., description="User ID"),
    authorization: str = Header(..., description="Bearer Token"),
):
    print(user)
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user:
        raise HTTPException(status_code=400, detail="User header is missing or empty")

    try:
        uuid.UUID(user)
        if user not in obtener_usuarios_cacheados():
            raise HTTPException(
                status_code=403,
                detail="User not authorized",
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="User header must be a valid Azure User ID (UUID format)",
        )

    # Aquí se podrían añadir más validaciones (ej: verificar token real)
    return {"user": user, "token": authorization.replace("Bearer ", "")}
