from typing import List, Union
from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from exceptions import AppError, ValidationError as AppValidationError

from dto.ParteDTO import ParteRecibidoPost, ParteImprimirPDF
from entities.LineaPedido import LineaPedidoPDF
from entities.User import User

from db.db_connection import get_num_parte
from db.db_queries import (
    create_parte,
    create_pdf_file,
    get_lineas_pdf,
    get_parte_pdf,
)
from utils.files import handle_signature

router = APIRouter(prefix="/api/partes", tags=["partes"])

# Also including the /api/pdf endpoint here as it relates to partes
pdf_router = APIRouter(prefix="/api/pdf", tags=["pdf"])


# antes de esto, tendríamos que verificar si el trigger de AHORA se ha ejecutado y el resultado es OK


@router.post("", status_code=status.HTTP_201_CREATED)
def create_partes(parte: ParteRecibidoPost) -> ParteRecibidoPost:
    # Removed async to prevent blocking loop with synchronous DB calls
    print(parte)
    handle_signature(parte)
    try:
        print(parte)
        create_parte(parte)
        return parte
    except AppValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al crear el parte de obra: {e}"
        )


@router.get("/parte/{parteId}", status_code=status.HTTP_200_OK)
def get_parte(parteId: int):
    # Removed async
    try:
        parte_data_dict = get_parte_pdf(parteId)
        if not parte_data_dict:
            raise HTTPException(
                status_code=404,
                detail=f"Parte con ID parteAPP {parteId} no encontrado.",
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

        parte_obj = ParteImprimirPDF(**parte_data_dict)
        return parte_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {e}",
        )


@router.get("/lastId")
def get_last_id():
    # Removed async
    val = get_num_parte()
    # Handle None if no partes exist
    if val is None:
        return 1
    return val + 1


# todo: cambiar idParte por idParteERP o idParteAPP
@router.post("/{idParte}/workers", status_code=status.HTTP_201_CREATED)
def asignar_trabajadores_parte(idParte: Union[int, str], workers: List[User]):
    # Removed async
    try:
        if idParte:
            #    if asginar_trabajadores_bd(idParte, workers):
            return True
        raise HTTPException(
            status_code=404, detail=f"Parte con ID {idParte} no encontrado."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error asignando trabajadores: {e}"
        )


@pdf_router.get("/{idParte}")
def create_pdf(idParte: Union[int, str]):
    pp = get_parte(int(idParte))  # Reuse logic

    handle_signature(pp)
    create_pdf_file(pp)
    if pp:
        return {"mensaje": "OK"}
    else:
        return status.HTTP_404_NOT_FOUND
