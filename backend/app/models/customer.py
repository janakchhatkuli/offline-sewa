import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _new_id() -> str:
	return "cust_" + uuid.uuid4().hex[:8]


class Customer(Base):
	__tablename__ = "customers"

	customer_id: Mapped[str] = mapped_column(String, primary_key=True, default=_new_id)
	name: Mapped[str] = mapped_column(String(120), nullable=False)
	phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
	online_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
	offline_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
	)

	def __repr__(self) -> str:
		return f"<Customer id={self.customer_id} phone={self.phone}>"
