"""Customer schemas (Block 3A)."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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
    online_balance: Decimal
    offline_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
