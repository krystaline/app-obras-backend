import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException
from fastapi.responses import FileResponse
from db import db_queries

# Assuming this path is relative to the root of the repo where main.py was.
# When running from main.py, Path(__file__).parent / 'imagenes' depended on main.py location.
# Now we are in routers/. so we need to go up one level.
# Ideally, define this in a config. 
# For now, we will construct it relative to the execution root (CWD usually).

IMAGES_DIR = Path("imagenes") 
# Ensure it exists
# if not IMAGES_DIR.exists():
#    IMAGES_DIR.mkdir()

router = APIRouter(
    prefix="/api",
    tags=["media"]
)


@router.post('/imagen')
async def get_imagen(
        image: UploadFile = File(...),
        idOferta: int = Form(...)
):
    # Kept async because file I/O with UploadFile is async-compatible in FastAPI
    # but the subsequent db call logic is sync.
    # However, create_file is IO bound.
    
    print(f"ID de la oferta: {idOferta}")
    print(f"Nombre del archivo de imagen: {image.content_type}")
    
    ext = ".jpg" # Defaulting to jpg as per original code, or extract from filename
    image_path = str(uuid.uuid4()) + ext
    
    print(f"UUID: {image_path}")
    try:
        # Saving to generic "imagenes/" folder in CWD
        with open(f"imagenes/{image_path}", "wb") as buffer:
            while content := await image.read(1024):
                buffer.write(content)
        
        # db call is sync, so it might block loop briefly.
        db_queries.subir_imagen(idOferta, image_path)
        
        print(f"UUID: {image_path}")
        return status.HTTP_200_OK
    except Exception as e:
        print(f"Error al guardar la imagen: {e}")
        return status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get('/oferta/imagenes/{idOferta}')
def get_imagenes_for_oferta(idOferta: int):
    # Removed async
    images = db_queries.get_imagenes_por_oferta(idOferta)
    print(images)
    return {"images": images}


@router.get("/images/imagenes/{image_name}")
def get_image(image_name: str):
    # Removed async
    image_path = IMAGES_DIR / image_name

    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    img = FileResponse(image_path)
    # print("h")
    # print(img.filename)
    return img
