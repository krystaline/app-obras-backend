from datetime import date
from typing import Optional
from pydantic import BaseModel


class Oferta(BaseModel):
    idOferta: int
    fecha: Optional[date] = None
    cliente: str
    idCliente: str
    contacto: Optional[str] = None
    idProyecto: Optional[str] = None
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None
    status: Optional[str] = None
    revision: Optional[int] = None
