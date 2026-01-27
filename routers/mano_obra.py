from fastapi import APIRouter, HTTPException, status, Header
from entities.partesmo.ParteMO import ParteMORecibir
from db.partes_manoobra import get_partes_mo_db
from db.db_queries import crear_parte_mo_bd, get_materiales_db, get_vehiculos_db
from exceptions import DatabaseError

router = APIRouter(prefix="/api", tags=["mano_obra"])


@router.get("/partesMO/{idOferta}", status_code=status.HTTP_200_OK)
def get_partes_mo(
    idOferta: int, user: str = Header(...), authorization: str = Header(...)
):
    # Removed async
    print(idOferta)
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        accessToken = authorization.replace("Bearer ", "")
    try:
        return get_partes_mo_db(idOferta, accessToken, user)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting partes MO: {e}")


@router.post("/partesMO/new", status_code=status.HTTP_201_CREATED)
def new_parte_mo(parte: ParteMORecibir):
    try:
        result = crear_parte_mo_bd(parte)
        print(f"Propagando ID: {result.get('idParteAPP')}")
        return result
    except DatabaseError as e:
        print(f"Error creating parte: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error creating parte")


@router.get("/materiales", status_code=status.HTTP_200_OK)
def get_materiales():
    # Removed async
    try:
        return get_materiales_db()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting materiales: {e}")


@router.get("/vehiculos", status_code=status.HTTP_200_OK)
def get_vehiculos():
    # Removed async
    try:
        return get_vehiculos_db()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting vehiculos: {e}")
