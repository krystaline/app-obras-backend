from pydantic import ConfigDict, BaseModel


class Linea_pedido:
    def __init__(self, **kwargs):
        self.ocl_IdOferta = kwargs.get('ocl_IdOferta')
        self.ocl_idlinea = kwargs.get('ocl_idlinea')
        self.ocl_revision = kwargs.get('ocl_revision')
        self.occ_SerieOferta = kwargs.get('occ_SerieOferta')
        self.occ_revision = kwargs.get('occ_revision')
        self.occ_idempresa = kwargs.get('occ_idempresa')
        self.occ_añonum = kwargs.get('occ_añonum')
        self.occ_numoferta = kwargs.get('occ_numoferta')
        self.occ_descrip = kwargs.get('occ_descrip')
        self.occ_idestado = kwargs.get('occ_idestado')
        self.occ_idproyecto = kwargs.get('occ_idproyecto')
        self.cd_idcliente = kwargs.get('cd_idcliente')
        self.cd_Cliente = kwargs.get('cd_Cliente')
        self.ocl_IdArticulo = kwargs.get('ocl_IdArticulo')
        self.ocl_Descrip = kwargs.get('ocl_Descrip')
        self.ocl_Cantidad = kwargs.get('ocl_Cantidad')
        self.ocl_PesoNeto = kwargs.get('ocl_PesoNeto')
        self.ocl_NumBultos = kwargs.get('ocl_NumBultos')
        self.ocl_UnidadesPres = kwargs.get('ocl_UnidadesPres')
        self.ppcl_IdParte = kwargs.get('ppcl_IdParte')
        self.ppcl_Capitulo = kwargs.get('ppcl_Capitulo')
        self.ppcl_IdArticulo = kwargs.get('ppcl_IdArticulo')
        self.ppcl_DescripArticulo = kwargs.get('ppcl_DescripArticulo')
        self.ppcl_cantidad = kwargs.get('ppcl_cantidad')
        self.ppcl_UnidadMedida = kwargs.get('ppcl_UnidadMedida')
        self.ppcl_Certificado = kwargs.get('ppcl_Certificado')
        self.ppcl_IdParte = kwargs.get('ppcl_IdParte')
        self.ppcc_observaciones = kwargs.get('ppcc_observaciones')

    def __repr__(self):
        return f"Linea_pedido(IdOferta={self.ocl_IdOferta}, idlinea={self.ocl_idlinea}, revision={self.ocl_revision} "


class LineaPedidoPost(BaseModel):
    id: int
    id_parte: int
    id_oferta: int
    descripcion: str
    medida: str
    unidades_puestas_hoy: float
    unidades_totales: float
    ya_certificado: int


class LineaPedidoDTO:
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.id_parte = kwargs.get('id_parte')
        self.id_oferta = kwargs.get('id_oferta')
        self.descripcion = kwargs.get('descripcion')
        self.unidades_totales = kwargs.get('unidades_totales')  # se llama de otra manera
        self.medida = kwargs.get('medida')  # se llama de otra manera
        self.unidades_puestas_hoy = kwargs.get('unidades_puestas_hoy')  # idem
        self.ya_certificado = kwargs.get('ya_certificado')

    def __repr__(self):
        return f"ba"
