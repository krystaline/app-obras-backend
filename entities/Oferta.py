import datetime

from pydantic import BaseModel


class Oferta(BaseModel):
    idOferta: int
    fecha: str | None
    cliente: str | None = ""
    idProyecto: str
    descripcion: str | None = None
    observaciones: str | None = None
    status: str = "activa"
    # def __init__(self, **kwargs):
    #     self.idOferta = kwargs.get('idOferta')
    #     self.fecha = kwargs.get('Fecha')
    #     self.cliente = kwargs.get('Cliente')
    #     self.idProyecto = kwargs.get('idProyecto')
    #     self.descripcion = kwargs.get('Descrip')
    #     self.observaciones = kwargs.get('Observaciones')
    #     self.status = 'activa' if False else 'completada'
