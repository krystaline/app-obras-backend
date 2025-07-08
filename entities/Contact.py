from pydantic import BaseModel


class Cliente(BaseModel): # Esto en verdad son Clientes
    id: str
    nombre: str

