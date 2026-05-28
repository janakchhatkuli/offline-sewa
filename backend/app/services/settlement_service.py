"""Merchant settlement (Block 3B).

Moves a merchant's ``pending_settlement`` balance into ``settled_balance``
and flips all related ``offline_transactions`` rows to ``settled``. The
operation is atomic — either every row updates or none does.
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

    pending_rows = (
        await db.execute(
            select(OfflineTransaction).where(
                OfflineTransaction.merchant_id == merchant_id,
                OfflineTransaction.status == TransactionStatus.pending_settlement,
            )
        )
    ).scalars().all()

    if not pending_rows:
        raise NothingToSettle("no pending transactions to settle")

    now = datetime.now(timezone.utc)
    total = Decimal("0.00")
    for txn in pending_rows:
        txn.status = TransactionStatus.settled
        txn.settled_at = now
        total += Decimal(txn.amount)

    merchant.pending_settlement = Decimal(merchant.pending_settlement) - total
    if merchant.pending_settlement < 0:
        merchant.pending_settlement = Decimal("0.00")
    merchant.settled_balance = Decimal(merchant.settled_balance) + total

    await db.commit()
    await db.refresh(merchant)

    return {
        "merchant_id": merchant.merchant_id,
        "settled_count": len(pending_rows),
        "settled_amount": total,
        "pending_settlement": merchant.pending_settlement,
        "settled_balance": merchant.settled_balance,
        "settled_at": now,
    }

