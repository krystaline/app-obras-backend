from fastapi import APIRouter
from db.db_queries import test_connection

router = APIRouter(
    tags=["general"]
)

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

@router.get("/api/queries")
def qu():
    # Removed async
    return test_connection()
