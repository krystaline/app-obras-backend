from db.db_queries import get_vehiculos_db
from fastapi import APIRouter, HTTPException, status
from entities.partesmo.ParteMO import ParteMORecibir
from db.partes_manoobra import get_partes_mo_db
from db.db_queries import crear_parte_mo_bd, get_materiales_db

router = APIRouter(prefix="/api", tags=["mano_obra"])


@router.get("/partesMO/{idOferta}")
def get_partes_mo(idOferta: int):
    # Removed async
    print(idOferta)
    return get_partes_mo_db(idOferta)


@router.post("/partesMO/new", status_code=201)
def new_parte_mo(parte: ParteMORecibir):
    # Removed async
    # Note: crear_parte_mo_bd is not fully typed in original, returns dict or object with .message?
    # Original code: if crear_parte_mo_bd(parte).message == "OK":
    # But looking at db_queries.py: return {"message": "OK"} (dict)
    # The original main.py had: `if crear_parte_mo_bd(parte).message == "OK":` which suggests it expected an object or named tuple,
    # OR the db_queries.py I saw earlier was slightly different/misinterpreted.
    # Looking at db_queries.py content provided:
    # return {"message": "OK"}
    # So `crear_parte_mo_bd(...)["message"]` is correct for python dicts.
    # OR maybe it was returning an object in a previous version.
    # START CORRECTION: accessing ["message"] for dict.

    result = crear_parte_mo_bd(parte)
    # Handle if result is dict or object
    msg = (
        result.get("message")
        if isinstance(result, dict)
        else getattr(result, "message", None)
    )

    if msg == "OK":
        print(parte)
        return parte
    else:
        raise HTTPException(status_code=500, detail="Error al crear el parte")


@router.get("/materiales")
def get_materiales():
    # Removed async
    return get_materiales_db()


@router.get("/vehiculos")
def get_vehiculos():
    # Removed async
    return get_vehiculos_db()
