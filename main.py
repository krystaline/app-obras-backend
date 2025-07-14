import base64
import datetime
from http.client import HTTPResponse
from typing import List

from fastapi import FastAPI, HTTPException, status

from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from db.db_connection import get_lineas, get_ofertas, get_num_parte, get_linea_por_oferta
from db.db_queries import test_connection, create_parte, create_pdf_file, get_lineas_pdf, get_parte_pdf
from dto.ParteDTO import ParteDTO, ParteRecibidoPost, ParteImprimirPDF
from entities.Actividad import Actividades
from entities.Contact import Cliente
from entities.Oferta import Oferta
from entities.Project import ProyectoObra
from entities.LineaPedido import Linea_pedido, LineaPedidoPost, LineaPedidoPDF

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
    parsed_ofertas = []
    for o in ofertas:
        try:
            # Asume que tu modelo Oferta puede inicializarse directamente con el diccionario
            parsed_ofertas.append(Oferta(**o))
        except ValidationError as e:
            print(f"Error de validación para oferta: {o} - {e}")
            # Decide si ignorar o manejar el error
    return parsed_ofertas


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


db_partes = []


@app.post("/api/partes")
async def create_partes(parte: ParteRecibidoPost) -> ParteRecibidoPost:
    # La validación de Pydantic ya ocurre automáticamente al recibir el JSON
    print(parte)
    handle_signature(parte)  # Asegúrate que esta función use parte.signature correctamente
    try:
        # Pasa el objeto parte Pydantic directamente a tu función de DB
        create_parte(parte)
        # db_partes.append(parte) # Si db_partes es solo un cache en memoria, puedes seguir usándolo.
        return parte
    except Exception as e:
        # Captura cualquier error que pueda haber sido relanzado desde db_queries
        raise HTTPException(status_code=500, detail=f"Error al crear el parte de obra: {e}")


@app.get("/api/partes/parte/{parteId}")
async def get_parte(parteId: int):
    # Obtener los datos del parte principal
    parte_data_dict = get_parte_pdf(parteId)
    if not parte_data_dict:
        raise HTTPException(status_code=404, detail=f"Parte con ID {parteId} no encontrado.")

    # Obtener las líneas asociadas
    lineas_data_list = get_lineas_pdf(parteId)
    validated_lineas = []
    for line_dict in lineas_data_list:
        try:
            # Aquí Pydantic debe mapear 'id', 'descripcion', 'cantidad', 'unidadMedida'
            # de tu LineaPedidoPDF con los alias de las columnas SQL
            validated_lineas.append(LineaPedidoPDF(**line_dict))
        except ValidationError as e:
            print(f"Error de validación para una línea de pedido (ID Parte: {parteId}): {e} - Datos: {line_dict}")
            # Decide cómo manejar esto: ¿Ignorar línea inválida o fallar la solicitud?
            # Por ahora, la ignoramos.
            continue

    # Asignar las líneas validadas al diccionario de datos del parte
    parte_data_dict["lineas"] = validated_lineas

    try:
        # Crear la instancia de ParteImprimirPDF desde el diccionario
        # Pydantic debería usar los alias y `populate_by_name = True`
        # para mapear correctamente las columnas de la DB a los campos del modelo.
        parte_obj = ParteImprimirPDF(**parte_data_dict)
    except ValidationError as e:
        print(f"Error de validación al crear ParteImprimirPDF desde DB: {e}")
        print(f"Datos del parte que causaron el error: {parte_data_dict}")
        raise HTTPException(status_code=500,
                            detail=f"Error interno del servidor: Fallo la validación de datos del parte principal - {e}")

    # Si todo va bien, crea el PDF y retorna el objeto
    return parte_obj


@app.get("/api/lineas")
async def listar_lineas():
    lista = obtener_lineas_pedido()
    return lista


@app.get("/api/lineas/{idoferta}")
async def listar_lineas_oferta(idoferta: int):
    lista_dicts = get_linea_por_oferta(idoferta)
    lista_objetos_linea = [Linea_pedido(**d) for d in lista_dicts]
    return lista_objetos_linea


@app.get('/api/lineas/{idoferta}/{idlinea}')
async def listar_linea_oferta(idoferta: int, idlinea: int):
    for linea in lista_lineas:
        if linea.get('ocl_IdOferta') == idoferta and linea.get('ocl_idlinea') == idlinea:
            return linea
    return None


@app.get("/api/partes/lastId")
async def get_last_id():
    print(get_num_parte() + 1)
    return get_num_parte() + 1


def handle_signature(parte: ParteRecibidoPost):
    firma = parte.firma
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
            # todo cambiar firma/pdf por la url de la imagen

    except Exception as e:
        print(f"Error al decodificar la firma: {e}")


@app.get("/api/queries")
def qu():
    return test_connection()


@app.get("/api/pdf/{idParte}")
async def create_pdf(idParte: int | str):
    pp = await get_parte(idParte)
    create_pdf_file(pp)
    if pp:
        return {"mensaje": "OK"}
    else:
        return status.HTTP_404_NOT_FOUND


@app.get("/api/partes/all")
async def get_all_partes_summary():
    # Esta función necesitaría implementarse en db/db_queries.py
    # para obtener una lista resumida de todos los partes de obra.
    # Por ejemplo, podría devolver ParteImprimirPDF[] sin las líneas completas
    # o un DTO más ligero con solo los campos principales.
    # Ejemplo: return get_all_partes_from_db()
    # Si no tienes esta función en db_queries.py, tendrías que crearla.
    # Por ahora, no podemos listar todos los partes sin esto.
    pass  #
