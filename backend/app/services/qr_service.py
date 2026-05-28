"""QR creation & verification logic (Block 3A).

QR payload format (compact, signed):

    v1.<base64url(json_body)>.<base64url(hmac_sha256)>

`json_body` fields (canonical key order enforced via sort_keys=True):
    - customer_id: str
    - amount: str (decimal, fixed 2dp)
    - nonce: str (hex)
    - issued_at: int (unix seconds)
    - expires_at: int (unix seconds)

Signature: HMAC-SHA256 over the base64url-encoded body using
`settings.SECRET_KEY`. This lets any verifier (backend) detect tampering of
any field — especially `amount` and `customer_id` — without needing the
customer to be online at the merchant.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.customer import Customer
from app.models.merchant import Merchant
from app.models.nonce import NonceLog
from app.models.transaction import OfflineTransaction, TransactionStatus
from app.utils.nonce import generate_nonce

QR_VERSION = "v1"
QR_TTL_SECONDS = 5 * 60  # 5 minutes


# --------------------------------------------------------------------------- #
# Domain errors
# --------------------------------------------------------------------------- #
class QRServiceError(Exception):
    """Base class for QR service errors."""

    code = "qr_error"
    http_status = 400


class EntityNotFound(QRServiceError):
    code = "not_found"
    http_status = 404


class InactiveAccount(QRServiceError):
    code = "inactive_account"
    http_status = 403


class InvalidAmount(QRServiceError):
    code = "invalid_amount"
    http_status = 422


class InsufficientBalance(QRServiceError):
    code = "insufficient_balance"
    http_status = 409


class MalformedQR(QRServiceError):
    code = "malformed_qr"
    http_status = 400


class InvalidSignature(QRServiceError):
    code = "invalid_signature"
    http_status = 401


class ExpiredQR(QRServiceError):
    code = "expired_qr"
    http_status = 410


class NonceAlreadyUsed(QRServiceError):
    code = "nonce_already_used"
    http_status = 409


# --------------------------------------------------------------------------- #
# Encoding helpers
# --------------------------------------------------------------------------- #
def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def _sign(body_b64: str) -> str:
    sig = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        body_b64.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return _b64url_encode(sig)


def _quantize_amount(amount: Decimal) -> Decimal:
    return Decimal(amount).quantize(Decimal("0.01"))


def _encode_payload(body: dict) -> str:
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    body_b64 = _b64url_encode(raw)
    return f"{QR_VERSION}.{body_b64}.{_sign(body_b64)}"


def _decode_payload(payload: str) -> dict:
    try:
        version, body_b64, sig_b64 = payload.split(".")
    except ValueError as e:
        raise MalformedQR("QR payload structure invalid") from e

    if version != QR_VERSION:
        raise MalformedQR(f"unsupported QR version: {version}")

    expected_sig = _sign(body_b64)
    if not hmac.compare_digest(expected_sig, sig_b64):
        raise InvalidSignature("QR signature mismatch")

    try:
        body = json.loads(_b64url_decode(body_b64))
    except (ValueError, json.JSONDecodeError) as e:
        raise MalformedQR("QR body not decodable") from e

    required = {"customer_id", "amount", "nonce", "issued_at", "expires_at"}
    if not required.issubset(body.keys()):
        raise MalformedQR("QR body missing required fields")
    return body


# --------------------------------------------------------------------------- #
# Service: create
# --------------------------------------------------------------------------- #
async def create_offline_qr(
    db: AsyncSession, customer_id: str, amount: Decimal
) -> dict:
    amount = _quantize_amount(amount)
    if amount <= 0:
        raise InvalidAmount("amount must be greater than zero")

    customer = await db.get(Customer, customer_id)
    if customer is None:
        raise EntityNotFound("customer not found")
    if not customer.is_active:
        raise InactiveAccount("customer account is inactive")

    if Decimal(customer.offline_balance) < amount:
        raise InsufficientBalance("offline balance is insufficient")

    nonce = generate_nonce()
    issued = datetime.now(timezone.utc)
    issued_ts = int(issued.timestamp())
    expires_ts = issued_ts + QR_TTL_SECONDS

    body = {
        "customer_id": customer.customer_id,
        "amount": f"{amount:.2f}",
        "nonce": nonce,
        "issued_at": issued_ts,
        "expires_at": expires_ts,
    }
    qr_payload = _encode_payload(body)

    return {
        "qr_payload": qr_payload,
        "nonce": nonce,
        "customer_id": customer.customer_id,
        "amount": amount,
        "issued_at": datetime.fromtimestamp(issued_ts, tz=timezone.utc),
        "expires_at": datetime.fromtimestamp(expires_ts, tz=timezone.utc),
    }


# --------------------------------------------------------------------------- #
# Service: verify
# --------------------------------------------------------------------------- #
async def verify_offline_qr(
    db: AsyncSession, merchant_id: str, qr_payload: str
) -> OfflineTransaction:
    body = _decode_payload(qr_payload)

    now_ts = int(datetime.now(timezone.utc).timestamp())
    if now_ts > int(body["expires_at"]):
        raise ExpiredQR("QR has expired")

    try:
        amount = _quantize_amount(Decimal(str(body["amount"])))
    except (ValueError, ArithmeticError) as e:
        raise MalformedQR("QR amount invalid") from e
    if amount <= 0:
        raise InvalidAmount("amount must be greater than zero")

    customer_id = str(body["customer_id"])
    nonce = str(body["nonce"])

    merchant = await db.get(Merchant, merchant_id)
    if merchant is None:
        raise EntityNotFound("merchant not found")
    if not merchant.is_active:
        raise InactiveAccount("merchant account is inactive")

    customer = await db.get(Customer, customer_id)
    if customer is None:
        raise EntityNotFound("customer not found")
    if not customer.is_active:
        raise InactiveAccount("customer account is inactive")

    # Replay check
    existing = await db.execute(select(NonceLog).where(NonceLog.nonce == nonce))
    if existing.scalar_one_or_none() is not None:
        raise NonceAlreadyUsed("nonce has already been used")

    if Decimal(customer.offline_balance) < amount:
        raise InsufficientBalance("offline balance is insufficient")

    # Atomic updates
    customer.offline_balance = Decimal(customer.offline_balance) - amount
    merchant.pending_settlement = Decimal(merchant.pending_settlement) + amount

    txn = OfflineTransaction(
        customer_id=customer.customer_id,
        merchant_id=merchant.merchant_id,
        amount=amount,
        nonce=nonce,
        status=TransactionStatus.pending_settlement,
    )
    db.add(txn)
    db.add(NonceLog(nonce=nonce, customer_id=customer.customer_id, status="used"))

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        # Unique constraint on nonce_log.nonce or offline_transactions.nonce
        raise NonceAlreadyUsed("nonce has already been used") from e

    await db.refresh(txn)
    return txn
