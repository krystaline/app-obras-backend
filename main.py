import base64
import datetime
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.db_connection import get_lineas, get_ofertas, get_num_parte
from db.db_queries import test_connection, create_parte
from dto.ParteDTO import ParteDTO, ParteRecibidoPost
from entities.Actividad import Actividades
from entities.Contact import Cliente
from entities.Oferta import Oferta
from entities.Project import ProyectoObra
from entities.LineaPedido import Linea_pedido

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

# db_partes: List[ParteDTO] = [
#   ParteDTO(id=540, parteDate=datetime.datetime.now(),
#           teamManager=db_managers[0],
#          actividades=db_actividades,
#         project=db_proyectos[0], status="pending")
# ]
app = FastAPI()
# test
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/api/partes")
# async def get_partes():
#    get_all_partes()
#    return db_partes


# @app.get("/api/partes/{id}")
# async def get_parte(id: int):
#    for parte in db_partes:
#        if parte.id == id:
#            return parte
#    return None


# seteo las lineas del parte


def obtener_lineas_pedido():
    lineas_pedido = get_lineas()
    lista = []
    for linea in lineas_pedido:
        lista.append(Linea_pedido(**linea))
    return lista


def crear_actividad(linea: Linea_pedido):
    return Actividades(
        idArticulo=linea.ocl_IdArticulo,
        descripcion=linea.ocl_Descrip,
        cantidad=linea.ocl_Cantidad,
        numbultos=linea.ocl_NumBultos,
        unidadesPres=linea.ocl_UnidadesPres,
        idParte=linea.ppcl_IdParte,
        unidadMedida=linea.ppcl_UnidadMedida,
        certificado=linea.ppcl_Certificado,
    )


def crear_cliente(linea: Linea_pedido):
    return Cliente(
        id=linea.cd_idcliente,
        nombre=linea.cd_Cliente,
    )


def crear_proyecto(linea: Linea_pedido):
    return ProyectoObra(
        id=linea.occ_idproyecto,
        descripcion=linea.occ_descrip
    )


lista_actividades = []
lista_clientes = []
lista_proyectos = []
lista_ofertas = []

lista_lineas = get_lineas()


def parse_ofertas() -> List[Oferta]:
    ofertas = get_ofertas()
    return ofertas


def parsear_datos(lista):
    for linea in lista:
        lista_actividades.append(crear_actividad(linea))
        lista_clientes.append(crear_cliente(linea))
        lista_proyectos.append(crear_proyecto(linea))
    # lista_ofertas.append(crear_oferta(linea))
    return [lista_actividades, lista_clientes, lista_proyectos]


@app.get("/")
async def root():
    return []


# @app.get("/api/managers")
# async def get_managers():
#     return db_managers
#

@app.get("/api/actividades")
async def get_actividades():
    return []  # lista_datos[0]


@app.get("/api/clientes")
async def get_clientes():
    # db_contacts = get_all_contacts()
    return parsear_datos(lista_lineas)[1]


@app.get("/api/proyectos")
async def get_proyectos():
    return []  # lista_datos[2]


@app.get("/api/ofertas")
async def listar_ofertas():
    lista = parse_ofertas()
    return lista


@app.post("/api/partes")
async def create_partes(parte: ParteRecibidoPost) -> ParteRecibidoPost:
    #  parte.id = db_partes[-1].id + 1
    print(parte)
    handle_signature(parte)
    #  create_parte(parte)
    #   db_partes.append(parte)
    # create_part(parte)
    return parte


@app.get("/api/lineas")
async def listar_lineas():
    lista = obtener_lineas_pedido()
    return lista


@app.get("/api/lineas/{idoferta}")
async def listar_lineas_oferta(idoferta: int):
    lista = []

    for linea in lista_lineas:
        if linea.get('ocl_IdOferta') == idoferta:
            lista.append(linea)

    return lista


@app.get('/api/lineas/{idoferta}/{idlinea}')
async def listar_linea_oferta(idoferta: int, idlinea: int):
    for linea in lista_lineas:
        if linea.get('ocl_IdOferta') == idoferta and linea.get('ocl_idlinea') == idlinea:
            return linea
    return None


@app.get("/api/partes/lastId")
async def get_last_id():
    return get_num_parte()+1


def handle_signature(parte: ParteRecibidoPost):
    firma = parte.signature
    if "," in firma:
        header, encoded_data = firma.split(",", 1)
    else:
        encoded_data = firma

    try:
        decoded_image_data = base64.b64decode(encoded_data)

        # Ahora puedes guardar estos datos binarios como una imagen
        with open("firmas/"
                  + str(parte.id_parte) + "_"
                  + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                  + "_signature.png", "wb") as f:
            f.write(decoded_image_data)

    except Exception as e:
        print(f"Error al decodificar la firma: {e}")


@app.get("/api/queries")
def qu():
    return test_connection()
