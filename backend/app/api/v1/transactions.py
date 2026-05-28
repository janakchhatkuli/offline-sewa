"""QR & transaction routes (Block 3A)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.transaction import (
    CreateOfflineQRRequest,
    CreateOfflineQRResponse,
    VerifyOfflineQRRequest,
    VerifyOfflineQRResponse,
)
from app.services import qr_service
from app.services.qr_service import QRServiceError

router = APIRouter()


def _raise(err: QRServiceError) -> None:
    raise HTTPException(
        status_code=err.http_status,
        detail={"error": err.code, "detail": str(err)},
    )


@router.post("/create-offline-qr", response_model=CreateOfflineQRResponse)
async def create_offline_qr(
    payload: CreateOfflineQRRequest,
    db: AsyncSession = Depends(get_db),
) -> CreateOfflineQRResponse:
    try:
        result = await qr_service.create_offline_qr(
            db, customer_id=payload.customer_id, amount=payload.amount
        )
    except QRServiceError as e:
        _raise(e)
    return CreateOfflineQRResponse(**result)


@router.post("/verify-offline-qr", response_model=VerifyOfflineQRResponse)
async def verify_offline_qr(
    payload: VerifyOfflineQRRequest,
    db: AsyncSession = Depends(get_db),
) -> VerifyOfflineQRResponse:
    try:
        txn = await qr_service.verify_offline_qr(
            db, merchant_id=payload.merchant_id, qr_payload=payload.qr_payload
        )
    except QRServiceError as e:
        _raise(e)
    return VerifyOfflineQRResponse(
        transaction_id=txn.transaction_id,
        status=txn.status.value,
        customer_id=txn.customer_id,
        merchant_id=txn.merchant_id,
        amount=txn.amount,
        nonce=txn.nonce,
        created_at=txn.created_at,
    )
