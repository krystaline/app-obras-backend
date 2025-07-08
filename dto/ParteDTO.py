from typing import List, Optional, Any
from pydantic import BaseModel
from entities.LineaPedido import LineaPedidoDTO, Linea_pedido, LineaPedidoPost


class ParteDTO(BaseModel):
    idOferta: Optional[int] = None  # Often id is None when creating a new item, then assigned by DB
    idParte: Optional[int] = None
    pdf: str
    signature: str = ""


class ParteRecibidoPost(BaseModel):
    id_oferta: int
    id_parte: int
    signature: str = ""
    lineas: List[LineaPedidoPost] = []
    comentarios: Optional[str] = ''
