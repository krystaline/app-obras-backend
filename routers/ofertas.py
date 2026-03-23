from db.db_queries import get_lineas_con_oferta
from fastapi import APIRouter, HTTPException, status

from entities.LineaPedido import Linea_pedido
from db.db_connection import get_linea_por_oferta, get_lineas, get_lineas_enriquecidas
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


@router.get("/ofertas", status_code=status.HTTP_200_OK)
def listar_ofertas():
    # Removed async
    try:
        lista = parse_ofertas()
        return lista
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing ofertas: {e}")


@router.get("/lineas/{idOferta}", status_code=status.HTTP_200_OK)
def listar_lineas_oferta(idOferta: int):
    # Removed async
    try:
        lista_dicts = get_linea_por_oferta(idOferta)
        # If None is returned
        if lista_dicts is None:
            return []

        print(lista_dicts)
        try:
            # Esto daba error, se ha solucionado cambiando el tipo de datos en la entidad Linea_pedido
            # Lo siguiente es ver cómo filtrar los datos bien (sacar datos de pers_partes_app y
            # comprobar si están, sacando el IdParteERP)
            lista_objetos_linea = [Linea_pedido(**d) for d in lista_dicts]
            print("### LISTA OBJETOS LINEA ###")
            print(lista_objetos_linea)
            print("###")
            return lista_objetos_linea
        except Exception as e:
            print(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing lineas for oferta {idOferta}: {e}"
        )


@router.get("/{idOferta}/lineas", status_code=status.HTTP_200_OK)
def listar_lineas_ejecutadas(idOferta: int):
    # Endpoint para devolver líneas crudas de pers_partes_app
    try:
        # ahora vamos a listar:
        # - líneas del ERP: vw_lineas_oferta
        # - líneas de la app: pers_partes_app
        data = get_lineas_con_oferta(idOferta)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting executed lineas for oferta {idOferta}: {e}",
        )


@router.get("/lineas/{idOferta}/{idlinea}", status_code=status.HTTP_200_OK)
def listar_linea_oferta(idOferta: int, idlinea: int):
    try:
        lista_lineas = get_cached_lineas()
        for linea in lista_lineas:
            if (
                linea.get("ocl_IdOferta") == idOferta
                and linea.get("ocl_idlinea") == idlinea
            ):
                return linea
        raise HTTPException(
            status_code=404, detail=f"Linea {idlinea} for oferta {idOferta} not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting linea: {e}")


@router.get("/{idOferta}/lineasEnriquecidas")
def listar_lineas_enriquecidas(idOferta: int):
    try:
        lista_enriquecidas = get_lineas_enriquecidas(idOferta)
        return lista_enriquecidas
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing lineas for oferta {idOferta}: {e}"
        )
