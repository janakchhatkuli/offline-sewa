"""SMS webhook routes. Implement in Block 3B."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/confirm-payment")
async def confirm_payment():
    return {"todo": "Block 3B: process incoming SMS"}
