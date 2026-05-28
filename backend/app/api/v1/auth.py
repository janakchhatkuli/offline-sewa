"""Authentication routes: register customer/merchant, login, me."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.customer import Customer
from app.models.merchant import Merchant
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.customer import CustomerRead, CustomerRegister
from app.schemas.merchant import MerchantRead, MerchantRegister

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def _conflict(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"error": "phone_exists", "detail": detail},
    )


def _unauthorized(detail: str = "invalid credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": "unauthorized", "detail": detail},
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/customer/register", response_model=TokenResponse, status_code=201)
async def register_customer(
    payload: CustomerRegister, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    existing = await db.execute(select(Customer).where(Customer.phone == payload.phone))
    if existing.scalar_one_or_none() is not None:
        raise _conflict("customer with this phone already exists")

    customer = Customer(
        name=payload.name,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        address=payload.address,
        dob=payload.dob,
        gender=payload.gender,
    )
    db.add(customer)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise _conflict("customer with this phone already exists")
    await db.refresh(customer)

    token = create_access_token(subject=customer.customer_id, role="customer")
    return TokenResponse(access_token=token, role="customer", user_id=customer.customer_id)


@router.post("/merchant/register", response_model=TokenResponse, status_code=201)
async def register_merchant(
    payload: MerchantRegister, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    existing = await db.execute(select(Merchant).where(Merchant.phone == payload.phone))
    if existing.scalar_one_or_none() is not None:
        raise _conflict("merchant with this phone already exists")

    merchant = Merchant(
        name=payload.name,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        business_name=payload.business_name,
        business_address=payload.business_address,
        business_phone=payload.business_phone,
        business_type=payload.business_type,
        pan_number=payload.pan_number,
    )
    db.add(merchant)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise _conflict("merchant with this phone already exists")
    await db.refresh(merchant)

    token = create_access_token(subject=merchant.merchant_id, role="merchant")
    return TokenResponse(access_token=token, role="merchant", user_id=merchant.merchant_id)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    if payload.role == "customer":
        result = await db.execute(select(Customer).where(Customer.phone == payload.phone))
        user = result.scalar_one_or_none()
        if user is None or not user.password_hash or not verify_password(
            payload.password, user.password_hash
        ):
            raise _unauthorized()
        if not user.is_active:
            raise _unauthorized("account disabled")
        token = create_access_token(subject=user.customer_id, role="customer")
        return TokenResponse(access_token=token, role="customer", user_id=user.customer_id)

    result = await db.execute(select(Merchant).where(Merchant.phone == payload.phone))
    user = result.scalar_one_or_none()
    if user is None or not user.password_hash or not verify_password(
        payload.password, user.password_hash
    ):
        raise _unauthorized()
    if not user.is_active:
        raise _unauthorized("account disabled")
    token = create_access_token(subject=user.merchant_id, role="merchant")
    return TokenResponse(access_token=token, role="merchant", user_id=user.merchant_id)


async def get_current_principal(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> tuple[str, Customer | Merchant]:
    """Return (role, user) for the bearer token, or raise 401."""
    if not token:
        raise _unauthorized("missing token")
    payload = decode_token(token)
    if not payload:
        raise _unauthorized("invalid or expired token")
    sub = payload.get("sub")
    role = payload.get("role")
    if not sub or role not in ("customer", "merchant"):
        raise _unauthorized("invalid token claims")

    if role == "customer":
        user = await db.get(Customer, sub)
    else:
        user = await db.get(Merchant, sub)
    if user is None or not user.is_active:
        raise _unauthorized("user not found")
    return role, user


def require_role(*allowed: str):
    """Dependency factory that enforces the principal's role."""

    async def _dep(principal=Depends(get_current_principal)):
        role, user = principal
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "forbidden", "detail": f"role '{role}' not allowed"},
            )
        return user

    return _dep


@router.get("/me")
async def me(principal=Depends(get_current_principal)):
    role, user = principal
    if role == "customer":
        return {"role": role, "user": CustomerRead.model_validate(user)}
    return {"role": role, "user": MerchantRead.model_validate(user)}
