from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NonceLog(Base):
	"""
	Every nonce that has been spent is recorded here.
	Before processing any payment, the backend checks this table first
	to prevent double-spend attacks.
	"""

	__tablename__ = "nonce_log"

	nonce: Mapped[str] = mapped_column(String(64), primary_key=True)
	customer_id: Mapped[str] = mapped_column(
		String, ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False, index=True
	)
	used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	status: Mapped[str] = mapped_column(String(20), default="used", nullable=False)

	def __repr__(self) -> str:
		return f"<NonceLog nonce={self.nonce[:12]} customer={self.customer_id}>"
