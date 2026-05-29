"""Customer routes (Block 3A)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_principal
from app.db.session import get_db
from app.models.customer import Customer
from app.models.transaction import OfflineTransaction
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerTopUp
from app.schemas.transaction import VerifyOfflineQRResponse

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


@router.post("/{customer_id}/topup", response_model=CustomerRead)
async def topup_customer(
    customer_id: str,
    payload: CustomerTopUp,
    db: AsyncSession = Depends(get_db),
    principal=Depends(get_current_principal),
) -> CustomerRead:
    role, user = principal
    if role != "customer" or user.customer_id != customer_id:
        raise HTTPException(
            status_code=403,
            detail={"error": "forbidden", "detail": "cannot top up other customers"},
        )
    customer = await db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "detail": "customer not found"},
        )
    if payload.target == "online":
        customer.online_balance = (customer.online_balance or 0) + payload.amount
    else:
        customer.offline_balance = (customer.offline_balance or 0) + payload.amount
    await db.commit()
    await db.refresh(customer)
    return CustomerRead.model_validate(customer)


@router.get("/{customer_id}/transactions", response_model=list[VerifyOfflineQRResponse])
async def list_customer_transactions(
    customer_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    principal=Depends(get_current_principal),
) -> list[VerifyOfflineQRResponse]:
    role, user = principal
    if role != "customer" or user.customer_id != customer_id:
        raise HTTPException(
            status_code=403,
            detail={"error": "forbidden", "detail": "cannot view other customers"},
        )
    limit = max(1, min(limit, 200))
    result = await db.execute(
        select(OfflineTransaction)
        .where(OfflineTransaction.customer_id == customer_id)
        .order_by(OfflineTransaction.created_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        VerifyOfflineQRResponse(
            transaction_id=t.transaction_id,
            status=t.status.value,
            customer_id=t.customer_id,
            merchant_id=t.merchant_id,
            amount=t.amount,
            nonce=t.nonce,
            created_at=t.created_at,
        )
        for t in rows
    ]
