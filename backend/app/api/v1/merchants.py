"""Merchant routes. Implement in Block 3A."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/{merchant_id}")
async def get_merchant(merchant_id: str):
    return {"todo": "Block 3A: return merchant", "merchant_id": merchant_id}


@router.post("/{merchant_id}/settle")
async def settle(merchant_id: str):
    return {"todo": "Block 3B: settlement", "merchant_id": merchant_id}
