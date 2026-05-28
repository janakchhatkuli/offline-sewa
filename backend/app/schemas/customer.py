"""Customer schemas (Block 3A)."""
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Gender = Literal["male", "female", "other"]


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    phone: str = Field(..., min_length=4, max_length=20)
    online_balance: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2)
    offline_balance: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2)


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    name: str
    phone: str
    address: str | None = None
    dob: date | None = None
    gender: str | None = None
    online_balance: Decimal
    offline_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CustomerRegister(BaseModel):
    """Registration payload for a new customer account."""

    name: str = Field(..., min_length=1, max_length=120)
    phone: str = Field(..., min_length=4, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    address: str = Field(..., min_length=1, max_length=255)
    dob: date
    gender: Gender

