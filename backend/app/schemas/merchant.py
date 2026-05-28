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
    business_name: str | None = None
    business_address: str | None = None
    business_phone: str | None = None
    business_type: str | None = None
    pan_number: str | None = None
    pending_settlement: Decimal
    settled_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MerchantRegister(BaseModel):
    """Registration payload for a new merchant account."""

    name: str = Field(..., min_length=1, max_length=120, description="Full name of owner")
    phone: str = Field(..., min_length=4, max_length=20, description="Owner contact phone")
    password: str = Field(..., min_length=6, max_length=128)
    business_name: str = Field(..., min_length=1, max_length=150)
    business_address: str = Field(..., min_length=1, max_length=255)
    business_phone: str | None = Field(default=None, max_length=20)
    business_type: str | None = Field(default=None, max_length=80)
    pan_number: str | None = Field(default=None, max_length=50)

