from pydantic import BaseModel
from typing import List
from entities.Actividad import Actividades
from entities.Manager import Manager
from entities.Project import ProyectoObra
import datetime


class ParteDTO(BaseModel):
    id: int
    project: ProyectoObra
    actividades: List[Actividades]
    teamManager: Manager
    status: str = "active"
    signature: str = ""  # almaceno la firma en str y la parseo luego !!
    parteDate: datetime.datetime  # ¡CAMBIADO AQUÍ! (o déjalo como str si realmente no necesitas el objeto datetime)
    comentarios: str = ""
