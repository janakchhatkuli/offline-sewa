"""QR & transaction routes. Implement in Block 3A."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/create-offline-qr")
async def create_offline_qr():
    return {"todo": "Block 3A: create QR"}


@router.post("/verify-offline-qr")
async def verify_offline_qr():
    return {"todo": "Block 3A: verify QR"}
