"""SMS webhook & settlement schemas (Block 3B)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SMSInboundPayload(BaseModel):
    """Generic inbound SMS webhook body.

    Maps common provider field names (Sparrow uses ``from``/``to``/``text``).
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    sender: str = Field(..., alias="from", min_length=1, max_length=32)
    to: Optional[str] = Field(default=None, max_length=32)
    text: str = Field(..., min_length=1, max_length=2048)
    received_at: Optional[datetime] = None


class SMSConfirmResponse(BaseModel):
    transaction_id: str
    status: str
    customer_id: str
    merchant_id: str
    amount: Decimal
    created_at: datetime
    notified: bool


class SettleResponse(BaseModel):
    merchant_id: str
    settled_count: int
    settled_amount: Decimal
    pending_settlement: Decimal
    settled_balance: Decimal

