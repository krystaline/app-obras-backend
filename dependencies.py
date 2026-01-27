from fastapi import Header, HTTPException


async def verify_auth_headers(
    user: str = Header(..., description="User ID"),
    authorization: str = Header(..., description="Bearer Token"),
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user:
        raise HTTPException(status_code=400, detail="User header is missing or empty")

    # Aquí se podrían añadir más validaciones (ej: verificar token real)
    return {"user": user, "token": authorization.replace("Bearer ", "")}
