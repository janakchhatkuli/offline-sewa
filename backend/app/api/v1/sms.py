"""SMS webhook routes (Block 3B).

The shopkeeper app SMSes the QR payload to a Sparrow shortcode; Sparrow
forwards it to this webhook. We parse the body, run the same payment
pipeline as the online verify endpoint, then fire a confirmation SMS
back to the customer's phone (best-effort).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.customer import Customer
from app.schemas.sms import SMSConfirmResponse, SMSInboundPayload
from app.services import qr_service, sms_service
from app.services.qr_service import QRServiceError
from app.services.sms_service import SMSServiceError

router = APIRouter()


def _raise(err: Exception, code: str, status: int) -> None:
    raise HTTPException(
        status_code=status,
        detail={"error": code, "detail": str(err)},
    )


@router.post("/confirm-payment", response_model=SMSConfirmResponse)
async def confirm_payment(
    payload: SMSInboundPayload, db: AsyncSession = Depends(get_db)
) -> SMSConfirmResponse:
    try:
        parsed = sms_service.parse_payment_sms(payload.text)
    except SMSServiceError as e:
        _raise(e, e.code, e.http_status)

    try:
        txn = await qr_service.verify_offline_qr(
            db, merchant_id=parsed.merchant_id, qr_payload=parsed.qr_payload
        )
    except QRServiceError as e:
        _raise(e, e.code, e.http_status)

    customer = await db.get(Customer, txn.customer_id)
    notified = False
    if customer and customer.phone:
        notified = await sms_service.send_sms(
            customer.phone,
            f"Sewa: Rs {txn.amount} paid to merchant {txn.merchant_id}. "
            f"Ref {txn.transaction_id}.",
        )

    return SMSConfirmResponse(
        transaction_id=txn.transaction_id,
        status=txn.status.value,
        customer_id=txn.customer_id,
        merchant_id=txn.merchant_id,
        amount=txn.amount,
        created_at=txn.created_at,
        notified=notified,
    )
