from typing import Union, Optional

from pydantic import BaseModel

class Actividades(BaseModel):
    idArticulo: str
    descripcion: str
    cantidad: float
    numbultos: Optional[int]
    unidadesPres: float
    idParte: Optional[int]
    unidadMedida: Optional[float]
    certificado: Union[int, bool]
