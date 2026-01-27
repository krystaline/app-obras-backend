from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import partes, ofertas, media, mano_obra, workers, general, nuevo
from dependencies import verify_auth_headers

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

# Include Routers with global authentication
app.include_router(partes.router, dependencies=[Depends(verify_auth_headers)])
app.include_router(partes.pdf_router, dependencies=[Depends(verify_auth_headers)])
app.include_router(ofertas.router, dependencies=[Depends(verify_auth_headers)])
app.include_router(media.router, dependencies=[Depends(verify_auth_headers)])
app.include_router(mano_obra.router, dependencies=[Depends(verify_auth_headers)])
app.include_router(workers.router, dependencies=[Depends(verify_auth_headers)])
app.include_router(
    general.router
)  # General might contain public endpoints? Keeping public for now unless specified.
app.include_router(nuevo.router, dependencies=[Depends(verify_auth_headers)])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8082, reload=True)
