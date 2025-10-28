from typing import List
from pydantic import BaseModel
import datetime


class ParteMO(BaseModel):
    id: int
    title: str
    description: str
    status: str
    createdAt: datetime.date
    updatedAt: datetime.date
    idProyecto: str
    idParte: str
    idProyecto: str
    descripcion: str | None = None
    observaciones: str | None = None
    status: str


class Materiales(BaseModel):
    idArticulo : str
    descripcion : str | None = None
    cantidad : int
    precio : int
    lote : str


class Desplazamiento(BaseModel):
    id: float
    distancia: float
    fecha: str
    matricula: str


class ManoDeObra(BaseModel):
    idManoObra: float
    accion: str
    fecha: str
    precio: float
    unidades: float


class ParteMORecibir(BaseModel):
    idParteMO: str
    idProyecto: str
    idOferta: int
    usuario: str
    materiales: List[Materiales]
    desplazamientos: List[Desplazamiento]
    manosdeobra: List[ManoDeObra]
    comentarios: str
    fecha: str
