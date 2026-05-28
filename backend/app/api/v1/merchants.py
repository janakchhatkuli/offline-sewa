"""Merchant routes (Block 3A)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantRead

router = APIRouter()


@router.post("", response_model=MerchantRead, status_code=201)
async def create_merchant(
    payload: MerchantCreate, db: AsyncSession = Depends(get_db)
) -> MerchantRead:
    existing = await db.execute(select(Merchant).where(Merchant.phone == payload.phone))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail={"error": "phone_exists", "detail": "merchant with this phone already exists"},
        )
    merchant = Merchant(name=payload.name, phone=payload.phone)
    db.add(merchant)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"error": "phone_exists", "detail": "merchant with this phone already exists"},
        )
    await db.refresh(merchant)
    return MerchantRead.model_validate(merchant)


@router.get("/{merchant_id}", response_model=MerchantRead)
async def get_merchant(
    merchant_id: str, db: AsyncSession = Depends(get_db)
) -> MerchantRead:
    merchant = await db.get(Merchant, merchant_id)
    if merchant is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "detail": "merchant not found"},
        )
    return MerchantRead.model_validate(merchant)


@router.post("/{merchant_id}/settle")
async def settle(merchant_id: str):
    return {"todo": "Block 3B: settlement", "merchant_id": merchant_id}
