from typing import List, Union
from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from dto.ParteDTO import ParteRecibidoPost, ParteImprimirPDF
from entities.LineaPedido import LineaPedidoPDF
from entities.User import User

from db.db_connection import get_num_parte
from db.db_queries import (
    create_parte,
    create_pdf_file,
    get_lineas_pdf,
    get_parte_pdf,
    asginar_trabajadores_bd,
    get_trabajadores_parte,
    get_lineas_con_oferta,
)
from utils.files import handle_signature

router = APIRouter(prefix="/api/partes", tags=["partes"])

# Also including the /api/pdf endpoint here as it relates to partes
pdf_router = APIRouter(prefix="/api/pdf", tags=["pdf"])


# antes de esto, tendríamos que verificar si el trigger de AHORA se ha ejecutado y el resultado es OK
@router.post("")
def create_partes(parte: ParteRecibidoPost) -> ParteRecibidoPost:
    # Removed async to prevent blocking loop with synchronous DB calls
    print(parte)
    handle_signature(parte)
    try:
        print(parte)
        create_parte(parte)
        return parte
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al crear el parte de obra: {e}"
        )


@router.get("/parte/{parteId}")
def get_parte(parteId: int):
    # Removed async
    parte_data_dict = get_parte_pdf(parteId)
    if not parte_data_dict:
        raise HTTPException(
            status_code=404, detail=f"Parte con ID parteAPP {parteId} no encontrado."
        )

    lineas_data_list = get_lineas_pdf(parteId)
    validated_lineas = []
    for line_dict in lineas_data_list:
        try:
            validated_lineas.append(LineaPedidoPDF(**line_dict))
        except ValidationError as e:
            print(
                f"Error de validación para una línea de pedido (ID Parte: {parteId}): {e} - Datos: {line_dict}"
            )
            continue

    parte_data_dict["lineas"] = validated_lineas

    try:
        parte_obj = ParteImprimirPDF(**parte_data_dict)
    except ValidationError as e:
        print(f"Error de validación al crear ParteImprimirPDF desde DB: {e}")
        print(f"Datos del parte que causaron el error: {parte_data_dict}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: Fallo la validación de datos del parte principal - {e}",
        )
    return parte_obj


@router.get("/lastId")
def get_last_id():
    # Removed async
    val = get_num_parte()
    # Handle None if no partes exist
    if val is None:
        return 1
    print(val + 1)
    return val + 1


@router.get("/all")
def get_all_partes_summary():
    # This was a placeholder in original code
    pass


# todo: cambiar idParte por idParteERP o idParteAPP
@router.post("/{idParte}/workers", status_code=201)
def asignar_trabajadores_parte(idParte: Union[int, str], workers: List[User]):
    # Removed async
    if idParte:
        if asginar_trabajadores_bd(idParte, workers):
            return True
    raise HTTPException(
        status_code=404, detail=f"Parte con ID {idParte} no encontrado."
    )


# todo: cambiar idParte por idParteERP o idParteAPP
@router.get("/{idParte}/workers")
def listar_trabajadores_parte(idParte: int):
    # Removed async
    return get_trabajadores_parte(idParte)


# PDF Endpoint - merged in file but could be separate router if desired.
# The original path was /api/pdf/{idParte}, so we register it differently or import it in main.
# I'll define the function here and main can include this router too or we effectively put it in this file.


@pdf_router.get("/{idParte}")
def create_pdf(idParte: Union[int, str]):
    # Removed async.
    # Note: create_pdf called get_parte which is now sync, so this must be sync or handle it.
    # Since we are refactoring, let's keep it clean.
    # get_parte logic is above. We can call the DB functions directly or the function above.
    # Calling the router function directly is okay if it returns the object we need.

    # However, get_parte raises HTTPException, which is fine.
    pp = get_parte(int(idParte))  # Reuse logic

    handle_signature(pp)
    create_pdf_file(pp)
    if pp:
        return {"mensaje": "OK"}
    else:
        return status.HTTP_404_NOT_FOUND
