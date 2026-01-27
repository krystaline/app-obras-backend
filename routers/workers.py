from fastapi import APIRouter, HTTPException, status
from db.azure_funcs import get_workers

router = APIRouter(prefix="/api/workers", tags=["workers"])


@router.get("", status_code=status.HTTP_200_OK)
async def list_users():
    try:
        # Kept async because get_workers() in main.py was awaited: `await get_workers()`
        # Assuming azure_funcs.get_workers is indeed async.
        workers = await get_workers()
        if workers:
            return workers
        else:
            return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving workers: {e}")
