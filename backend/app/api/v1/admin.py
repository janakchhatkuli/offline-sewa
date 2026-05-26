"""Admin dashboard routes. Implement in Block 6."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/stats")
async def stats():
    return {"todo": "Block 6: aggregate stats"}


@router.get("/transactions")
async def transactions():
    return {"todo": "Block 6: list transactions"}
