"""Customer routes. Implement in Block 3A."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/{customer_id}")
async def get_customer(customer_id: str):
    return {"todo": "Block 3A: return customer", "customer_id": customer_id}
