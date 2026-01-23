from db.db_queries import get_lineas_con_oferta
from fastapi import APIRouter
from typing import List, Optional

from entities.LineaPedido import Linea_pedido
from db.db_connection import get_linea_por_oferta, get_lineas
from utils.mappers import parse_ofertas

router = APIRouter(
    prefix="/api",  # The original paths were scattered: /api/ofertas, /api/lineas
    tags=["ofertas"],
)

# Cache-like behavior from main.py
# In main.py, lista_lineas = get_lineas() was called at module level.
# This means it was loaded ONCE at startup.
# To preserve this behavior (though it's not ideal for dynamic data), we can do:
_LISTA_LINEAS_CACHE = None


def get_cached_lineas():
    global _LISTA_LINEAS_CACHE
    if _LISTA_LINEAS_CACHE is None:
        _LISTA_LINEAS_CACHE = get_lineas() or []
    return _LISTA_LINEAS_CACHE


@router.get("/ofertas")
def listar_ofertas():
    # Removed async
    lista = parse_ofertas()
    return lista


@router.get("/lineas/{idOferta}")
def listar_lineas_oferta(idOferta: int):
    # Removed async
    lista_dicts = get_linea_por_oferta(idOferta)
    # If None is returned
    if lista_dicts is None:
        return []
    lista_objetos_linea = [Linea_pedido(**d) for d in lista_dicts]
    return lista_objetos_linea


@router.get("/{idOferta}/lineas")
def listar_lineas_ejecutadas(idOferta: int):
    # Endpoint para devolver líneas crudas de pers_partes_app
    return get_lineas_con_oferta(idOferta)


@router.get("/lineas/{idOferta}/{idlinea}")
def listar_linea_oferta(idOferta: int, idlinea: int):
    # Removed async
    # Using the cached list as per original main.py logic
    lista_lineas = get_cached_lineas()
    for linea in lista_lineas:
        if (
            linea.get("ocl_IdOferta") == idOferta
            and linea.get("ocl_idlinea") == idlinea
        ):
            return linea
    return None
