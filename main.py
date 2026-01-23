from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import partes, ofertas, media, mano_obra, workers, general, nuevo

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

# Include Routers
app.include_router(partes.router)  # /api/partes
app.include_router(partes.pdf_router)  # /api/pdf
app.include_router(ofertas.router)  # /api/ofertas, /api/lineas
app.include_router(media.router)  # /api/imagen, /api/oferta/imagenes
app.include_router(mano_obra.router)  # /api/partesMO, /api/materiales
app.include_router(workers.router)  # /api/workers
app.include_router(general.router)  # /, /api/actividades, /api/queries
app.include_router(nuevo.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8082, reload=True)
