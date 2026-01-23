from typing import Optional

from pydantic import ConfigDict, BaseModel, Field


class Linea_pedido(BaseModel):
    ocl_IdOferta: str
    ocl_idlinea: str
    ocl_revision: int
    occ_SerieOferta: Optional[int] = None
    occ_idproyecto: Optional[str] = None
    ocl_IdArticulo: str
    ocl_Descrip: Optional[str] = None
    ocl_Cantidad: Optional[float] = None
    ocl_UnidadesPres: Optional[float] = None
    ppcl_IdParte: Optional[str] = None
    ppcl_Capitulo: Optional[str] = None
    ocl_tipoUnidad: Optional[str] = None
    ppcl_cantidad: Optional[float] = None
    ppcl_UnidadMedida: Optional[float] = None
    ppcl_Certificado: int
    idParteAPP: Optional[int] = None
    borradoERP: bool = False


class LineaPedidoPost(BaseModel):
    id_linea: int  # Parece ser el 'ocl_idlinea' o 'IdLinea'
    id_parte: int  # Se refiere al Id del parte de obra al que pertenece
    id_oferta: int  # Cambiado a int, asumiendo que es un ID numérico
    descripcion: str
    medida: str  # Esto se mapea a 'tipounidad' en LineaPedidoPDF
    unidades_puestas_hoy: float  # Cantidad puesta hoy
    unidades_totales: float  # Cantidad total (ofertada)
    ya_certificado: int  # 0 o 1, podría ser bool
    cantidad: int  # lo que ya tengo hecho (para sumarlo)

    capitulo: Optional[int] = None  # Si es opcional
    idArticulo: Optional[str] = None  # 'ocl_IdArticulo' o similar
    idParteERP: Optional[int] = None
    idParteAPP: Optional[int] = None
    borradoERP: Optional[int] = None


class LineaPedidoDTO:
    # Esta clase parece redundante si usas LineaPedidoPost y LineaPedidoPDF
    # Si su propósito es mapear algo de la DB, mejor que sea un BaseModel de Pydantic
    # para aprovechar la validación. Si es una entidad de DB, podría ser más clara.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.id_parte = kwargs.get("id_parte")
        self.id_oferta = kwargs.get("id_oferta")
        self.descripcion = kwargs.get("descripcion")
        self.unidades_totales = kwargs.get("unidades_totales")
        self.medida = kwargs.get("medida")
        self.unidades_puestas_hoy = kwargs.get("unidades_puestas_hoy")
        self.ya_certificado = kwargs.get("ya_certificado")

    def __repr__(self):
        return f"LineaPedidoDTO(id={self.id}, descripcion={self.descripcion})"


# **Modelo ajustado para la impresión de PDF y lectura de DB**
class LineaPedidoPDF(BaseModel):
    # Asegúrate que estos nombres coincidan con los 'AS' en tus consultas SQL
    id: int = Field(..., alias="id")
    id_linea: int = Field(
        ..., alias="IdLinea"
    )  # O el nombre de la columna en la DB para el ID de línea
    descripcion: str = Field(..., alias="DescripArticulo")
    cantidad: float = Field(
        ..., alias="cantidad"
    )  # Este es el campo que se usa en pdf_manager para 'Cant.'
    unidadMedida: str = Field(
        ..., alias="UnidadMedida"
    )  # Este es el campo que se usa en pdf_manager para 'Unid.'

    class Config:
        populate_by_name = True
