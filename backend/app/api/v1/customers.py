"""Customer routes (Block 3A)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerRead

router = APIRouter()


@router.post("", response_model=CustomerRead, status_code=201)
async def create_customer(
    payload: CustomerCreate, db: AsyncSession = Depends(get_db)
) -> CustomerRead:
    existing = await db.execute(select(Customer).where(Customer.phone == payload.phone))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail={"error": "phone_exists", "detail": "customer with this phone already exists"},
        )
    customer = Customer(
        name=payload.name,
        phone=payload.phone,
        online_balance=payload.online_balance,
        offline_balance=payload.offline_balance,
    )
    db.add(customer)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"error": "phone_exists", "detail": "customer with this phone already exists"},
        )
    await db.refresh(customer)
    return CustomerRead.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: str, db: AsyncSession = Depends(get_db)
) -> CustomerRead:
    customer = await db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "detail": "customer not found"},
        )
    return CustomerRead.model_validate(customer)
