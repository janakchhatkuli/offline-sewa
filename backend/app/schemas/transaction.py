"""Transaction & QR schemas (Block 3A)."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CreateOfflineQRRequest(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=64)
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)


class CreateOfflineQRResponse(BaseModel):
    qr_payload: str
    nonce: str
    customer_id: str
    amount: Decimal
    issued_at: datetime
    expires_at: datetime


class VerifyOfflineQRRequest(BaseModel):
    merchant_id: str = Field(..., min_length=1, max_length=64)
    qr_payload: str = Field(..., min_length=1)


class VerifyOfflineQRResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    status: str
    customer_id: str
    merchant_id: str
    amount: Decimal
    nonce: str
    created_at: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
