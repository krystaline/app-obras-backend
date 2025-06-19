from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import datetime
from fastapi.middleware.cors import CORSMiddleware
import base64

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]


class ParteObra(BaseModel):
    id: int
    title: str
    description: str
    status: str
    createdAt: datetime.date


class Contact(BaseModel):
    id: str
    title: str
    phone: int
    signature: str


class Manager(BaseModel):
    id: str
    name: str


class Actividades(BaseModel):
    id: int
    name: str
    cantidad: int
    unidad: str


class ProyectoObra(BaseModel):
    id: str
    title: str
    contact: Contact
    teamManager: Manager
    obraDate: datetime.datetime  # ¡CAMBIADO AQUÍ!


class ParteDTO(BaseModel):
    id: int
    project: ProyectoObra
    actividades: List[Actividades]
    teamManager: Manager
    status: str = "active"
    signature: str = ""  # almaceno la firma en str y la parseo luego !!
    parteDate: datetime.datetime  # ¡CAMBIADO AQUÍ! (o déjalo como str si realmente no necesitas el objeto datetime)
    comentarios: str = ""


db_managers: List[Manager] = [
    Manager(id="1", name="Alessandro Volta")
]

db_contacts: List[Contact] = [
    Contact(id='1', title="Vicente Hernández", signature="VCLX", phone=123456789),
    Contact(id='2', title="Paula Brotons", signature="PBRQ", phone=987654321),
    Contact(id='3', title="Sergio Guirao", signature="SRGO", phone=123789456),
]

db_proyectos: List[ProyectoObra] = [
    ProyectoObra(id='1', title="CRC Orihuela", contact=db_contacts[0], obraDate=datetime.datetime(2020, 6, 1),
                 teamManager=db_managers[0]),
    ProyectoObra(id='2', title="Ferrovial", contact=db_contacts[2], obraDate=datetime.datetime(2020, 6, 1),
                 teamManager=db_managers[0]),
]

db_actividades: List[Actividades] = [
    Actividades(id=1, name="Suministro", cantidad=2, unidad="metros")
]

db_partes: List[ParteDTO] = [
    ParteDTO(id=540, parteDate=datetime.datetime.now(),
             teamManager=db_managers[0],
             actividades=db_actividades,
             project=db_proyectos[0], status="pending")
]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/partes")
async def get_partes():
    return db_partes


@app.get("/api/partes/{id}")
async def get_parte(id: int):
    for parte in db_partes:
        if parte.id == id:
            return parte


@app.get("/api/managers")
async def get_managers():
    return db_managers


@app.get("/api/proyectos")
async def get_proyectos():
    return db_proyectos


@app.get("/api/contacts")
async def get_contacts():
    return db_contacts


@app.post("/api/partes")
async def create_partes(parte: ParteDTO):
    parte.id = db_partes[-1].id + 1
    handle_signature(parte)
    db_partes.append(parte)
    return parte


@app.get("/api/partes/lastId")
async def get_last_id():
    return db_partes[-1].id + 1


def handle_signature(parte: ParteDTO):
    firma = parte.signature
    if "," in firma:
        header, encoded_data = firma.split(",", 1)
    else:
        encoded_data = firma

    try:
        decoded_image_data = base64.b64decode(encoded_data)

        # Ahora puedes guardar estos datos binarios como una imagen
        with open("firmas/" + parte.project.title.replace(" ", "")
                  + "_" + parte.project.id + "_"
                  + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                  + "_" + parte.project.contact.title.replace(" ", "")
                  + "_signature.png", "wb") as f:
            f.write(decoded_image_data)

    except Exception as e:
        print(f"Error al decodificar la firma: {e}")
