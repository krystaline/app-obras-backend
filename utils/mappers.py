from typing import List
from entities.Actividad import Actividades
from entities.Oferta import Oferta
from entities.LineaPedido import Linea_pedido
from pydantic import ValidationError
from db.db_connection import get_ofertas


def crear_actividad(linea: Linea_pedido):
    return Actividades(
        idArticulo=linea.ocl_IdArticulo,
        descripcion=linea.ocl_Descrip,
        cantidad=linea.ocl_Cantidad,
        # numbultos removed as it is not in Linea_pedido DDL
        unidadesPres=linea.ocl_UnidadesPres,
        idParte=linea.ppcl_IdParte,
        unidadMedida=linea.ppcl_UnidadMedida,
        certificado=linea.ppcl_Certificado,
    )


# Note: lists like lista_actividades were global in main.py.
# Depending on usage, we might need a different approach, but for now moving the logic.
# If these lists are stateful caches, they should be managed in a service or dependency, not just global vars in a util.
# However, based on main.py, they seemed to be populated by `parsear_datos`.
# I will keep the function pure here returning lists.


def parse_ofertas() -> List[Oferta]:
    ofertas = get_ofertas()
    parsed_ofertas = []
    if not ofertas:
        return []
    for o in ofertas:
        try:
            parsed_ofertas.append(Oferta(**o))
        except ValidationError as e:
            print(f"Error de validación para oferta: {o} - {e}")
    return parsed_ofertas


def parsear_datos(lista):
    # This was populating a global list in main.py.
    # Adapting to return the list instead.
    lista_actividades = []
    for linea in lista:
        lista_actividades.append(crear_actividad(linea))
    return [lista_actividades]
