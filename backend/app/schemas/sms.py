"""SMS payload schemas (Block 3B)."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SMSWebhookRequest(BaseModel):
    """Inbound SMS payload as posted by the SMS provider (e.g. Sparrow).

    The merchant forwards the customer's QR string to a short-code; the
    provider then POSTs the message body here.
    """

    from_: str = Field(..., alias="from", min_length=4, max_length=20)
    text: str = Field(..., min_length=1, max_length=2048)
    message_id: str | None = Field(default=None, max_length=128)

    model_config = ConfigDict(populate_by_name=True)


class SMSWebhookResponse(BaseModel):
    transaction_id: str
    status: str
    customer_id: str
    merchant_id: str
    amount: Decimal
    nonce: str
    created_at: datetime
    sms_sent: bool


class SettleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_id: str
    settled_count: int
    settled_amount: Decimal
    pending_settlement: Decimal
    settled_balance: Decimal
    settled_at: datetime

