"""Auth schemas: login, token."""
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["customer", "merchant"]


class LoginRequest(BaseModel):
    role: Role
    phone: str = Field(..., min_length=4, max_length=20)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    user_id: str
