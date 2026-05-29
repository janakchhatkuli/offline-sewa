"""Merchant settlement logic (Block 3B).

Moves a merchant's accumulated ``pending_settlement`` into
``settled_balance`` and flips the related offline transactions to
``settled``. Runs in a single transaction so the books always balance.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant import Merchant
from app.models.transaction import OfflineTransaction, TransactionStatus


class SettlementError(Exception):
    code = "settlement_error"
    http_status = 400


class MerchantNotFound(SettlementError):
    code = "not_found"
    http_status = 404


class NothingToSettle(SettlementError):
    code = "nothing_to_settle"
    http_status = 409


async def settle_merchant(db: AsyncSession, merchant_id: str) -> dict:
    merchant = await db.get(Merchant, merchant_id)
    if merchant is None:
        raise MerchantNotFound("merchant not found")

    result = await db.execute(
        select(OfflineTransaction).where(
            OfflineTransaction.merchant_id == merchant_id,
            OfflineTransaction.status == TransactionStatus.pending_settlement,
        )
    )
    pending = list(result.scalars().all())
    if not pending:
        raise NothingToSettle("no pending transactions to settle")

    now = datetime.now(timezone.utc)
    total = Decimal("0.00")
    for txn in pending:
        total += Decimal(txn.amount)
        txn.status = TransactionStatus.settled
        txn.settled_at = now

    pending_before = Decimal(merchant.pending_settlement)
    move = min(pending_before, total)
    merchant.pending_settlement = pending_before - move
    merchant.settled_balance = Decimal(merchant.settled_balance) + move

    await db.commit()
    await db.refresh(merchant)

    return {
        "merchant_id": merchant.merchant_id,
        "settled_count": len(pending),
        "settled_amount": total,
        "pending_settlement": Decimal(merchant.pending_settlement),
        "settled_balance": Decimal(merchant.settled_balance),
    }

