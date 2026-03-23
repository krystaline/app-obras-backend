from db.db_connection import get_lineas_enriquecidas
from fastapi import APIRouter

router = APIRouter(tags=["general"])


@router.get("/")
def root():
    # Removed async
    return []


@router.get("/api/actividades")
def get_actividades():
    # Placeholder from original
    return []


@router.get("/api/proyectos")
def get_proyectos():
    # Placeholder from original
    return []
