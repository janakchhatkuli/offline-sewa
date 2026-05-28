"""Merchant schemas (Block 3A)."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MerchantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    phone: str = Field(..., min_length=4, max_length=20)


class MerchantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_id: str
    name: str
    phone: str
    pending_settlement: Decimal
    settled_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
