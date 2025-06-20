from pydantic import BaseModel
from entities.Manager import Manager
from entities.Contact import Contact
import datetime



class ProyectoObra(BaseModel):
    id: str
    title: str
    contact: Contact
    teamManager: Manager
    obraDate: datetime.datetime  # ¡CAMBIADO AQUÍ!

