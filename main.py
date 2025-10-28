import base64
import datetime
import uuid
from http.client import HTTPResponse
from pathlib import Path
from typing import List

from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from db import db_queries
from db.azure_funcs import get_workers
from db.db_connection import get_lineas, get_ofertas, get_num_parte, get_linea_por_oferta
from db.db_queries import test_connection, create_parte, create_pdf_file, get_lineas_pdf, get_parte_pdf, \
    asginar_trabajadores_bd, get_trabajadores_parte, subir_imagen, crear_parte_mo_bd, get_materiales_db
from db.partes_manoobra import get_partes_mo_db
from dto.ParteDTO import ParteRecibidoPost, ParteImprimirPDF
from entities.Actividad import Actividades
from entities.Contact import Cliente
from entities.Oferta import Oferta
from entities.Project import ProyectoObra
from entities.LineaPedido import Linea_pedido, LineaPedidoPDF
from entities.User import User
from entities.partesmo.ParteMO import ParteMORecibir

IMAGES_DIR = Path(__file__).parent / 'imagenes'

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
            parsed_ofertas.append(Oferta(**o))
        except ValidationError as e:
            print(f"Error de validación para oferta: {o} - {e}")
    return parsed_ofertas


def parsear_datos(lista):
    for linea in lista:
        lista_actividades.append(crear_actividad(linea))
    return [lista_actividades]


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


@app.get("/api/proyectos")
async def get_proyectos():
    return []  # lista_datos[2]


@app.get("/api/ofertas")
async def listar_ofertas():
    lista = parse_ofertas()
    return lista


@app.post("/api/partes")
async def create_partes(parte: ParteRecibidoPost) -> ParteRecibidoPost:
    # La validación de Pydantic ya ocurre automáticamente al recibir el JSON
    print(parte)
    handle_signature(parte)  # Asegúrate que esta función use parte.signature correctamente
    try:
        print(parte)
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
    return parte_obj


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


def handle_signature(parte: ParteImprimirPDF | ParteRecibidoPost, ):
    firma = parte.firma
    if "," in firma:
        header, encoded_data = firma.split(",", 1)
    else:
        encoded_data = firma

    try:
        decoded_image_data = base64.b64decode(encoded_data)
        nombre_firma = (str(parte.nParte) + "_"
                        + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        + "_signature.png")
        # Ahora puedes guardar estos datos binarios como una imagen
        with open("firmas/" + nombre_firma, "wb") as f:
            f.write(decoded_image_data)
            parte.pdf = nombre_firma
            return parte
    except Exception as e:
        print(f"Error al decodificar la firma: {e}")


@app.get("/api/queries")
def qu():
    return test_connection()


@app.get("/api/pdf/{idParte}")
async def create_pdf(idParte: int | str):
    pp = await get_parte(idParte)
    handle_signature(pp)
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


@app.get("/api/workers")
async def list_users():
    workers = await get_workers()
    if workers:
        return workers
    else:
        return []


@app.post('/api/partes/{idParte}/workers', status_code=201)
async def asignar_trabajadores_parte(idParte: int | str, workers: List[User]):
    if idParte:
        if asginar_trabajadores_bd(idParte, workers):
            return True
    return HTTPException(status_code=404, detail=f"Parte con ID {idParte} no encontrado.")


@app.get('/api/partes/{idParte}/workers')
async def listar_trabajadores_parte(idParte: int):
    return get_trabajadores_parte(idParte)


@app.post('/api/imagen')
async def get_imagen(
        image: UploadFile = File(...),
        idOferta: int = Form(...)
):
    print(f"ID de la oferta: {idOferta}")
    print(f"Nombre del archivo de imagen: {image.content_type}")
    image_path = str(uuid.uuid4()) + '.jpg'
    print(f"UUID: {image_path}")
    try:
        with open(f"imagenes/{image_path}", "wb") as buffer:
            while content := await image.read(1024):
                buffer.write(content)
        db_queries.subir_imagen(idOferta, image_path)
        print(f"UUID: {image_path}")
        return status.HTTP_200_OK
    except Exception as e:
        print(f"Error al guardar la imagen: {e}")
        return status.HTTP_500_INTERNAL_SERVER_ERROR


@app.get('/api/oferta/imagenes/{idOferta}')
async def get_imagenes_for_oferta(idOferta: int):
    images = db_queries.get_imagenes_por_oferta(idOferta)
    print(images)
    return {"images": images}


@app.get("/api/images/imagenes/{image_name}")
async def get_image(image_name: str):
    image_path = IMAGES_DIR / image_name

    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    img = FileResponse(image_path)
    print("h")
    print(img.filename)
    return img


# PARTES MANO DE OBRA
@app.get("/api/partesMO/{idOferta}")
async def get_partes_mo(idOferta: int):
    print(idOferta)
    return get_partes_mo_db(idOferta)


@app.post("/api/partesMO/new", status_code=201)
async def new_parte_mo(parte: ParteMORecibir):
    if crear_parte_mo_bd(parte).message == "OK":
        print(parte)
        return parte
    else:
        return HTTPException(status_code=500, detail="Error al crear el parte")


@app.get("/api/materiales")
async def get_materiales():
    return get_materiales_db()
