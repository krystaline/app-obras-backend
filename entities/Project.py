from typing import Optional

from pydantic import BaseModel
from entities.Manager import Manager



class ProyectoObra(BaseModel):
    id: Optional[str]
    descripcion: Optional[str]



