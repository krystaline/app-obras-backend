
from pydantic import BaseModel

class Actividades(BaseModel):
    id: int
    name: str
    cantidad: int
    unidad: str

