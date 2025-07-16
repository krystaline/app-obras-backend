from typing import List, Optional
from pydantic import BaseModel, Field
from entities.LineaPedido import LineaPedidoPDF, LineaPedidoPost


class ParteDTO(BaseModel):
    idOferta: Optional[int] = None
    idParte: Optional[int] = None
    pdf: str  # ¿Esto es la ruta al PDF o el contenido binario? Si es contenido, mejor usar bytes o base64
    firma: str = ""


class ParteRecibidoPost(BaseModel):
    idoferta: int
    nParte: int
    firma: str = ""
    lineas: List[LineaPedidoPost] = []  # Asumiendo que LineaPedidoPost es para recibir datos de la UI
    comentarios: Optional[str] = ''
    proyecto: str = ''
    oferta: str
    telefono: str
    fecha: str
    contacto_obra: str
    jefe_equipo: str
    pdf: Optional[str]


# **Modelo ajustado para la impresión de PDF y lectura de DB**
class ParteImprimirPDF(BaseModel):
    nParte: int = Field(..., alias="nParte")  # Alias si el campo de DB es diferente, ej. n_parte
    proyecto: str
    oferta: str = Field(..., alias="oferta")  # Si en DB se llama diferente, ajusta
    jefe_equipo: str
    telefono: str
    fecha: str  # Considera cambiar a date si la DB lo guarda como fecha
    contacto_obra: str
    comentarios: Optional[str] = None  # 'None' en lugar de un string vacío si es opcional y puede ser NULL
    lineas: List[LineaPedidoPDF] = []  # Asegúrate que esto se llene correctamente
    firma: str = Field(..., alias="firma")  # Si la columna en DB se llama 'firma'
    idoferta: int = Field(..., alias="idoferta")
    pdf: Optional[str] = None

    # Configuración para permitir la asignación por nombre de campo de la DB
    class Config:
        populate_by_name = True  # Permite que Pydantic use el alias para la asignación
        # Esto es importante para cargar desde un diccionario donde las claves son los nombres de columna de la DB
        # allow_population_by_field_name = True # Versiones antiguas de Pydantic
