from fastapi import APIRouter
from db.azure_funcs import get_workers

router = APIRouter(
    prefix="/api/workers",
    tags=["workers"]
)

@router.get("")
async def list_users():
    # Kept async because get_workers() in main.py was awaited: `await get_workers()`
    # Assuming azure_funcs.get_workers is indeed async.
    workers = await get_workers()
    if workers:
        return workers
    else:
        return []
