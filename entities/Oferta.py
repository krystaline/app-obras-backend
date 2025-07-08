import datetime

from pydantic import BaseModel


class Oferta(BaseModel):
    idOferta: int
    fecha: str | None
    cliente: str | None = ""
    idProyecto: str
    descripcion: str | None = None
    observaciones: str | None = None
    status: str

