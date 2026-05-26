import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TransactionStatus(str, enum.Enum):
	pending_settlement = "pending_settlement"
	settled = "settled"
	failed = "failed"


def _new_txn_id() -> str:
	return "TXN" + uuid.uuid4().hex[:8].upper()


class OfflineTransaction(Base):
	__tablename__ = "offline_transactions"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	transaction_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, default=_new_txn_id, index=True)
	customer_id: Mapped[str] = mapped_column(
		String, ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False, index=True
	)
	merchant_id: Mapped[str] = mapped_column(
		String, ForeignKey("merchants.merchant_id", ondelete="RESTRICT"), nullable=False, index=True
	)
	amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
	nonce: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
	status: Mapped[TransactionStatus] = mapped_column(
		Enum(TransactionStatus), default=TransactionStatus.pending_settlement, nullable=False
	)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
	)

	# relationships (lazy loaded — avoids N+1 by default)
	customer: Mapped["Customer"] = relationship("Customer", lazy="select")  # noqa: F821
	merchant: Mapped["Merchant"] = relationship("Merchant", lazy="select")  # noqa: F821

	def __repr__(self) -> str:
		return f"<OfflineTransaction {self.transaction_id} {self.status} ₹{self.amount}>"
