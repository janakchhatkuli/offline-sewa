"""SMS webhook routes (Block 3B)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.merchant import Merchant
from app.schemas.sms import SMSWebhookRequest, SMSWebhookResponse
from app.services import qr_service, sms_service
from app.services.qr_service import QRServiceError
from app.services.sms_service import SMSParseError

router = APIRouter()


@router.post("/confirm-payment", response_model=SMSWebhookResponse)
async def confirm_payment(
    payload: SMSWebhookRequest,
    db: AsyncSession = Depends(get_db),
) -> SMSWebhookResponse:
    # 1. Identify merchant by sender phone.
    merchant = (
        await db.execute(select(Merchant).where(Merchant.phone == payload.from_))
    ).scalar_one_or_none()
    if merchant is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "merchant_not_found", "detail": "unknown sender phone"},
        )

    # 2. Extract the QR payload from the SMS body.
    try:
        qr_payload = sms_service.extract_qr_payload(payload.text)
    except SMSParseError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "malformed_sms", "detail": str(e)},
        )

    # 3. Run the same verification path as the online endpoint.
    try:
        txn = await qr_service.verify_offline_qr(
            db, merchant_id=merchant.merchant_id, qr_payload=qr_payload
        )
    except QRServiceError as e:
        raise HTTPException(
            status_code=e.http_status,
            detail={"error": e.code, "detail": str(e)},
        )

    # 4. Best-effort confirmation SMS back to the merchant.
    sms_sent = await sms_service.send_sms(
        to=merchant.phone,
        message=sms_service.format_confirmation(
            transaction_id=txn.transaction_id,
            amount=txn.amount,
            merchant_name=merchant.name,
        ),
    )

    return SMSWebhookResponse(
        transaction_id=txn.transaction_id,
        status=txn.status.value,
        customer_id=txn.customer_id,
        merchant_id=txn.merchant_id,
        amount=txn.amount,
        nonce=txn.nonce,
        created_at=txn.created_at,
        sms_sent=sms_sent,
    )
